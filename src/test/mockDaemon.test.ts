import * as assert from "assert";
import * as http from "node:http";
import { AddressInfo } from "node:net";
import { WebSocketServer } from "ws";
import { AppLabClient, ApiError } from "../appLabClient";

/**
 * Spins up a tiny HTTP + SSE + WebSocket server that mimics the arduino-app-cli
 * daemon, and drives the AppLabClient against it. Validates request<T>, SSE
 * dispatch + mid-stream abort, and the WebSocket monitor — the transport paths
 * the pure SSE-parser test cannot cover.
 */
suite("AppLabClient against a mock daemon", () => {
  let server: http.Server;
  let wss: WebSocketServer;
  let base: string;

  suiteSetup(async () => {
    server = http.createServer((req, res) => {
      const url = req.url ?? "";
      if (url === "/v1/version") {
        res.setHeader("content-type", "application/json");
        res.end(JSON.stringify({ version: "9.9.9" }));
        return;
      }
      if (url === "/v1/apps/a1/start") {
        res.setHeader("content-type", "text/event-stream");
        res.write("event: progress\ndata: {\"name\":\"flash\",\"progress\":0.5}\n\n");
        res.write("event: message\ndata: {\"message\":\"done\"}\n\n");
        res.end();
        return;
      }
      if (url === "/v1/apps/events" || url === "/v1/forever") {
        // Never completes — used to test abort.
        res.setHeader("content-type", "text/event-stream");
        res.write(": hello\n\n");
        return;
      }
      if (url.startsWith("/v1/apps")) {
        res.setHeader("content-type", "application/json");
        res.end(JSON.stringify({ apps: [{ id: "a1", name: "Demo", status: "stopped" }] }));
        return;
      }
      if (url === "/v1/system/resources") {
        res.statusCode = 500;
        res.end(JSON.stringify({ message: "kaboom" }));
        return;
      }
      res.statusCode = 404;
      res.end();
    });

    wss = new WebSocketServer({ server, path: "/v1/monitor/ws" });
    wss.on("connection", (sock) => {
      sock.on("message", (data) => sock.send(data)); // echo
    });

    await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
    const port = (server.address() as AddressInfo).port;
    base = `http://127.0.0.1:${port}`;
  });

  suiteTeardown(async () => {
    wss.close();
    await new Promise<void>((resolve) => server.close(() => resolve()));
  });

  test("request<T> parses JSON for version()", async () => {
    const client = new AppLabClient({ baseUrl: base });
    const v = await client.version();
    assert.strictEqual(v.version, "9.9.9");
  });

  test("listApps returns the apps array", async () => {
    const client = new AppLabClient({ baseUrl: base });
    const res = await client.listApps();
    assert.strictEqual(res.apps.length, 1);
    assert.strictEqual(res.apps[0].id, "a1");
  });

  test("non-ok responses throw ApiError with the daemon message", async () => {
    const client = new AppLabClient({ baseUrl: base });
    await assert.rejects(
      () => client.resources(),
      (err: unknown) => err instanceof ApiError && err.status === 500 && /kaboom/.test(err.message),
    );
  });

  test("startApp dispatches SSE progress + message events", async () => {
    const client = new AppLabClient({ baseUrl: base });
    const progress: number[] = [];
    const messages: string[] = [];
    await client.startApp("a1", {
      onProgress: (p) => progress.push(p.progress),
      onMessage: (m) => messages.push(m.message),
    });
    assert.deepStrictEqual(progress, [0.5]);
    assert.deepStrictEqual(messages, ["done"]);
  });

  test("aborting an SSE stream resolves cleanly (no throw)", async () => {
    const client = new AppLabClient({ baseUrl: base });
    const ctrl = new AbortController();
    const p = client.appStatusEvents(() => {}, ctrl.signal);
    setTimeout(() => ctrl.abort(), 50);
    await assert.doesNotReject(() => p);
  });

  test("openMonitor echoes data over the WebSocket", async () => {
    const client = new AppLabClient({ baseUrl: base });
    const sock = client.openMonitor();
    const got = await new Promise<string>((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("timeout")), 2000);
      sock.on("open", () => sock.send("ping"));
      sock.on("data", (chunk) => {
        clearTimeout(timer);
        resolve(chunk.toString());
      });
      sock.on("error", reject);
    });
    sock.close();
    assert.strictEqual(got, "ping");
  });
});
