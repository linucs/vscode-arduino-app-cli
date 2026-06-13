import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";
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
 * Listing examples is expensive on the board (the daemon rescans and parses
 * every example), so the list is fetched **once** and cached; live status
 * changes from the `/apps/events` SSE patch the cache via {@link applyStatus}.
 * Example paths are also handed to the {@link AppRegistry} so the active-app
 * toolbar resolves when an example folder is opened.
 */
export class ExamplesTreeProvider implements vscode.TreeDataProvider<Node> {
  private readonly emitter = new vscode.EventEmitter<Node | undefined>();
  readonly onDidChangeTreeData = this.emitter.event;

  private cache: AppInfo[] | undefined;
  private rerenderTimer: ReturnType<typeof setTimeout> | undefined;

  constructor(
    private readonly client: () => Promise<AppLabClient>,
    private readonly register: (apps: AppInfo[]) => void,
  ) {}

  /** Hard refresh: drop the cache so the next render re-lists from the daemon. */
  refresh(): void {
    this.cache = undefined;
    this.emitter.fire(undefined);
  }

  /** Apply a live status update (one `app` event from the SSE) to the cache. */
  applyStatus(app: AppInfo): void {
    if (!this.cache) {
      return;
    }
    const idx = this.cache.findIndex((a) => a.id === app.id);
    if (idx !== -1) {
      this.cache[idx] = { ...this.cache[idx], ...app };
      this.rerender();
    }
  }

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

  async getChildren(node?: Node): Promise<Node[]> {
    if (node) {
      return [];
    }
    try {
      const apps = await this.loadExamples();
      return apps.length
        ? apps.map((app) => ({ kind: "app", app }))
        : [{ kind: "message", label: vscode.l10n.t("No examples") }];
    } catch (err) {
      return [{ kind: "message", label: err instanceof Error ? err.message : String(err) }];
    }
  }

  /** List the examples from the daemon once, then serve from the cache. */
  private async loadExamples(): Promise<AppInfo[]> {
    if (this.cache) {
      return this.cache;
    }
    const client = await this.client();
    const res = await client.listApps({ filter: "examples" });
    this.cache = res.apps ?? [];
    this.register(this.cache);
    return this.cache;
  }
}

export type ExamplesNode = Node;
