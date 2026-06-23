import * as vscode from "vscode";
import { DaemonManager } from "./daemon";
import { AppLabClient } from "./appLabClient";
import { AppManager } from "./appManager";
import { BrickManager } from "./brickManager";
import { ModelManager } from "./modelManager";
import { SketchLibManager } from "./sketchLibManager";
import { SystemManager } from "./systemManager";
import { SerialMonitor } from "./monitor";
import { PlotterPanel } from "./plotterPanel";
import { PlotterFeeder } from "./plotterFeeder";
import { AppRegistry } from "./appRegistry";
import { ExamplesTreeProvider } from "./examplesView";
import { InstalledAppsTreeProvider } from "./installedAppsView";
import { AppItemsTreeProvider } from "./appBricksView";
import { BricksTreeProvider } from "./bricksView";
import { ModelsTreeProvider } from "./modelsView";
import { ActiveAppTracker } from "./activeApp";
import { FastReloadManager } from "./fastReload";
import { IntelliSenseManager } from "./intellisense";
import { StatusBar } from "./statusBar";
import { installAiAssistants } from "./skill/installSkill";
import type { AppInfo, BrickInstance, ModelInfo, SketchLibrary, VersionResponse } from "./api/types";

interface Ready {
  client: AppLabClient;
  apps: AppManager;
  bricks: BrickManager;
  models: ModelManager;
  sketchLibs: SketchLibManager;
  system: SystemManager;
  monitor: SerialMonitor;
  intellisense: IntelliSenseManager;
}

let context: vscode.ExtensionContext;
let output: vscode.OutputChannel;
let daemon: DaemonManager;
let registry: AppRegistry;
let activeTracker: ActiveAppTracker;
let fastReload: FastReloadManager;
let statusBar: StatusBar;
let examplesView: ExamplesTreeProvider;
let installedAppsView: InstalledAppsTreeProvider;
let appBricksView: AppItemsTreeProvider;
let appLibsView: AppItemsTreeProvider;
let bricksView: BricksTreeProvider;
let modelsView: ModelsTreeProvider;

let ready: Ready | undefined;
let readyPromise: Promise<Ready | undefined> | undefined;

// The serial plotter is fed from ONE source at a time — the serial monitor or
// the Python log stream — chosen by the user when they open it. Both producers
// forward their chunks to this single feeder, gated by `plotterSource`.
const plotterFeeder = new PlotterFeeder();
let plotterSource: "serial" | "python" | undefined;
let statusAbort: AbortController | undefined;
let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
let reconnectAttempts = 0;
let lastAppClick: { id: string; time: number } | undefined;

/** Bounded background reconnect: re-probe every 5s, up to ~1 minute. */
const RECONNECT_DELAY_MS = 5000;
const RECONNECT_MAX_ATTEMPTS = 12;

