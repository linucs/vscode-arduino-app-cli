import { spawn } from "node:child_process";
import * as fs from "node:fs";
import WebSocket from "ws";
import { SseFrameParser, decodeSseEvent } from "./sseParser";
import type {
  AppInfo,
  AppListResponse,
  BrickInfo,
  BrickInstance,
  ExposedPort,
  LibraryInfo,
  ModelInfo,
  ResourcesResponse,
  SketchLibrary,
  SseError,
  SseEvent,
  SseMessage,
  SseProgress,
  VersionResponse,
} from "./api/types";

/** Error carrying the HTTP status of a failed daemon request. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Sinks for an SSE stream; only the relevant callbacks need be supplied. */
export interface SseSinks {
  onProgress?: (p: SseProgress) => void;
  onMessage?: (m: SseMessage) => void;
  onApp?: (a: AppInfo) => void;
  onError?: (e: SseError) => void;
  onRaw?: (e: SseEvent) => void;
}

/** A live serial-monitor connection, shaped like the sibling's MonitorStream. */
export interface MonitorSocket {
  send(data: string | Buffer): void;
  close(): void;
  on(event: "data", cb: (chunk: Buffer) => void): void;
  on(event: "error", cb: (err: Error) => void): void;
  on(event: "close", cb: () => void): void;
  on(event: "open", cb: () => void): void;
}

type Query = Record<string, string | number | boolean | undefined>;

export interface ClientOptions {
  baseUrl: string;
  apiKey?: string;
  cliPath?: string;
  log?: (msg: string) => void;
}

/**
 * Thin wrapper over the arduino-app-cli daemon. REST for unary operations, SSE
 * for streaming (start/stop/logs/status/update), WebSocket for the serial
 * monitor, plus a one-shot CLI exec helper for the handful of commands the
 * daemon does not expose over REST.
 *
 * Transport-only: no VS Code dependency, so it can be exercised against a mock
 * daemon in unit tests.
 */
export class AppLabClient {
  private base: string;
  private apiKey?: string;
  private cliPath: string;
  private log?: (msg: string) => void;

  constructor(opts: ClientOptions) {
    this.base = opts.baseUrl.replace(/\/$/, "");
    this.apiKey = opts.apiKey || undefined;
    this.cliPath = opts.cliPath || "arduino-app-cli";
    this.log = opts.log;
  }

  private headers(extra?: Record<string, string>): Record<string, string> {
    const h: Record<string, string> = { "Content-Type": "application/json", ...extra };
    if (this.apiKey) {
      h["X-API-Key"] = this.apiKey;
    }
    return h;
  }

  private url(path: string, query?: Query): string {
    const qs = query
      ? Object.entries(query)
          .filter(([, v]) => v !== undefined)
          .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
          .join("&")
      : "";
    return `${this.base}/v1${path}${qs ? `?${qs}` : ""}`;
  }

  // ---- Unary JSON ----

  private async request<T>(
    method: string,
    path: string,
    opts: { body?: unknown; query?: Query; headers?: Record<string, string>; signal?: AbortSignal } = {},
  ): Promise<T> {
    const url = this.url(path, opts.query);
    this.log?.(`[http] ${method} ${url}`);
    const res = await fetch(url, {
      method,
      signal: opts.signal,
      headers: this.headers(opts.headers),
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    });
    if (!res.ok) {
      throw new ApiError(res.status, await safeError(res));
    }
    if (res.status === 204 || res.headers.get("content-length") === "0") {
      return undefined as T;
    }
    const text = await res.text();
    return (text ? JSON.parse(text) : undefined) as T;
  }

  // ---- SSE streaming ----

