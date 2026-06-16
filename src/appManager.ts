import * as path from "node:path";
import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";
import type { AppInfo, AppListResponse } from "./api/types";

/**
 * App lifecycle operations: create / run (start) / stop / restart / delete /
 * console (logs) / export / import / clone / rename / edit / default / cache.
 *
 * "Run" performs the whole-app operation App Lab exposes: the daemon compiles &
 * flashes the sketch to the MCU and starts the Python side, streaming progress
 * over SSE which we surface via a notification + the console output channel.
 */
export class AppManager {
  private readonly logChannels = new Map<string, vscode.OutputChannel>();
  private readonly pythonChannels = new Map<string, vscode.OutputChannel>();
  private readonly logAborts = new Map<string, AbortController>();

  constructor(
    private readonly client: AppLabClient,
    private readonly console: vscode.OutputChannel,
    private readonly onChanged: () => void,
    /**
     * Optional sink for each Python/runtime log line (newline-terminated), used
     * to feed the serial plotter when the user selects "Python" as its source.
     */
    private readonly onLogLine?: (text: string) => void,
    /**
     * Called after a successful run (compile + flash + start), so dependents can
     * react to the freshly rebuilt sketch — e.g. regenerate C++ IntelliSense.
     */
    private readonly onRan?: (app: AppInfo) => void,
  ) {}

  list(filter?: "apps" | "examples"): Promise<AppListResponse> {
    return this.client.listApps(filter ? { filter } : undefined);
  }