export function activate(ctx: vscode.ExtensionContext) {
  context = ctx;
  output = vscode.window.createOutputChannel("Arduino App CLI");
  ctx.subscriptions.push(output);

  daemon = new DaemonManager(output);

  maybeAnnounceVersion(ctx);

  const clientOf = async () => (await ensureReady())!.client;
  registry = new AppRegistry(clientOf);
  examplesView = new ExamplesTreeProvider(registry);
  installedAppsView = new InstalledAppsTreeProvider(registry);
  appBricksView = new AppItemsTreeProvider("bricks", clientOf, () => activeTracker.current);
  appLibsView = new AppItemsTreeProvider("libs", clientOf, () => activeTracker.current);
  bricksView = new BricksTreeProvider(async () => (await ensureReady())!.bricks.listCatalog());
  modelsView = new ModelsTreeProvider(async () => (await ensureReady())!.models.list());

  activeTracker = new ActiveAppTracker((root) => registry.resolveByPath(root));
  statusBar = new StatusBar(activeTracker);
  fastReload = new FastReloadManager(ctx, {
    output,
    activeApp: () => activeTracker.current,
    // The apps list omits `path`; fall back to the detail endpoint, like
    // revealInExplorer does.
    resolveAppDir: async (app) => {
      if (app.path) {
        return app.path;
      }
      const d = await ensureReady();
      if (!d) {
        return undefined;
      }
      try {
        return (await d.client.getApp(app.id)).path;
      } catch {
        return undefined;
      }
    },
  });
  ctx.subscriptions.push(
    statusBar,
    activeTracker.register(),
    registry,
    examplesView,
    installedAppsView,
    fastReload,
  );

  // Once the active app changes, refresh the active-app Bricks and Libraries
  // views; once the registry lists/updates apps, the editor toolbar can resolve,
  // so re-run active-app resolution.
  ctx.subscriptions.push(
    activeTracker.onDidChange(() => {
      appBricksView.onActiveChanged();
      appLibsView.onActiveChanged();
      fastReload.onActiveAppChanged();
    }),
    registry.onDidChange(() => activeTracker.reresolve()),
  );

  ctx.subscriptions.push(
    vscode.window.createTreeView("appLab.appBricks", { treeDataProvider: appBricksView }),
    vscode.window.createTreeView("appLab.appLibs", { treeDataProvider: appLibsView }),
    vscode.window.createTreeView("appLab.installedApps", { treeDataProvider: installedAppsView }),
    vscode.window.createTreeView("appLab.apps", { treeDataProvider: examplesView }),
    vscode.window.createTreeView("appLab.bricks", { treeDataProvider: bricksView }),
    vscode.window.createTreeView("appLab.models", { treeDataProvider: modelsView }),
  );

  registerCommands(ctx);

  // Kick off a connection in the background so the views populate and the status
  // bar reflects reality without waiting for the first user action.
  void ensureReady();
}

/**
 * Announce the packaged version once per version by comparing it against the one
 * stored in globalState: on first install open the Get Started walkthrough, and
 * after an update surface a "What's New" notification linking to the changelog.
 * Cheap and daemon-independent, so it runs at activation without waiting on the
 * daemon connection.
 */
function maybeAnnounceVersion(ctx: vscode.ExtensionContext): void {
  const currentVersion = ctx.extension.packageJSON.version as string;
  const lastVersion = ctx.globalState.get<string>("lastVersion");
  if (lastVersion === currentVersion) {
    return;
  }
  void ctx.globalState.update("lastVersion", currentVersion);

  if (lastVersion === undefined) {
    // Fresh install → Get Started walkthrough.
    void vscode.commands.executeCommand(
      "workbench.action.openWalkthrough",
      `${ctx.extension.id}#appLab.welcome`,
      false,
    );
    return;
  }

  // Update → changelog notification.
  void showUpdateNotification(ctx, currentVersion);
}

async function showUpdateNotification(
  ctx: vscode.ExtensionContext,
  version: string,
): Promise<void> {
  const whatsNew = vscode.l10n.t("What's New");
  const choice = await vscode.window.showInformationMessage(
    vscode.l10n.t("Arduino App CLI updated to v{0}", version),
    whatsNew,
  );
  if (choice === whatsNew) {
    // Open the extension's native Changelog tab (rendered by VS Code from the
    // bundled CHANGELOG.md) rather than previewing the file by path, which is
    // unreliable in the installed layout.
    void vscode.commands.executeCommand(
      "extension.open",
      ctx.extension.id,
      "changelog",
    );
  }
}

export function deactivate() {
  statusAbort?.abort();
  cancelReconnect();
  ready?.monitor.dispose();
  ready?.apps.dispose();
  // We never own the daemon (it runs under systemd), so there's nothing to stop.
}

// A full re-sync of every view, for the broad manual action (reconnect). The
// Examples view re-renders off `registry.refresh()`'s change event, so it isn't
// listed here. Per-mutation refreshes are scoped to the affected view instead.
function refreshAll(): void {
  void registry.refresh();
  appBricksView.refresh();
  appLibsView.refresh();
  bricksView.refresh();
  modelsView.refresh();
}

/**
 * Connect to the daemon and wire the managers once.
 *
 * Memoised: concurrent callers (the three tree views + the background kick-off
 * all fire at activation) share ONE in-flight attempt, so daemon.start() — i.e.
 * the connection probe — runs at most once at a time instead of once per caller.
 */