  private async sseStream(
    method: string,
    path: string,
    sinks: SseSinks,
    opts: { body?: unknown; query?: Query; signal?: AbortSignal } = {},
  ): Promise<void> {
    const url = this.url(path, opts.query);
    this.log?.(`[sse] ${method} ${url}`);
    const res = await fetch(url, {
      method,
      signal: opts.signal,
      headers: this.headers({ Accept: "text/event-stream" }),
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    });
    if (!res.ok) {
      throw new ApiError(res.status, await safeError(res));
    }
    const body = res.body;
    if (!body) {
      return;
    }
    const reader = body.getReader();
    const decoder = new TextDecoder();
    const parser = new SseFrameParser();
    const dispatch = (raw: { event: string; data: string; id?: string }) => {
      const ev = decodeSseEvent(raw);
      sinks.onRaw?.(ev);
      switch (ev.event) {
        case "progress":
          sinks.onProgress?.(ev.data as SseProgress);
          break;
        case "message":
          sinks.onMessage?.(ev.data as SseMessage);
          break;
        case "app":
          sinks.onApp?.(ev.data as AppInfo);
          break;
        case "error":
          sinks.onError?.(ev.data as SseError);
          break;
      }
    };
    try {
      for (;;) {
        const { value, done } = await reader.read();
        if (done) {
          for (const f of parser.flush()) {
            dispatch(f);
          }
          break;
        }
        for (const f of parser.push(decoder.decode(value, { stream: true }))) {
          dispatch(f);
        }
      }
    } catch (err) {
      // A user-initiated abort closes the stream cleanly.
      if (isAbortError(err)) {
        return;
      }
      throw err;
    }
  }

  // ---- One-shot CLI exec (for REST-less commands) ----

  /**
   * Run `arduino-app-cli <args>` once and return stdout. Used for commands the
   * daemon does not expose over REST (clean-cache, system init/cleanup/
   * network-mode/keyboard/set-name).
   */
  cli(args: string[], opts: { json?: boolean; signal?: AbortSignal } = {}): Promise<string> {
    const finalArgs = opts.json ? [...args, "--format", "json"] : args;
    this.log?.(`[cli] ${this.cliPath} ${finalArgs.join(" ")}`);
    return new Promise<string>((resolve, reject) => {
      const proc = spawn(this.cliPath, finalArgs, { stdio: ["ignore", "pipe", "pipe"] });
      let out = "";
      let err = "";
      opts.signal?.addEventListener("abort", () => proc.kill(), { once: true });
      proc.stdout.on("data", (c: Buffer) => (out += c.toString()));
      proc.stderr.on("data", (c: Buffer) => (err += c.toString()));
      proc.on("error", (e: NodeJS.ErrnoException) =>
        reject(
          e.code === "ENOENT"
            ? new Error(`arduino-app-cli not found at "${this.cliPath}". Set "appLab.cliPath".`)
            : e,
        ),
      );
      proc.on("close", (code) =>
        code === 0 ? resolve(out) : reject(new Error(err.trim() || `exited with code ${code}`)),
      );
    });
  }

  // ---- Lifecycle / probe ----

  version(signal?: AbortSignal): Promise<VersionResponse> {
    return this.request("GET", "/version", { signal });
  }

  // ---- Apps ----

  listApps(query?: { filter?: string; status?: string }): Promise<AppListResponse> {
    return this.request("GET", "/apps", { query });
  }
  createApp(body: { name: string; description?: string; icon?: string; from_app?: string; bricks?: string[]; no_sketch?: boolean }): Promise<AppInfo> {
    return this.request("POST", "/apps", { body });
  }
  getApp(id: string): Promise<AppInfo> {
    return this.request("GET", `/apps/${encodeURIComponent(id)}`);
  }
  patchApp(id: string, body: Partial<Pick<AppInfo, "name" | "description" | "icon" | "default">>): Promise<AppInfo> {
    return this.request("PATCH", `/apps/${encodeURIComponent(id)}`, { body });
  }
  deleteApp(id: string): Promise<void> {
    return this.request("DELETE", `/apps/${encodeURIComponent(id)}`);
  }
  startApp(id: string, sinks: SseSinks, opts: { verbose?: boolean; signal?: AbortSignal } = {}): Promise<void> {
    return this.sseStream("POST", `/apps/${encodeURIComponent(id)}/start`, sinks, {
      query: { verbose: opts.verbose },
      signal: opts.signal,
    });
  }
  stopApp(id: string, sinks: SseSinks, signal?: AbortSignal): Promise<void> {
    return this.sseStream("POST", `/apps/${encodeURIComponent(id)}/stop`, sinks, { signal });
  }
  appLogs(
    id: string,
    sinks: SseSinks,
    opts: { filter?: string; tail?: number; nofollow?: boolean; signal?: AbortSignal } = {},
  ): Promise<void> {
    return this.sseStream("GET", `/apps/${encodeURIComponent(id)}/logs`, sinks, {
      query: { filter: opts.filter, tail: opts.tail, nofollow: opts.nofollow },
      signal: opts.signal,
    });
  }
  appStatusEvents(onApp: (a: AppInfo) => void, signal?: AbortSignal): Promise<void> {
    return this.sseStream("GET", "/apps/events", { onApp }, { signal });
  }
  exposedPorts(id: string): Promise<ExposedPort[]> {
    return this.request("GET", `/apps/${encodeURIComponent(id)}/exposed-ports`);
  }
  cloneApp(id: string, body?: { name?: string; icon?: string }): Promise<AppInfo> {
    return this.request("POST", `/apps/${encodeURIComponent(id)}/clone`, { body: body ?? {} });
  }

