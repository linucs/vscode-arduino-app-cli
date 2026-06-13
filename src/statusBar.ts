import * as vscode from "vscode";
import type { ActiveAppTracker } from "./activeApp";
import { isAppRunning } from "./api/types";

/**
 * Left-aligned status bar items mirroring App Lab's prominent controls:
 *  - the current app with a Run/Stop toggle (the primary action), plus Restart
 *    (when running) and Logs;
 *  - the daemon connection + CLI version.
 * (The serial-monitor line-ending item lives in monitor.ts.)
 */
export class StatusBar implements vscode.Disposable {
  private readonly appItem: vscode.StatusBarItem;
  private readonly restartItem: vscode.StatusBarItem;
  private readonly logsItem: vscode.StatusBarItem;
  private readonly connItem: vscode.StatusBarItem;

  constructor(private readonly active: ActiveAppTracker) {
    // Priorities descend left-to-right: toggle, restart, logs, then connection.
    this.appItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    this.restartItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 99.7);
    this.logsItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 99.4);
    this.connItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 99);
    this.restartItem.text = "$(debug-restart)";
    this.restartItem.command = "appLab.app.restart";
    this.logsItem.text = "$(output)";
    this.logsItem.command = "appLab.app.logs";
    this.connItem.command = "appLab.showVersion";
    this.active.onDidChange(() => this.renderApp());
    this.renderApp();
    this.setDisconnected();
  }

  /** Update the connection item once a daemon version is known. */
  setConnected(version: string, baseUrl: string): void {
    this.connItem.text = `$(circuit-board) Arduino App ${version}`;
    this.connItem.tooltip = vscode.l10n.t("Connected to {0}", baseUrl);
    this.connItem.backgroundColor = undefined;
    this.connItem.show();
  }

  setDisconnected(): void {
    this.connItem.text = "$(debug-disconnect) Arduino App";
    this.connItem.tooltip = vscode.l10n.t("Not connected — click to reconnect");
    this.connItem.backgroundColor = new vscode.ThemeColor("statusBarItem.warningBackground");
    this.connItem.show();
  }

  private renderApp(): void {
    const app = this.active.current;
    if (!app) {
      this.appItem.hide();
      this.restartItem.hide();
      this.logsItem.hide();
      return;
    }
    const running = isAppRunning(app.status);
    this.appItem.text = `${running ? "$(debug-stop)" : "$(run)"} ${app.name}`;
    this.appItem.tooltip = running
      ? vscode.l10n.t("Stop {0}", app.name)
      : vscode.l10n.t("Run {0} (compile, flash & start)", app.name);
    this.appItem.command = running ? "appLab.app.stop" : "appLab.app.start";
    this.appItem.show();

    // Restart only makes sense for a running app; Logs are always useful.
    this.restartItem.tooltip = vscode.l10n.t("Restart {0}", app.name);
    this.logsItem.tooltip = vscode.l10n.t("Show logs for {0}", app.name);
    if (running) {
      this.restartItem.show();
    } else {
      this.restartItem.hide();
    }
    this.logsItem.show();
  }

  dispose(): void {
    this.appItem.dispose();
    this.restartItem.dispose();
    this.logsItem.dispose();
    this.connItem.dispose();
  }
}