  async create(): Promise<void> {
    const name = await vscode.window.showInputBox({
      title: vscode.l10n.t("New App"),
      prompt: vscode.l10n.t("App name"),
      validateInput: (v) => (v.trim() ? undefined : vscode.l10n.t("Name is required")),
    });
    if (!name) {
      return;
    }
    const description = await vscode.window.showInputBox({
      title: vscode.l10n.t("New App"),
      prompt: vscode.l10n.t("Description (optional)"),
    });
    if (description === undefined) {
      return;
    }
    const sketch = await vscode.window.showQuickPick(
      [
        { label: vscode.l10n.t("Python + Sketch"), no_sketch: false },
        { label: vscode.l10n.t("Python only (no sketch)"), no_sketch: true },
      ],
      { title: vscode.l10n.t("App type") },
    );
    if (!sketch) {
      return;
    }
    const created = await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: vscode.l10n.t("Creating app…") },
      () => this.client.createApp({ name, description: description || undefined }, { skipSketch: sketch.no_sketch }),
    );
    this.onChanged();

    // Open the new app in its own window. The create response may omit `path`
    // (like the list endpoint), so fall back to the app detail to resolve it.
    let folder = created.path;
    if (!folder) {
      const detail = await this.client.getApp(created.id).catch(() => undefined);
      folder = detail?.path;
    }
    if (folder) {
      await vscode.commands.executeCommand("vscode.openFolder", vscode.Uri.file(folder), {
        forceNewWindow: true,
      });
    } else {
      vscode.window.showInformationMessage(vscode.l10n.t("Created app {0}.", created.name));
    }
  }

  /**
   * Run = compile+flash the sketch and start the app (streaming progress).
   * Only one app runs at a time, so if another app is already running we ask to
   * switch — stopping it first — mirroring App Lab's swap dialog.
   */
  async run(app: AppInfo): Promise<void> {
    let running: AppInfo[] = [];
    try {
      const list = await this.client.listApps();
      running = (list.apps ?? []).filter(
        (a) => a.id !== app.id && (a.status === "running" || a.status === "starting"),
      );
    } catch {
      // If we can't list, just attempt to start.
    }
    if (running.length) {
      const names = running.map((a) => a.name).join(", ");
      const switchLabel = vscode.l10n.t("Switch");
      const choice = await vscode.window.showWarningMessage(
        vscode.l10n.t('"{0}" is currently running. Stop it and run "{1}"?', names, app.name),
        { modal: true },
        switchLabel,
      );
      if (choice !== switchLabel) {
        return;
      }
      for (const r of running) {
        await this.streamLifecycle(r, vscode.l10n.t("Stopping {0}…", r.name), (sinks, signal) =>
          this.client.stopApp(r.id, sinks, signal),
        );
      }
    }
    await this.streamLifecycle(app, vscode.l10n.t("Running {0}…", app.name), (sinks, signal) =>
      this.client.startApp(app.id, sinks, { signal }),
    );
    // streamLifecycle throws on failure, so reaching here means the build + start
    // succeeded and the compilation database under .cache/sketch/ is up to date.
    this.onRan?.(app);
  }

  async stop(app: AppInfo): Promise<void> {
    await this.streamLifecycle(app, vscode.l10n.t("Stopping {0}…", app.name), (sinks, signal) =>
      this.client.stopApp(app.id, sinks, signal),
    );
  }

  async restart(app: AppInfo): Promise<void> {
    await this.stop(app);
    await this.run(app);
  }

  private async streamLifecycle(
    app: AppInfo,
    title: string,
    run: (
      sinks: Parameters<AppLabClient["startApp"]>[1],
      signal: AbortSignal,
    ) => Promise<void>,
  ): Promise<void> {
    const channel = this.channelFor(app);
    channel.show(true);
    channel.appendLine(`\n=== ${title} ===`);
    let failure: string | undefined;
    await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title, cancellable: true },
      async (progress, token) => {
        const ctrl = new AbortController();
        token.onCancellationRequested(() => ctrl.abort());
        await run(
          {
            onProgress: (p) =>
              progress.report({ message: `${p.name} ${Math.round((p.progress ?? 0) * 100)}%` }),
            onMessage: (m) => channel.appendLine(m.message),
            onError: (e) => {
              failure = e.message;
              channel.appendLine(`[error] ${e.message}`);
            },
          },
          ctrl.signal,
        );
      },
    );
    // No onChanged(): a run/stop is a status-only change, and the status flows
    // back to the views via the `/apps/events` SSE — no re-list needed.
    if (failure) {
      throw new Error(failure);
    }
  }

  /**
   * Tail the app's runtime console (Python + service logs) into its own
   * dedicated channel — mirroring App Lab's "Python" tab, kept separate from the
   * "App launch" (start/stop) output. Each line is also forwarded to the plotter
   * feed sink so the plotter can chart `>`-prefixed telemetry from Python.
   * Returns once the stream is attached (it follows until aborted).
   */
  async showLogs(app: AppInfo): Promise<void> {
    this.logAborts.get(app.id)?.abort();
    const channel = this.pythonChannelFor(app);
    channel.show(true);
    const tail = vscode.workspace.getConfiguration("appLab").get<number>("logs.tail", 200);
    const ctrl = new AbortController();
    this.logAborts.set(app.id, ctrl);
    channel.appendLine(`\n=== ${vscode.l10n.t("Console: {0}", app.name)} ===`);
    this.client
      .appLogs(
        app.id,
        {
          onMessage: (m) => {
            channel.appendLine(m.message);
            this.onLogLine?.(m.message + "\n");
          },
          onError: (e) => channel.appendLine(`[error] ${e.message}`),
        },
        { filter: "app,services", tail, signal: ctrl.signal },
      )
      .catch((err) => channel.appendLine(`[error] ${err instanceof Error ? err.message : String(err)}`));
  }

  async destroy(app: AppInfo): Promise<void> {
    const ok = await vscode.window.showWarningMessage(
      vscode.l10n.t('Delete app "{0}"? This cannot be undone.', app.name),
      { modal: true },
      vscode.l10n.t("Delete"),
    );
    if (!ok) {
      return;
    }
    await this.client.deleteApp(app.id);
    this.onChanged();
  }

  async clone(app: AppInfo): Promise<void> {
    const name = await vscode.window.showInputBox({
      title: vscode.l10n.t("Copy and Edit App"),
      prompt: vscode.l10n.t("Name for the copy"),
      value: `${app.name} copy`,
    });
    if (!name) {
      return;
    }
    await this.client.cloneApp(app.id, { name });
    this.onChanged();
  }

  async rename(app: AppInfo): Promise<void> {
    const name = await vscode.window.showInputBox({
      title: vscode.l10n.t("Rename App"),
      value: app.name,
      validateInput: (v) => (v.trim() ? undefined : vscode.l10n.t("Name is required")),
    });
    if (!name || name === app.name) {
      return;
    }
    await this.client.patchApp(app.id, { name });
    this.onChanged();
  }

  async edit(app: AppInfo): Promise<void> {
    const description = await vscode.window.showInputBox({
      title: vscode.l10n.t("Edit App Details"),
      prompt: vscode.l10n.t("Description"),
      value: app.description ?? "",
    });
    if (description === undefined) {
      return;
    }
    await this.client.patchApp(app.id, { description });
    this.onChanged();
  }

  async setDefault(app: AppInfo): Promise<void> {
    await this.client.patchApp(app.id, { default: true });
    vscode.window.showInformationMessage(vscode.l10n.t('"{0}" is now the default app.', app.name));
    this.onChanged();
  }

  async export(app: AppInfo): Promise<void> {
    const target = await vscode.window.showSaveDialog({
      title: vscode.l10n.t("Export App"),
      defaultUri: vscode.Uri.file(path.join(homeDir(), `${app.id}.zip`)),
      filters: { Zip: ["zip"] },
    });
    if (!target) {
      return;
    }
    const includeData =
      (await vscode.window.showQuickPick([vscode.l10n.t("No"), vscode.l10n.t("Yes")], {
        title: vscode.l10n.t("Include data directory?"),
      })) === vscode.l10n.t("Yes");
    await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: vscode.l10n.t("Exporting…") },
      () => this.client.exportApp(app.id, target.fsPath, { includeData }),
    );
    vscode.window.showInformationMessage(vscode.l10n.t("Exported to {0}", target.fsPath));
  }

  async import(): Promise<void> {
    const picked = await vscode.window.showOpenDialog({
      title: vscode.l10n.t("Import App"),
      canSelectMany: false,
      filters: { Zip: ["zip"] },
    });
    if (!picked || picked.length === 0) {
      return;
    }
    await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: vscode.l10n.t("Importing…") },
      () => this.client.importApp(picked[0].fsPath),
    );
    this.onChanged();
  }

  async cleanCache(app: AppInfo): Promise<void> {
    await this.client.cli(["app", "clean-cache", app.id, "--force"]);
    vscode.window.showInformationMessage(vscode.l10n.t("Cleared cache for {0}.", app.name));
  }

  async openExposedPort(app: AppInfo): Promise<void> {
    const ports = await this.client.exposedPorts(app.id).catch(() => []);
    if (!ports.length) {
      vscode.window.showInformationMessage(vscode.l10n.t("No exposed ports for this app."));
      return;
    }
    const pick = await vscode.window.showQuickPick(
      ports.map((p) => ({ label: `${p.name ?? p.port}`, description: `:${p.port}`, port: p.port })),
      { title: vscode.l10n.t("Open Exposed Port") },
    );
    if (!pick) {
      return;
    }
    await vscode.env.openExternal(vscode.Uri.parse(`http://${hostFromConfig()}:${pick.port}`));
  }

  async revealInExplorer(app: AppInfo): Promise<void> {
    // The list endpoint omits `path`; fetch the app detail to resolve the folder.
    let folder = app.path;
    if (!folder) {
      const detail = await this.client.getApp(app.id).catch(() => undefined);
      folder = detail?.path;
    }
    if (!folder) {
      vscode.window.showWarningMessage(vscode.l10n.t("Could not resolve the folder for {0}.", app.name));
      return;
    }
    const uri = vscode.Uri.file(folder);
    // If the app's folder is already part of the open workspace — whether it is
    // the sole root or one of several — just reveal and focus it in the Explorer.
    // Reopening the window would be jarring and pointless when it's right there.
    if (vscode.workspace.getWorkspaceFolder(uri)) {
      await vscode.commands.executeCommand("revealInExplorer", uri);
      return;
    }
    // Not in the workspace: open the folder as the workspace root (in this window).
    await vscode.commands.executeCommand("vscode.openFolder", uri, { forceNewWindow: false });
  }

  dispose(): void {
    for (const c of this.logAborts.values()) {
      c.abort();
    }
    for (const ch of this.logChannels.values()) {
      ch.dispose();
    }
    for (const ch of this.pythonChannels.values()) {
      ch.dispose();
    }
  }

  /** The "App launch" channel — start/stop lifecycle output. */
  private channelFor(app: AppInfo): vscode.OutputChannel {
    let ch = this.logChannels.get(app.id);
    if (!ch) {
      ch = vscode.window.createOutputChannel(`Arduino App: ${app.name}`);
      this.logChannels.set(app.id, ch);
    }
    return ch;
  }

  /** The "Python" channel — runtime container/service logs, kept separate. */
  private pythonChannelFor(app: AppInfo): vscode.OutputChannel {
    let ch = this.pythonChannels.get(app.id);
    if (!ch) {
      ch = vscode.window.createOutputChannel(`Arduino App: ${app.name} — Python`);
      this.pythonChannels.set(app.id, ch);
    }
    return ch;
  }
}

function homeDir(): string {
  return process.env.HOME || process.env.USERPROFILE || ".";
}

function hostFromConfig(): string {
  return vscode.workspace.getConfiguration("appLab").get<string>("daemon.host", "127.0.0.1");
}