  /** Download an app export zip to `destPath`. */
  async exportApp(id: string, destPath: string, opts: { includeData?: boolean } = {}): Promise<void> {
    const res = await fetch(this.url(`/apps/${encodeURIComponent(id)}/export`, { include_data: opts.includeData }), {
      headers: this.headers(),
    });
    if (!res.ok) {
      throw new ApiError(res.status, await safeError(res));
    }
    const buf = Buffer.from(await res.arrayBuffer());
    await fs.promises.writeFile(destPath, buf);
  }

  /** Upload a zip to import an app. */
  async importApp(zipPath: string): Promise<AppInfo> {
    const buf = await fs.promises.readFile(zipPath);
    const res = await fetch(this.url("/apps/import"), {
      method: "POST",
      headers: this.headers({ "Content-Type": "application/zip" }),
      body: new Uint8Array(buf),
    });
    if (!res.ok) {
      throw new ApiError(res.status, await safeError(res));
    }
    return (await res.json()) as AppInfo;
  }

  // ---- Bricks ----

  async listBricks(): Promise<BrickInfo[]> {
    const res = await this.request<{ bricks?: BrickInfo[] }>("GET", "/bricks");
    return res.bricks ?? [];
  }
  getBrick(id: string): Promise<BrickInfo> {
    return this.request("GET", `/bricks/${encodeURIComponent(id)}`);
  }
  async listAppBricks(appId: string): Promise<BrickInstance[]> {
    const res = await this.request<{ bricks?: BrickInstance[] }>(
      "GET",
      `/apps/${encodeURIComponent(appId)}/bricks`,
    );
    return res.bricks ?? [];
  }
  addAppBrick(appId: string, brickId: string, config?: Record<string, string>): Promise<BrickInstance> {
    return this.request("PUT", `/apps/${encodeURIComponent(appId)}/bricks/${encodeURIComponent(brickId)}`, {
      body: config ? { variables: config } : {},
    });
  }
  patchAppBrick(appId: string, brickId: string, config: Record<string, string>): Promise<BrickInstance> {
    return this.request("PATCH", `/apps/${encodeURIComponent(appId)}/bricks/${encodeURIComponent(brickId)}`, {
      body: { variables: config },
    });
  }
  deleteAppBrick(appId: string, brickId: string): Promise<void> {
    return this.request("DELETE", `/apps/${encodeURIComponent(appId)}/bricks/${encodeURIComponent(brickId)}`);
  }
  renameAppBrick(appId: string, brickId: string, name: string): Promise<BrickInstance> {
    return this.request("POST", `/apps/${encodeURIComponent(appId)}/bricks/${encodeURIComponent(brickId)}/rename`, {
      body: { name },
    });
  }

  // ---- Models ----

  async listModels(query?: { bricks?: string }): Promise<ModelInfo[]> {
    const res = await this.request<{ models?: ModelInfo[] }>("GET", "/models", { query });
    return res.models ?? [];
  }
  getModel(id: string): Promise<ModelInfo> {
    return this.request("GET", `/models/${encodeURIComponent(id)}`);
  }
  installEiModel(projectId: string, body?: Record<string, unknown>): Promise<ModelInfo> {
    return this.request("PUT", `/models/ei/projects/${encodeURIComponent(projectId)}`, { body: body ?? {} });
  }
  deleteModel(id: string): Promise<void> {
    return this.request("DELETE", `/models/${encodeURIComponent(id)}`);
  }

  // ---- Sketch / MCU C++ libraries ----

