/**
 * Hand-written TypeScript interfaces for the arduino-app-cli daemon REST/SSE
 * payloads. The daemon has no gRPC/proto surface, so these are maintained by
 * hand against `internal/api/handlers/*` and the `--format json` CLI output.
 *
 * Fields are intentionally permissive (most optional) — the daemon evolves and
 * we only depend on a stable core. Keep this file as the single source of truth
 * for response shapes.
 */

export type AppStatus =
  | "running"
  | "starting"
  | "stopping"
  | "stopped"
  | "failed"
  | "uninitialized"
  | "unknown";

/**
 * Whether an app is up or transitioning up/down (Stop applies). Everything else
 * — stopped, failed, uninitialized, unknown, or an omitted status — is treated
 * as "can Run". Used to gate the Run/Stop controls.
 */
export function isAppRunning(status?: string): boolean {
  return status === "running" || status === "starting" || status === "stopping";
}

/** One app as returned by `GET /v1/apps` and `GET /v1/apps/{id}`. */
export interface AppInfo {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  path?: string;
  status: AppStatus;
  example?: boolean;
  default?: boolean;
  bricks?: BrickInstance[];
}

/** An app the daemon could load metadata for but considers broken. */
export interface BrokenAppInfo {
  id: string;
  name?: string;
  path?: string;
  error: string;
}

export interface AppListResponse {
  apps: AppInfo[];
  broken_apps?: BrokenAppInfo[];
}

/** A configurable brick variable (`config_variables[]`). */
export interface BrickConfigVariable {
  name: string;
  value?: string;
  description?: string;
  required?: boolean;
}

/** A brick from the global catalog (`GET /v1/bricks`) or its details. */
export interface BrickInfo {
  id: string;
  name: string;
  author?: string;
  category?: string;
  description?: string;
  status?: string;
  require_model?: boolean;
  readme?: string;
  config_variables?: BrickConfigVariable[];
}

/** A brick instance attached to an app (`GET /v1/apps/{id}/bricks`). */
export interface BrickInstance {
  id: string;
  name: string;
  author?: string;
  category?: string;
  status?: string;
  require_model?: boolean;
  model?: string;
  readme?: string;
  config_variables?: BrickConfigVariable[];
  /** Deprecated flat map kept for backward compatibility. */
  variables?: Record<string, string>;
}

/** An AI model (`GET /v1/models`). */
export interface ModelInfo {
  id: string;
  name: string;
  description?: string;
  runner?: string;
  brick_ids?: string[];
  is_builtin?: boolean;
  disk_usage?: number;
}

/** A library from the Arduino catalog (`GET /v1/libraries`). */
export interface LibraryInfo {
  name: string;
  author?: string;
  sentence?: string;
  versions?: string[];
  latest?: string;
}

/**
 * A library attached to an app's sketch. The daemon returns these as plain
 * `"Name"` / `"Name@version"` strings; we parse them into this shape.
 */
export interface SketchLibrary {
  name: string;
  version?: string;
}

export interface VersionResponse {
  version: string;
  commit?: string;
  date?: string;
}

export interface ResourcesResponse {
  cpu?: number;
  memory?: { used: number; total: number };
  disk?: { used: number; total: number };
}

export interface ExposedPort {
  name?: string;
  port: number;
  protocol?: string;
}

// ---- SSE event payloads (event: <type>\ndata: <json>) ----

export interface SseProgress {
  name: string;
  progress: number;
}

export interface SseMessage {
  id?: string;
  brick_id?: string;
  message: string;
}

export interface SseError {
  code: string;
  message: string;
}

/** Discriminated decode of a raw SSE frame. `data` is JSON-parsed when possible. */
export type SseEvent =
  | { event: "progress"; data: SseProgress }
  | { event: "message"; data: SseMessage }
  | { event: "app"; data: AppInfo }
  | { event: "error"; data: SseError }
  | { event: string; data: unknown };
