import * as vscode from "vscode";
import { DaemonManager } from "./daemon";
import { AppLabClient } from "./appLabClient";
import { AppManager } from "./appManager";
import { BrickManager } from "./brickManager";
import { ModelManager } from "./modelManager";
import { SketchLibManager } from "./sketchLibManager";
import { SystemManager } from "./systemManager";
import { SerialMonitor } from "./monitor";
import { AppsTreeProvider, type AppsNode } from "./appsView";
import { BricksTreeProvider } from "./bricksView";
import { ModelsTreeProvider } from "./modelsView";
import { ActiveAppTracker } from "./activeApp";
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
}

let context: vscode.ExtensionContext;
let output: vscode.OutputChannel;
let daemon: DaemonManager;
let activeTracker: ActiveAppTracker;
let statusBar: StatusBar;
let appsView: AppsTreeProvider;
let bricksView: BricksTreeProvider;
let modelsView: ModelsTreeProvider;

let ready: Ready | undefined;
let readyPromise: Promise<Ready | undefined> | undefined;
let statusAbort: AbortController | undefined;
let lastAppClick: { id: string; time: number } | undefined;

export function activate(ctx: vscode.ExtensionContext) {
  context = ctx;
  output = vscode.window.createOutputChannel("Arduino App");
  ctx.subscriptions.push(output);

  daemon = new DaemonManager(output);

  appsView = new AppsTreeProvider(async () => (await ensureReady())!.client);
  bricksView = new BricksTreeProvider(async () => (await ensureReady())!.bricks.listCatalog());
  modelsView = new ModelsTreeProvider(async () => (await ensureReady())!.models.list());

  activeTracker = new ActiveAppTracker((p) => appsView.findByPath(p));
  statusBar = new StatusBar(activeTracker);
  ctx.subscriptions.push(statusBar, activeTracker.register());

  ctx.subscriptions.push(
    vscode.window.createTreeView("appLab.apps", { treeDataProvider: appsView }),
    vscode.window.createTreeView("appLab.bricks", { treeDataProvider: bricksView }),
    vscode.window.createTreeView("appLab.models", { treeDataProvider: modelsView }),
  );

  registerCommands(ctx);

  // Kick off a connection in the background so the views populate and the status
  // bar reflects reality without waiting for the first user action.
  void ensureReady();
}

export function deactivate() {
  statusAbort?.abort();
  ready?.monitor.dispose();
  ready?.apps.dispose();
  // We never own the daemon (it runs under systemd), so there's nothing to stop.
}

function refreshAll(): void {
  appsView.refresh();
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
    vscode.window.showErrorMessage(
      vscode.l10n.t("Cannot reach the Arduino App daemon: {0}", asMessage(err)),
    );
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

  ready = {
    client,
    apps: new AppManager(client, output, refreshAll),
    bricks: new BrickManager(client, refreshAll),
    models: new ModelManager(client, refreshAll),
    sketchLibs: new SketchLibManager(client, refreshAll),
    system: new SystemManager(client, output),
    monitor: new SerialMonitor(client),
  };
  context.subscriptions.push(ready.monitor);

  // The probe already fetched the version (it hits /v1/version), so reuse it
  // instead of a second round-trip.
  statusBar.setConnected(version.version, daemon.baseUrl);

  armStatusEvents(client);
  return ready;
}

/**
 * Open the long-lived `/apps/events` stream, but only once the Apps view has
 * painted its first list. Connecting triggers a full filesystem rescan on the
 * board (the daemon's snapshot), so deferring it keeps that scan from running
 * concurrently with the tree's own `listApps` — two heavy scans at once would
 * make both slower on the UNO Q. A timer backstops the case where the view is
 * never rendered (e.g. the activity bar is collapsed).
 */
function armStatusEvents(client: AppLabClient): void {
  let armed = false;
  const go = () => {
    if (armed) {
      return;
    }
    armed = true;
    disposable.dispose();
    clearTimeout(timer);
    subscribeStatusEvents(client);
  };
  const disposable = appsView.onDidFirstLoad(go);
  const timer = setTimeout(go, 1500);
  if (appsView.hasLoaded()) {
    go();
  }
}

/** Long-lived `/apps/events` subscription with reconnect-and-resync. */
function subscribeStatusEvents(client: AppLabClient): void {
  statusAbort?.abort();
  const ctrl = new AbortController();
  statusAbort = ctrl;

  // On connect the daemon emits one `app` event per app (initial sync), then
  // streams changes. Each event patches the cached row in place — no re-listing
  // — and the tree provider debounces the resulting re-renders, so the snapshot
  // burst costs nothing beyond the one scan the daemon already did to produce it.
  const run = async () => {
    while (!ctrl.signal.aborted) {
      try {
        await client.appStatusEvents((app) => {
          activeTracker.updateStatus(app);
          appsView.applyStatus(app);
        }, ctrl.signal);
      } catch {
        // fall through to backoff
      }
      if (ctrl.signal.aborted) {
        return;
      }
      // The stream dropped: a status may have changed while we were away, and
      // the cache can't be patched from events we missed — re-list to resync.
      appsView.refresh();
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
  if (arg && typeof arg === "object" && "kind" in arg && (arg as AppsNode).kind === "app") {
    return (arg as Extract<AppsNode, { kind: "app" }>).app;
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
  reg("appLab.refreshApps", () => refreshAll());
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
      const v = await d.client.getProperty("default").catch(() => undefined);
      vscode.window.showInformationMessage(
        v ? vscode.l10n.t("Default app: {0}", String(v)) : vscode.l10n.t("No default app set."),
      );
    }),
  );

  // Bricks
  reg("appLab.refreshBricks", () => bricksView.refresh());
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
  reg("appLab.app.refreshSketchLibs", () => appsView.refresh());
  reg("appLab.sketchLib.remove", (arg) => withReady((d) => withAppLib(arg, (a, l) => d.sketchLibs.remove(a, l))));

  // Monitor
  reg("appLab.openMonitor", (arg) => withReady((d) => d.monitor.open(appFrom(arg))));
  reg("appLab.setMonitorLineEnding", () => withReady((d) => d.monitor.setLineEnding()));
  reg("appLab.saveMonitorLog", () => withReady((d) => d.monitor.saveLog()));

  // IntelliSense / Python (Phase 3 — placeholders for now)
  reg("appLab.configureIntelliSense", () => notImplemented("C++ IntelliSense"));
  reg("appLab.python.createVenv", () => notImplemented("Python environment setup"));
  reg("appLab.python.setupStubs", () => notImplemented("Arduino Python stubs"));
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

function notImplemented(feature: string): void {
  vscode.window.showInformationMessage(
    vscode.l10n.t("{0} is coming in a later release.", feature),
  );
}

function asMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}