function ensureReady(): Promise<Ready | undefined> {
  if (ready) {
    return Promise.resolve(ready);
  }
  if (!readyPromise) {
    readyPromise = doEnsureReady().finally(() => {
      readyPromise = undefined;
    });
  }
  return readyPromise;
}

async function doEnsureReady(): Promise<Ready | undefined> {
  if (ready) {
    return ready;
  }
  let version: VersionResponse;
  try {
    version = await daemon.start();
  } catch (err) {
    statusBar.setDisconnected();
    // Notify once on the initial failure; stay quiet while auto-reconnect retries.
    if (reconnectAttempts === 0) {
      vscode.window.showErrorMessage(
        vscode.l10n.t("Cannot reach the Arduino App CLI daemon: {0}", asMessage(err)),
      );
    }
    scheduleReconnect();
    return undefined;
  }

  const apiKey = vscode.workspace.getConfiguration("appLab").get<string>("apiKey", "");
  const cliPath = vscode.workspace.getConfiguration("appLab").get<string>("cliPath", "arduino-app-cli");
  const client = new AppLabClient({
    baseUrl: daemon.baseUrl,
    apiKey,
    cliPath,
    log: (m) => output.appendLine(m),
  });

  // Per-mutation refreshes are scoped to the view each manager actually changes,
  // so a single action doesn't re-scan everything. App structural changes re-list
  // (unfiltered) into the registry, which the Examples view + active-app toolbar
  // project off; run/stop refresh nothing (their status flows back via the SSE).
  const intellisense = new IntelliSenseManager(client, output, context);
  ready = {
    client,
    apps: new AppManager(
      client,
      output,
      () => void registry.refresh(),
      (text) => {
        if (plotterSource === "python") {
          plotterFeeder.feed(text);
        }
      },
      // After a successful run the sketch has been rebuilt, so refresh IntelliSense
      // from the fresh compilation database (gated by the user's setting).
      (app) => {
        if (intellisense.autoEnabled()) {
          void intellisense.configure(app, { silent: true });
        }
      },
    ),
    bricks: new BrickManager(client, () => appBricksView.refresh()),
    models: new ModelManager(client, () => modelsView.refresh()),
    sketchLibs: new SketchLibManager(client, () => appLibsView.refresh()),
    system: new SystemManager(client, output),
    monitor: new SerialMonitor(client, (text) => {
      if (plotterSource === "serial") {
        plotterFeeder.feed(text);
      }
    }),
    intellisense,
  };
  context.subscriptions.push(ready.monitor);

  // The probe already fetched the version (it hits /v1/version), so reuse it
  // instead of a second round-trip.
  statusBar.setConnected(version.version, daemon.baseUrl);

  // Bootstrap the apps index straight from the SSE: connecting emits a full
  // snapshot (apps + examples) which populates the registry via applyStatus — no
  // separate startup `GET /apps` scan. The active-editor app then resolves as the
  // snapshot lands, and the Examples view projects off the same data.
  subscribeStatusEvents(client);
  reconnectAttempts = 0;
  cancelReconnect();
  return ready;
}

/**
 * While the daemon is unreachable, re-probe in the background so a still-booting
 * board connects on its own — no manual Reconnect needed. Bounded (gives up after
 * ~1 minute) and self-cancelling on success. This polls liveness only, never the
 * apps list, so it doesn't add load once connected.
 */
function scheduleReconnect(): void {
  if (reconnectTimer || ready || reconnectAttempts >= RECONNECT_MAX_ATTEMPTS) {
    return;
  }
  reconnectTimer = setTimeout(() => {
    reconnectTimer = undefined;
    reconnectAttempts++;
    // ensureReady() re-probes; on success it clears the counter (and this loop),
    // on failure its catch reschedules the next attempt.
    void ensureReady();
  }, RECONNECT_DELAY_MS);
}

/** Stop any pending background reconnect (on success or manual reconnect). */
function cancelReconnect(): void {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = undefined;
  }
}

