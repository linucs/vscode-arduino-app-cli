import * as vscode from "vscode";
import type { AppRegistry } from "./appRegistry";
import { isAppRunning, type AppInfo } from "./api/types";

type Node =
  | { kind: "app"; app: AppInfo }
  | { kind: "message"; label: string };

/**
 * My Apps list: a flat list of the user's installed (non-example) apps on the
 * board, each row showing its emoji icon + name and the running/default state.
 * Unlike examples — read-only blueprints you clone — these are the real apps you
 * start, stop, set as default and delete. Clicking a row reveals its folder (an
 * installed app is an editable workspace folder); the context menu offers
 * Run/Stop, Show Console, Set as Default and Delete.
 *
 * Like {@link ExamplesTreeProvider} this view owns no data: it is a pure
 * projection of the {@link AppRegistry} (the non-example rows of the
 * `/apps/events` snapshot), re-rendering off {@link AppRegistry.onDidChange}.
 */
export class InstalledAppsTreeProvider implements vscode.TreeDataProvider<Node> {
  private readonly emitter = new vscode.EventEmitter<Node | undefined>();
  readonly onDidChangeTreeData = this.emitter.event;

  private rerenderTimer: ReturnType<typeof setTimeout> | undefined;
  private readonly subscription: vscode.Disposable;

  constructor(private readonly registry: AppRegistry) {
    this.subscription = registry.onDidChange(() => this.rerender());
  }

  dispose(): void {
    this.subscription.dispose();
    if (this.rerenderTimer) {
      clearTimeout(this.rerenderTimer);
    }
  }

  /** Coalesce the SSE snapshot burst into a single tree refresh. */
  private rerender(): void {
    if (this.rerenderTimer) {
      return;
    }
    this.rerenderTimer = setTimeout(() => {
      this.rerenderTimer = undefined;
      this.emitter.fire(undefined);
    }, 300);
  }

  getTreeItem(node: Node): vscode.TreeItem {
    if (node.kind === "message") {
      const item = new vscode.TreeItem(node.label, vscode.TreeItemCollapsibleState.None);
      item.contextValue = "message";
      return item;
    }
    const icon = node.app.icon?.trim();
    const label = icon ? `${icon} ${node.app.name}` : node.app.name;
    const item = new vscode.TreeItem(label, vscode.TreeItemCollapsibleState.None);
    // Surface the default app right in the row; otherwise fall back to its description.
    item.description = node.app.default
      ? `★ ${vscode.l10n.t("run on startup")}`
      : node.app.description || undefined;
    item.tooltip = node.app.description
      ? `${node.app.description} — ${node.app.status}`
      : node.app.status;
    item.contextValue = isAppRunning(node.app.status) ? "app:user:running" : "app:user";
    item.command = {
      command: "appLab.app.reveal",
      title: vscode.l10n.t("Reveal in Explorer"),
      arguments: [node],
    };
    return item;
  }

  getChildren(node?: Node): Node[] {
    if (node) {
      return [];
    }
    const apps = this.registry.installedApps();
    if (!apps.length) {
      // Distinguish "snapshot not in yet" from "genuinely none".
      return [
        {
          kind: "message",
          label: this.registry.hasBooted() ? vscode.l10n.t("No apps") : vscode.l10n.t("Loading…"),
        },
      ];
    }
    return apps.map((app) => ({ kind: "app", app }));
  }
}

export type InstalledAppsNode = Node;
