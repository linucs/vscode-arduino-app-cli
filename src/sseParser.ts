import type {
  SseEvent,
  SseProgress,
  SseMessage,
  SseError,
  AppInfo,
} from "./api/types";

/**
 * A complete Server-Sent Event frame: an `event:` type (default "message")
 * plus the concatenated `data:` lines and an optional `id:`.
 */
export interface RawSseEvent {
  event: string;
  data: string;
  id?: string;
}

/**
 * Incremental SSE frame parser.
 *
 * SSE frames are newline-delimited fields terminated by a blank line. Because a
 * network read can split anywhere — mid-field, mid-frame, or pack several frames
 * into one chunk — the parser keeps a line buffer across `push()` calls and only
 * emits a frame when it sees the terminating blank line.
 *
 * Pure and transport-free (no fetch/grpc) so it can be unit-tested against canned
 * byte strings split at arbitrary boundaries — the SSE analogue of the sibling's
 * `buildStream.ts`.
 *
 * Spec notes honoured: lines may end with `\n`, `\r`, or `\r\n`; a leading space
 * after the field colon is stripped; lines starting with `:` are comments
 * (heartbeats) and ignored; multiple `data:` lines join with `\n`.
 */
export class SseFrameParser {
  private buf = "";
  private event = "";
  private data: string[] = [];
  private id: string | undefined;

  /** Feed a decoded text chunk; returns any frames completed by it. */
  push(chunk: string): RawSseEvent[] {
    this.buf += chunk;
    const out: RawSseEvent[] = [];
    let idx: number;
    // Split on any line terminator. Normalise CRLF/CR to LF first.
    this.buf = this.buf.replace(/\r\n?/g, "\n");
    while ((idx = this.buf.indexOf("\n")) >= 0) {
      const line = this.buf.slice(0, idx);
      this.buf = this.buf.slice(idx + 1);
      const frame = this.consumeLine(line);
      if (frame) {
        out.push(frame);
      }
    }
    return out;
  }

  /** Emit any buffered-but-unterminated frame at end of stream. */
  flush(): RawSseEvent[] {
    const out: RawSseEvent[] = [];
    if (this.buf.length > 0) {
      const frame = this.consumeLine(this.buf);
      if (frame) {
        out.push(frame);
      }
      this.buf = "";
    }
    // A trailing frame with collected fields but no final blank line.
    if (this.data.length > 0 || this.event !== "" || this.id !== undefined) {
      out.push(this.finish());
    }
    return out;
  }

  /** Process one complete line; returns a frame on a dispatching blank line. */
  private consumeLine(line: string): RawSseEvent | undefined {
    if (line === "") {
      // Blank line dispatches the accumulated frame (if any).
      if (this.data.length > 0 || this.event !== "" || this.id !== undefined) {
        return this.finish();
      }
      return undefined;
    }
    if (line.startsWith(":")) {
      // Comment / heartbeat — ignore.
      return undefined;
    }
    const colon = line.indexOf(":");
    const field = colon === -1 ? line : line.slice(0, colon);
    let value = colon === -1 ? "" : line.slice(colon + 1);
    if (value.startsWith(" ")) {
      value = value.slice(1);
    }
    switch (field) {
      case "event":
        this.event = value;
        break;
      case "data":
        this.data.push(value);
        break;
      case "id":
        this.id = value;
        break;
      // "retry" and unknown fields are ignored.
    }
    return undefined;
  }

  private finish(): RawSseEvent {
    const frame: RawSseEvent = {
      event: this.event || "message",
      data: this.data.join("\n"),
      id: this.id,
    };
    this.event = "";
    this.data = [];
    this.id = undefined;
    return frame;
  }
}

/**
 * Decode a raw frame into a typed {@link SseEvent}. The `data` payload is
 * JSON-parsed; if parsing fails the raw string is kept as `data`.
 */
export function decodeSseEvent(raw: RawSseEvent): SseEvent {
  let data: unknown = raw.data;
  if (raw.data) {
    try {
      data = JSON.parse(raw.data);
    } catch {
      data = raw.data;
    }
  }
  switch (raw.event) {
    case "progress":
      return { event: "progress", data: data as SseProgress };
    case "message":
      return { event: "message", data: data as SseMessage };
    case "app":
      return { event: "app", data: data as AppInfo };
    case "error":
      return { event: "error", data: data as SseError };
    default:
      return { event: raw.event, data };
  }
}