/** Long-lived `/apps/events` subscription with reconnect-and-resync. */
function subscribeStatusEvents(client: AppLabClient): void {
  statusAbort?.abort();
  const ctrl = new AbortController();
  statusAbort = ctrl;

  // On connect the daemon emits one `app` event per app (initial snapshot), then
  // streams changes. Each event upserts the registry row in place — no re-listing
  // — and dependent views debounce the resulting re-renders, so the snapshot burst
  // costs nothing beyond the one scan the daemon already did to produce it.
  const run = async () => {
    while (!ctrl.signal.aborted) {
      try {
        await client.appStatusEvents((app) => registry.applyStatus(app), ctrl.signal);
      } catch {
        // fall through to backoff
      }
      if (ctrl.signal.aborted) {
        return;
      }
      // The stream dropped: events may have been missed, and an upsert can't
      // reflect a deletion that happened while we were away — re-list (unfiltered,
      // atomic replace) to resync before the next reconnect re-emits the snapshot.
      void registry.refresh();
      await new Promise((r) => setTimeout(r, 3000));
    }
  };
  void run();
}

/** Run `fn` once connected, surfacing errors as notifications. */
async function withReady<T>(fn: (d: Ready) => Promise<T> | T): Promise<T | undefined> {
  const d = await ensureReady();
  if (!d) {
    return undefined;
  }
  try {
    return await fn(d);
  } catch (err) {
    vscode.window.showErrorMessage(vscode.l10n.t("Error: {0}", asMessage(err)));
    output.appendLine(`[error] ${asMessage(err)}`);
    return undefined;
  }
}

/** Resolve the target app from a tree-node arg, else the active app. */
function appFrom(arg: unknown): AppInfo | undefined {
  if (arg && typeof arg === "object" && "app" in arg) {
    return (arg as { app: AppInfo }).app;
  }
  return activeTracker.current;
}

