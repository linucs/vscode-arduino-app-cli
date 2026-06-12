import * as assert from "assert";
import { SseFrameParser, decodeSseEvent } from "../sseParser";

/** Feed a whole payload one byte at a time to stress chunk-boundary handling. */
function pushByByte(parser: SseFrameParser, text: string) {
  const frames = [];
  for (const ch of text) {
    frames.push(...parser.push(ch));
  }
  frames.push(...parser.flush());
  return frames;
}

suite("SseFrameParser", () => {
  test("parses a single event with type and data", () => {
    const p = new SseFrameParser();
    const frames = p.push("event: progress\ndata: {\"name\":\"x\",\"progress\":0.5}\n\n");
    assert.strictEqual(frames.length, 1);
    assert.strictEqual(frames[0].event, "progress");
    assert.strictEqual(frames[0].data, '{"name":"x","progress":0.5}');
  });

  test("defaults the event type to 'message'", () => {
    const p = new SseFrameParser();
    const frames = p.push("data: hello\n\n");
    assert.strictEqual(frames.length, 1);
    assert.strictEqual(frames[0].event, "message");
    assert.strictEqual(frames[0].data, "hello");
  });

  test("joins multiple data lines with newlines", () => {
    const p = new SseFrameParser();
    const frames = p.push("data: line1\ndata: line2\n\n");
    assert.strictEqual(frames[0].data, "line1\nline2");
  });

  test("emits multiple events from one chunk", () => {
    const p = new SseFrameParser();
    const frames = p.push("data: a\n\ndata: b\n\n");
    assert.strictEqual(frames.length, 2);
    assert.deepStrictEqual(frames.map((f) => f.data), ["a", "b"]);
  });

  test("reassembles an event split across arbitrary byte boundaries", () => {
    const p = new SseFrameParser();
    const frames = pushByByte(p, "event: app\ndata: {\"id\":\"a1\"}\n\n");
    assert.strictEqual(frames.length, 1);
    assert.strictEqual(frames[0].event, "app");
    assert.strictEqual(frames[0].data, '{"id":"a1"}');
  });

  test("handles CRLF and CR line endings", () => {
    const p = new SseFrameParser();
    const frames = p.push("event: message\r\ndata: hi\r\n\r\n");
    assert.strictEqual(frames.length, 1);
    assert.strictEqual(frames[0].event, "message");
    assert.strictEqual(frames[0].data, "hi");
  });

  test("ignores comment/heartbeat lines", () => {
    const p = new SseFrameParser();
    const frames = p.push(": keep-alive\n\ndata: real\n\n");
    assert.strictEqual(frames.length, 1);
    assert.strictEqual(frames[0].data, "real");
  });

  test("strips only a single leading space after the colon", () => {
    const p = new SseFrameParser();
    const frames = p.push("data:  two-leading-spaces\n\n");
    assert.strictEqual(frames[0].data, " two-leading-spaces");
  });

  test("flush emits a trailing frame with no terminating blank line", () => {
    const p = new SseFrameParser();
    assert.strictEqual(p.push("data: partial\n").length, 0);
    const frames = p.flush();
    assert.strictEqual(frames.length, 1);
    assert.strictEqual(frames[0].data, "partial");
  });

  test("carries the id field through", () => {
    const p = new SseFrameParser();
    const frames = p.push("id: 42\ndata: x\n\n");
    assert.strictEqual(frames[0].id, "42");
  });
});

suite("decodeSseEvent", () => {
  test("JSON-parses progress payloads", () => {
    const e = decodeSseEvent({ event: "progress", data: '{"name":"flash","progress":0.25}' });
    assert.strictEqual(e.event, "progress");
    assert.deepStrictEqual(e.data, { name: "flash", progress: 0.25 });
  });

  test("decodes app events into AppInfo", () => {
    const e = decodeSseEvent({ event: "app", data: '{"id":"a1","name":"My App","status":"running"}' });
    assert.strictEqual(e.event, "app");
    assert.deepStrictEqual(e.data, { id: "a1", name: "My App", status: "running" });
  });

  test("keeps raw string when data is not valid JSON", () => {
    const e = decodeSseEvent({ event: "message", data: "plain text" });
    assert.strictEqual(e.data, "plain text");
  });

  test("passes through unknown event types", () => {
    const e = decodeSseEvent({ event: "custom", data: '{"k":1}' });
    assert.strictEqual(e.event, "custom");
    assert.deepStrictEqual(e.data, { k: 1 });
  });
});
