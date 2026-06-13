import * as fs from "node:fs";
import * as path from "node:path";
import * as vscode from "vscode";
import { isAppRunning, type AppInfo } from "./api/types";
import { activeDocumentUri } from "./workspaceRoot";

/**
 * Tracks the "current app" — the app that owns the active editor file — mirroring
 * App Lab's app-scoped Run/Stop. Resolution walks the active file's path up to
 * the nearest `app.yaml`, then asks the {@link AppRegistry} which app owns that
 * directory. The registry holds the freshest status (kept current by the SSE),
 * so {@link current} always reflects live state.
 *
 * Publishes two context keys that gate the editor toolbar and status bar:
 *  - `appLab.activeApp`        the app id (or "")
 *  - `appLab.activeAppStatus`  the app status, or "none"
 */
export class ActiveAppTracker {
  private readonly emitter = new vscode.EventEmitter<void>();
  readonly onDidChange = this.emitter.event;

  /** Directory of the active editor's nearest `app.yaml`, if any. */
  private appRoot: string | undefined;

  constructor(private readonly resolve: (appRoot: string) => AppInfo | undefined) {}

  /** Wire editor + selection listeners. Returns disposables for subscriptions. */
  register(): vscode.Disposable {
    const d1 = vscode.window.onDidChangeActiveTextEditor(() => this.refreshFromEditor());
    const d2 = vscode.window.tabGroups.onDidChangeTabs(() => this.refreshFromEditor());
    this.refreshFromEditor();
    return vscode.Disposable.from(d1, d2, this.emitter);
  }

  /** The resolved current app (with freshest known status), if any. */
  get current(): AppInfo | undefined {
    return this.appRoot ? this.resolve(this.appRoot) : undefined;
  }

  /**
   * Re-publish without re-walking the filesystem. Called when the registry
   * lists or a status event arrives, so the toolbar/status bar reflect the
   * active app as soon as it becomes known and flip on every status change.
   */
  reresolve(): void {
    this.publish();
  }

  private refreshFromEditor(): void {
    const uri = activeDocumentUri();
    this.appRoot = uri && uri.scheme === "file" ? findAppRoot(uri.fsPath) : undefined;
    this.publish();
  }

  private publish(): void {
    const app = this.current;
    // Normalise to running/stopped/none so the editor toolbar gates correctly.
    const status = app ? (isAppRunning(app.status) ? "running" : "stopped") : "none";
    void vscode.commands.executeCommand("setContext", "appLab.activeApp", app?.id ?? "");
    void vscode.commands.executeCommand("setContext", "appLab.activeAppStatus", status);
    this.emitter.fire();
  }
}

/** Walk up from a file path to the nearest directory containing `app.yaml`. */
export function findAppRoot(filePath: string): string | undefined {
  let dir = path.dirname(filePath);
  for (let i = 0; i < 40; i++) {
    if (fs.existsSync(path.join(dir, "app.yaml"))) {
      return dir;
    }
    const parent = path.dirname(dir);
    if (parent === dir) {
      break;
    }
    dir = parent;
  }
  return undefined;
}