function registerCommands(ctx: vscode.ExtensionContext) {
  const reg = (id: string, handler: (...args: unknown[]) => unknown) =>
    ctx.subscriptions.push(vscode.commands.registerCommand(id, handler));

  // System / daemon
  reg("appLab.showVersion", () => withReady((d) => d.system.showVersion()));
  reg("appLab.reconnect", async () => {
    // Re-probe the (systemd-managed) daemon and re-wire the client.
    statusAbort?.abort();
    cancelReconnect();
    reconnectAttempts = 0;
    ready = undefined;
    readyPromise = undefined;
    await ensureReady();
    refreshAll();
  });
  reg("appLab.showConfig", () => withReady((d) => d.system.showConfig()));
  reg("appLab.addProperty", () => withReady((d) => d.system.addProperty()));
  reg("appLab.editProperty", () => withReady((d) => d.system.editProperty()));
  reg("appLab.deleteProperty", () => withReady((d) => d.system.deleteProperty()));
  reg("appLab.checkUpdate", () => withReady((d) => d.system.checkUpdate()));
  reg("appLab.applyUpdate", () => withReady((d) => d.system.applyUpdate()));
  reg("appLab.showResources", () => withReady((d) => d.system.showResources()));
  reg("appLab.system.init", () => withReady((d) => d.system.init()));
  reg("appLab.cleanup", () => withReady((d) => d.system.cleanup()));
  reg("appLab.system.networkMode", () => withReady((d) => d.system.networkMode()));
  reg("appLab.system.keyboard", () => withReady((d) => d.system.keyboard()));
  reg("appLab.system.setName", () => withReady((d) => d.system.setName()));
  reg("appLab.installAiAssistant", () => installAiAssistants(ctx));

  // Apps
  reg("appLab.refreshApps", () => void registry.refresh());
  reg("appLab.newApp", () => withReady((d) => d.apps.create()));
  reg("appLab.importApp", () => withReady((d) => d.apps.import()));
  reg("appLab.app.start", (arg) => withReady((d) => withApp(arg, (a) => d.apps.run(a))));
  reg("appLab.app.stop", (arg) => withReady((d) => withApp(arg, (a) => d.apps.stop(a))));
  reg("appLab.app.restart", (arg) => withReady((d) => withApp(arg, (a) => d.apps.restart(a))));
  reg("appLab.app.destroy", (arg) => withReady((d) => withApp(arg, (a) => d.apps.destroy(a))));
  reg("appLab.app.logs", (arg) => withReady((d) => withApp(arg, (a) => d.apps.showLogs(a))));
  reg("appLab.app.export", (arg) => withReady((d) => withApp(arg, (a) => d.apps.export(a))));
  reg("appLab.app.clone", (arg) => withReady((d) => withApp(arg, (a) => d.apps.clone(a))));
  reg("appLab.app.rename", (arg) => withReady((d) => withApp(arg, (a) => d.apps.rename(a))));
  reg("appLab.app.edit", (arg) => withReady((d) => withApp(arg, (a) => d.apps.edit(a))));
  reg("appLab.app.openExposedPort", (arg) => withReady((d) => withApp(arg, (a) => d.apps.openExposedPort(a))));
  reg("appLab.app.revealInExplorer", (arg) => withReady((d) => withApp(arg, (a) => d.apps.revealInExplorer(a))));
  // Row click: only reveal (and add the folder) on a double-click; a single
  // click just selects the app.
  reg("appLab.app.reveal", (arg) => {
    const app = appFrom(arg);
    if (!app) {
      return;
    }
    const now = Date.now();
    if (lastAppClick && lastAppClick.id === app.id && now - lastAppClick.time < 500) {
      lastAppClick = undefined;
      return withReady((d) => d.apps.revealInExplorer(app));
    }
    lastAppClick = { id: app.id, time: now };
  });
  reg("appLab.app.cleanCache", (arg) => withReady((d) => withApp(arg, (a) => d.apps.cleanCache(a))));
  reg("appLab.setDefaultApp", (arg) => withReady((d) => withApp(arg, (a) => d.apps.setDefault(a))));
  reg("appLab.getDefaultApp", () =>
    withReady(async (d) => {
      // The default app is the one flagged `default: true` in the app list —
      // there is no "default" property key.
      const res = await d.client.listApps({ filter: "apps" });
      const def = res.apps?.find((a) => a.default);
      vscode.window.showInformationMessage(
        def ? vscode.l10n.t("Default app: {0}", def.name) : vscode.l10n.t("No default app set."),
      );
    }),
  );

  // Bricks
  reg("appLab.refreshBricks", () => bricksView.refresh());
  reg("appLab.app.refreshBricks", () => appBricksView.refresh());
  reg("appLab.app.addBrick", (arg) =>
    withReady((d) => {
      const brickId = arg && typeof arg === "object" && "brick" in arg
        ? (arg as { brick: { id: string } }).brick.id
        : undefined;
      const app = appFrom(arg);
      if (!app) {
        return noActiveApp();
      }
      return d.bricks.addToApp(app, brickId);
    }),
  );
  reg("appLab.brick.configure", (arg) => withReady((d) => withAppBrick(arg, (a, b) => d.bricks.configure(a, b))));
  reg("appLab.brick.remove", (arg) => withReady((d) => withAppBrick(arg, (a, b) => d.bricks.remove(a, b))));
  reg("appLab.brick.rename", (arg) => withReady((d) => withAppBrick(arg, (a, b) => d.bricks.rename(a, b))));
  reg("appLab.brick.showDetails", (arg) =>
    withReady((d) => {
      const id = brickIdFrom(arg);
      return id ? d.bricks.showDetails(id) : undefined;
    }),
  );

  // Models
  reg("appLab.refreshModels", () => modelsView.refresh());
  reg("appLab.model.import", () => withReady((d) => d.models.importEi()));
  reg("appLab.model.delete", (arg) => withReady((d) => withModel(arg, (m) => d.models.delete(m))));
  reg("appLab.model.showDetails", (arg) => withReady((d) => withModel(arg, (m) => d.models.showDetails(m))));

  // Sketch / MCU libraries
  reg("appLab.app.addSketchLib", (arg) =>
    withReady((d) => withApp(arg, (a) => d.sketchLibs.add(a))),
  );
  reg("appLab.app.refreshSketchLibs", () => appLibsView.refresh());
  // Reveal the active-app views wherever the user has docked them (Explorer by
  // default, or the secondary side bar if moved). The `.focus` command is the one
  // VS Code auto-generates for a contributed view.
  reg("appLab.showAppBricks", () => vscode.commands.executeCommand("appLab.appBricks.focus"));
  reg("appLab.showAppLibs", () => vscode.commands.executeCommand("appLab.appLibs.focus"));
  reg("appLab.sketchLib.remove", (arg) => withReady((d) => withAppLib(arg, (a, l) => d.sketchLibs.remove(a, l))));

  // Monitor
  reg("appLab.openMonitor", (arg) => withReady((d) => d.monitor.open(appFrom(arg))));
  reg("appLab.setMonitorLineEnding", () => withReady((d) => d.monitor.setLineEnding()));
  reg("appLab.saveMonitorLog", () => withReady((d) => d.monitor.saveLog()));

  // Plotter — charts `>`-prefixed telemetry from the source the user picks.
  reg("appLab.openPlotter", (arg) => withReady((d) => openPlotter(d, appFrom(arg))));

  // IntelliSense / Python
  reg("appLab.configureIntelliSense", (arg) =>
    withReady((d) => withApp(arg, (a) => d.intellisense.configure(a))),
  );
  reg("appLab.python.toggleFastReload", () => fastReload.toggle());
}

