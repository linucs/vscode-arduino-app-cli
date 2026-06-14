import * as path from "node:path";
import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";
import type { AppInfo } from "./api/types";

/**
 * Tree-independent registry of the apps the daemon knows about, keyed by id. It
 * exists so app discovery survives the removal of the My-Apps tree:
 * {@link ActiveAppTracker} resolves the active editor's app through
 * {@link resolveByPath}, and the Examples view projects {@link examples} off it.
 *
 * The daemon's `GET /v1/apps` list omits the filesystem `path` (only the
 * per-app detail carries it), so we cannot match the active file to an app by
 * path directly. Instead we exploit the id scheme: an app id is
 * `base64("<group>:<folder>")` (e.g. `dXNlcjpuOG4tYnJpZGdl` → `user:n8n-bridge`),
 * and the `<folder>` segment is the basename of the app's directory. Matching
 * that against the basename of the directory holding `app.yaml` resolves the
 * active app with no extra round-trips. Folder names are unique within the
 * user's apps dir, so the match is exact; on a user/example name collision we
 * prefer the user's own app.
 *
 * Listing apps is expensive on the board (the daemon rescans the filesystem and
 * parses every app.yaml on each `GET /v1/apps`), so we do **not** list at startup:
 * the `/apps/events` SSE emits a full snapshot (apps + examples) on connect, which
 * bootstraps the map via {@link applyStatus}. Only a structural change (create,
 * delete, manual refresh, reconnect-resync) re-lists — unfiltered — via {@link refresh}.
 */
export class AppRegistry {
  /** Latest apps seen, keyed by id. */
  private readonly byId = new Map<string, AppInfo>();

  /** Set once the SSE has delivered its first event (drives the Examples loading state). */
  private booted = false;

  /** Fires whenever the map changes, so dependent views can re-render. */
  private readonly changed = new vscode.EventEmitter<void>();
  readonly onDidChange = this.changed.event;

  constructor(private readonly client: () => Promise<AppLabClient>) {}

  /** Whether the SSE snapshot has started arriving (used for the Examples loading state). */
  hasBooted(): boolean {
    return this.booted;
  }

  get(id: string): AppInfo | undefined {
    return this.byId.get(id);
  }

  /** The example apps currently known, sorted by name for a stable view. */
  examples(): AppInfo[] {
    return [...this.byId.values()]
      .filter((a) => a.example === true)
      .sort((a, b) => a.name.localeCompare(b.name));
  }

  /**
   * Resolve the app that owns `appRoot` — the directory holding `app.yaml` —
   * by matching its basename to the folder segment of each app id.
   */
  resolveByPath(appRoot: string): AppInfo | undefined {
    const base = path.basename(appRoot);
    let exampleMatch: AppInfo | undefined;
    for (const app of this.byId.values()) {
      if (folderOf(app.id) !== base) {
        continue;
      }
      if (app.example) {
        exampleMatch ??= app;
      } else {
        return app;
      }
    }
    return exampleMatch;
  }

  /**
   * Hard re-list (apps + examples) and atomically replace the index. Unfiltered so
   * examples survive; full replace so **deletions** are reflected (the SSE patches
   * are upsert-only and can't remove rows). Used for structural changes and the
   * reconnect resync; a manual list does not trigger SSE feedback.
   */
  async refresh(): Promise<void> {
    const client = await this.client();
    const res = await client.listApps();
    this.byId.clear();
    for (const a of res.apps ?? []) {
      this.byId.set(a.id, a);
    }
    this.changed.fire();
  }

  /** Upsert apps into the index (used by the load and by the Examples view). */
  merge(apps: AppInfo[]): void {
    if (!apps.length) {
      return;
    }
    for (const a of apps) {
      // Merge so fields a partial event omits (description, icon) survive.
      this.byId.set(a.id, { ...this.byId.get(a.id), ...a });
    }
    this.changed.fire();
  }

  /** Apply a live status update (one `app` event from the SSE). */
  applyStatus(app: AppInfo): void {
    this.booted = true;
    this.merge([app]);
  }

  dispose(): void {
    this.changed.dispose();
  }
}

/** The `<folder>` of an app id (`base64("<group>:<folder>")`), or undefined. */
function folderOf(id: string): string | undefined {
  try {
    // Accept both standard and URL-safe base64.
    const norm = id.replace(/-/g, "+").replace(/_/g, "/");
    const decoded = Buffer.from(norm, "base64").toString("utf8");
    if (!decoded || decoded.includes("�")) {
      return undefined;
    }
    const colon = decoded.lastIndexOf(":");
    return colon === -1 ? decoded : decoded.slice(colon + 1);
  } catch {
    return undefined;
  }
}
