import * as vscode from "vscode";
import type { AppRegistry } from "./appRegistry";
import { isAppRunning, type AppInfo } from "./api/types";

type Node =
  | { kind: "app"; app: AppInfo }
  | { kind: "message"; label: string };

/**
 * Examples list: a flat list of the example apps the daemon ships, each row
 * showing its emoji icon + name. Examples are read-only templates you browse
 * and clone (your own apps are edited as workspace folders, not listed here —
 * the open folder *is* the app). Clicking a row reveals its folder; the context
 * menu offers Clone / Export / Logs.
 *
 * This view owns no data: it is a pure projection of the {@link AppRegistry}
 * (the example rows of the `/apps/events` snapshot), re-rendering off
 * {@link AppRegistry.onDidChange}. Listing apps is expensive on the board, so
 * keeping the registry as the single SSE-fed source avoids a separate scan.
 */
export class ExamplesTreeProvider implements vscode.TreeDataProvider<Node> {
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
    item.description = node.app.description || undefined;
    item.tooltip = node.app.description
      ? `${node.app.description} — ${node.app.status}`
      : node.app.status;
    item.contextValue = isAppRunning(node.app.status) ? "app:example:running" : "app:example";
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
    const examples = this.registry.examples();
    if (!examples.length) {
      // Distinguish "snapshot not in yet" from "genuinely none".
      return [
        {
          kind: "message",
          label: this.registry.hasBooted() ? vscode.l10n.t("No examples") : vscode.l10n.t("Loading…"),
        },
      ];
    }
    return examples.map((app) => ({ kind: "app", app }));
  }
}

export type ExamplesNode = Node;