/**
 * Open the serial plotter, asking the user which stream to chart. The choice
 * sets `plotterSource` (which gates the two feed callbacks) and starts the
 * matching stream so data flows even if it wasn't already open.
 */
async function openPlotter(d: Ready, app: AppInfo | undefined): Promise<void> {
  const pick = await vscode.window.showQuickPick(
    [
      { label: vscode.l10n.t("Serial Monitor"), value: "serial" as const },
      { label: vscode.l10n.t("Python output"), value: "python" as const },
    ],
    { title: vscode.l10n.t("Plot data from…") },
  );
  if (!pick) {
    return;
  }
  if (pick.value === "python" && !app) {
    noActiveApp();
    return;
  }
  plotterSource = pick.value;
  plotterFeeder.reset();
  // Title the panel after the chosen source — the plotter is no longer
  // serial-only, so a fixed "Serial Plotter" would mislabel Python feeds.
  const title =
    pick.value === "serial"
      ? vscode.l10n.t("Serial data plotter")
      : vscode.l10n.t("Python data plotter");
  PlotterPanel.show(context.extensionUri, title);
  PlotterPanel.current()?.notifyConnected();
  // Make sure the chosen source is actually streaming.
  if (pick.value === "serial") {
    await d.monitor.open(app);
  } else if (app) {
    await d.apps.showLogs(app);
  }
}

// ---- node-argument helpers ----

function withApp(arg: unknown, fn: (a: AppInfo) => unknown): unknown {
  const app = appFrom(arg);
  return app ? fn(app) : noActiveApp();
}

function withAppBrick(arg: unknown, fn: (a: AppInfo, b: BrickInstance) => unknown): unknown {
  if (arg && typeof arg === "object" && "app" in arg && "brick" in arg) {
    const node = arg as { app: AppInfo; brick: BrickInstance };
    return fn(node.app, node.brick);
  }
  return undefined;
}

function withAppLib(arg: unknown, fn: (a: AppInfo, l: SketchLibrary) => unknown): unknown {
  if (arg && typeof arg === "object" && "app" in arg && "lib" in arg) {
    const node = arg as { app: AppInfo; lib: SketchLibrary };
    return fn(node.app, node.lib);
  }
  return undefined;
}

function withModel(arg: unknown, fn: (m: ModelInfo) => unknown): unknown {
  if (arg && typeof arg === "object" && "model" in arg) {
    return fn((arg as { model: ModelInfo }).model);
  }
  return undefined;
}

function brickIdFrom(arg: unknown): string | undefined {
  if (arg && typeof arg === "object") {
    if ("brick" in arg) {
      return (arg as { brick: { id: string } }).brick.id;
    }
    if ("id" in arg && typeof (arg as { id: unknown }).id === "string") {
      return (arg as { id: string }).id;
    }
  }
  return undefined;
}

function noActiveApp(): undefined {
  vscode.window.showWarningMessage(
    vscode.l10n.t("No app selected. Open a file inside an app or pick one in the Apps view."),
  );
  return undefined;
}

function asMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}
