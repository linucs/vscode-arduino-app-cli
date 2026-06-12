import * as fs from "node:fs";
import * as path from "node:path";
import * as vscode from "vscode";
import { isAppRunning, type AppInfo, type AppStatus } from "./api/types";
import { activeDocumentUri } from "./workspaceRoot";

/**
 * Tracks the "current app" — the app that owns the active editor file — mirroring
 * App Lab's app-scoped Run/Stop. Resolution walks the active file's path up to
 * the nearest `app.yaml`; if no editor maps to an app, the last app selected in
 * the Apps tree is used as a fallback.
 *
 * Publishes two context keys that gate the editor toolbar and status bar:
 *  - `appLab.activeApp`        the app id (or "")
 *  - `appLab.activeAppStatus`  the app status, or "none"
 */
export class ActiveAppTracker {
  private readonly emitter = new vscode.EventEmitter<void>();
  readonly onDidChange = this.emitter.event;

  private appPath: string | undefined;
  private app: AppInfo | undefined;
  private statusByPath = new Map<string, AppStatus>();

  constructor(private readonly findByPath: (p: string) => AppInfo | undefined) {}

  /** Wire editor + selection listeners. Returns disposables for subscriptions. */
  register(): vscode.Disposable {
    const d1 = vscode.window.onDidChangeActiveTextEditor(() => this.refreshFromEditor());
    const d2 = vscode.window.tabGroups.onDidChangeTabs(() => this.refreshFromEditor());
    this.refreshFromEditor();
    return vscode.Disposable.from(d1, d2, this.emitter);
  }

  /** The resolved current app (with freshest known status), if any. */
  get current(): AppInfo | undefined {
    if (!this.appPath) {
      return this.app;
    }
    const fromTree = this.findByPath(this.appPath);
    const app = fromTree ?? this.app;
    if (!app) {
      return undefined;
    }
    const status = this.statusByPath.get(this.appPath);
    return status ? { ...app, status } : app;
  }

  /** Explicitly select an app (e.g. from a tree click) as the fallback target. */
  select(app: AppInfo | undefined): void {
    this.app = app;
    this.appPath = app?.path;
    this.publish();
  }

  /** Feed live status updates (from the `/apps/events` SSE) so the toolbar tracks. */
  updateStatus(app: AppInfo): void {
    if (app.path) {
      this.statusByPath.set(app.path, app.status);
    }
    if (this.app && this.app.id === app.id) {
      this.app = { ...this.app, ...app };
    }
    this.publish();
  }

  private refreshFromEditor(): void {
    const uri = activeDocumentUri();
    const appRoot = uri && uri.scheme === "file" ? findAppRoot(uri.fsPath) : undefined;
    if (appRoot) {
      this.appPath = appRoot;
      this.app = this.findByPath(appRoot) ?? this.app;
    }
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