  async listLibraries(query?: { search?: string; page?: number; limit?: number }): Promise<LibraryInfo[]> {
    const res = await this.request<{ libraries?: LibraryInfo[] }>("GET", "/libraries", { query });
    return res.libraries ?? [];
  }
  async getSketchLibs(appId: string): Promise<SketchLibrary[]> {
    // The daemon returns `{ libraries: ["Name", "Name@1.2.3", …] }` (plain strings).
    const res = await this.request<{ libraries?: string[] }>(
      "GET",
      `/apps/${encodeURIComponent(appId)}/sketch/libraries`,
    );
    return (res.libraries ?? []).map(parseLibraryRef);
  }
  addSketchLib(appId: string, ref: string, opts: { addDeps?: boolean } = {}): Promise<SketchLibrary[]> {
    return this.request("PUT", `/apps/${encodeURIComponent(appId)}/sketch/libraries/${encodeURIComponent(ref)}`, {
      query: { add_deps: opts.addDeps },
    });
  }
  removeSketchLib(appId: string, ref: string, opts: { removeDeps?: boolean } = {}): Promise<void> {
    return this.request("DELETE", `/apps/${encodeURIComponent(appId)}/sketch/libraries/${encodeURIComponent(ref)}`, {
      query: { remove_deps: opts.removeDeps },
    });
  }

  // ---- System / config / properties ----

  getConfig(): Promise<unknown> {
    return this.request("GET", "/config");
  }
  listProperties(): Promise<string[]> {
    return this.request("GET", "/properties");
  }
  getProperty(key: string): Promise<unknown> {
    return this.request("GET", `/properties/${encodeURIComponent(key)}`);
  }
  putProperty(key: string, value: unknown): Promise<void> {
    return this.request("PUT", `/properties/${encodeURIComponent(key)}`, { body: { value } });
  }
  deleteProperty(key: string): Promise<void> {
    return this.request("DELETE", `/properties/${encodeURIComponent(key)}`);
  }
  checkUpdate(): Promise<unknown> {
    return this.request("GET", "/system/update/check");
  }
  applyUpdate(): Promise<void> {
    return this.request("PUT", "/system/update/apply");
  }
  updateEvents(sinks: SseSinks, signal?: AbortSignal): Promise<void> {
    return this.sseStream("GET", "/system/update/events", sinks, { signal });
  }
  resources(): Promise<ResourcesResponse> {
    return this.request("GET", "/system/resources");
  }

  // ---- Serial monitor (WebSocket) ----

  /**
   * Open a serial-monitor WebSocket. Prefers the per-app route (which App Lab
   * uses); the caller passes the app id, falling back to the global monitor when
   * none is given.
   */
  openMonitor(appId?: string): MonitorSocket {
    const wsBase = this.base.replace(/^http/, "ws");
    const path = appId ? `/v1/apps/${encodeURIComponent(appId)}/serial-monitor` : "/v1/monitor/ws";
    const headers: Record<string, string> = {};
    if (this.apiKey) {
      headers["X-API-Key"] = this.apiKey;
    }
    this.log?.(`[ws] ${wsBase}${path}`);
    const sock = new WebSocket(`${wsBase}${path}`, { headers });
    return {
      send: (data) => sock.send(data),
      close: () => sock.close(),
      on: (event: string, cb: (...a: never[]) => void) => {
        if (event === "data") {
          sock.on("message", (d: WebSocket.RawData) => cb(toBuffer(d) as never));
        } else {
          sock.on(event, cb as (...a: unknown[]) => void);
        }
      },
    } as MonitorSocket;
  }
}

/** Split a `"Name"` / `"Name@version"` library reference into parts. */
function parseLibraryRef(ref: string): SketchLibrary {
  const at = ref.lastIndexOf("@");
  return at > 0 ? { name: ref.slice(0, at), version: ref.slice(at + 1) } : { name: ref };
}

function toBuffer(d: WebSocket.RawData): Buffer {
  if (Buffer.isBuffer(d)) {
    return d;
  }
  if (Array.isArray(d)) {
    return Buffer.concat(d);
  }
  return Buffer.from(d as ArrayBuffer);
}

function isAbortError(err: unknown): boolean {
  return err instanceof Error && (err.name === "AbortError" || err.name === "DOMException");
}

async function safeError(res: Response): Promise<string> {
  try {
    const text = await res.text();
    if (!text) {
      return `HTTP ${res.status}`;
    }
    try {
      const obj = JSON.parse(text) as { message?: string; error?: string };
      return obj.message || obj.error || text;
    } catch {
      return text;
    }
  } catch {
    return `HTTP ${res.status}`;
  }
}
