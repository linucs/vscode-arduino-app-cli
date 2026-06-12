import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";
import { isAppRunning, type AppInfo, type BrokenAppInfo } from "./api/types";

type Group = "myapps" | "examples";

type Node =
  | { kind: "group"; group: Group; label: string }
  | { kind: "app"; app: AppInfo; example: boolean }
  | { kind: "message"; label: string };

/** A loaded group: its apps plus any apps the daemon flagged as broken. */
interface GroupData {
  apps: AppInfo[];
  broken: BrokenAppInfo[];
}

/**
 * Apps tree: two groups (My Apps / Examples), each listing its apps as leaf
 * rows. An app row shows its emoji icon + name and its description; clicking it
 * reveals the app's folder in the Explorer. Bricks and sketch libraries are NOT
 * shown here — they're managed from the app's context menu / editor toolbar.
 *
 * Listing an app group is expensive on the board (the daemon rescans the
 * filesystem and parses every app.yaml/README on each `GET /v1/apps`), so each
 * group is listed **once** and cached. Live status changes from the
 * `/apps/events` SSE are applied to the cache via {@link applyStatus} and
 * re-rendered without hitting the network; only a structural change (create,
 * delete, manual refresh) clears the cache via {@link refresh}.
 */
export class AppsTreeProvider implements vscode.TreeDataProvider<Node> {
  private readonly emitter = new vscode.EventEmitter<Node | undefined>();
  readonly onDidChangeTreeData = this.emitter.event;

  /** Fires after the first group finishes loading, so callers can defer work. */
  private readonly firstLoad = new vscode.EventEmitter<void>();
  readonly onDidFirstLoad = this.firstLoad.event;
  private loaded = false;

  /** Per-group cache; absent until the group is first expanded/loaded. */
  private readonly cache = new Map<Group, GroupData>();

  /** Latest apps seen, keyed by filesystem path (for active-app resolution). */
  private readonly byPath = new Map<string, AppInfo>();

  /** Debounce coalesces the SSE snapshot burst into a single re-render. */
  private rerenderTimer: ReturnType<typeof setTimeout> | undefined;

  constructor(private readonly client: () => Promise<AppLabClient>) {}

  /** Whether at least one group has been listed (used to arm the status stream). */
  hasLoaded(): boolean {
    return this.loaded;
  }

  /** Hard refresh: drop the cache so the next render re-lists from the daemon. */
  refresh(node?: Node): void {
    if (!node) {
      this.cache.clear();
      this.byPath.clear();
    }
    this.emitter.fire(node);
  }

  /** Re-render from the cache without re-listing (cheap; no network). */
  private rerender(): void {
    if (this.rerenderTimer) {
      return;
    }
    this.rerenderTimer = setTimeout(() => {
      this.rerenderTimer = undefined;
      this.emitter.fire(undefined);
    }, 300);
  }

  findByPath(p: string): AppInfo | undefined {
    return this.byPath.get(p);
  }

  /**
   * Apply a live status update (one `app` event from the SSE) to the cached
   * lists, re-rendering the affected rows from memory. Apps not yet cached are
   * ignored — they'll be listed in full when their group is first expanded.
   */
  applyStatus(app: AppInfo): void {
    let hit = false;
    for (const data of this.cache.values()) {
      const idx = data.apps.findIndex((a) => a.id === app.id);
      if (idx !== -1) {
        // Merge so fields the event omits (path, description) survive.
        const merged = { ...data.apps[idx], ...app };
        data.apps[idx] = merged;
        if (merged.path) {
          this.byPath.set(merged.path, merged);
        }
        hit = true;
      }
    }
    if (hit) {
      this.rerender();
    }
  }

  getTreeItem(node: Node): vscode.TreeItem {
    switch (node.kind) {
      case "group": {
        // Examples can be numerous and each costs a status check — keep it
        // collapsed so startup only lists My Apps.
        const state =
          node.group === "examples"
            ? vscode.TreeItemCollapsibleState.Collapsed
            : vscode.TreeItemCollapsibleState.Expanded;
        const item = new vscode.TreeItem(node.label, state);
        item.contextValue = `appgroup:${node.group}`;
        return item;
      }
      case "app": {
        const icon = node.app.icon?.trim();
        const label = icon ? `${icon} ${node.app.name}` : node.app.name;
        const item = new vscode.TreeItem(label, vscode.TreeItemCollapsibleState.None);
        item.description = node.app.description || undefined;
        item.tooltip = node.app.description
          ? `${node.app.description} — ${node.app.status}`
          : node.app.status;
        // Normalise to running/stopped so Run/Stop gate correctly regardless of
        // the exact status (stopped, failed, uninitialized, omitted, …).
        item.contextValue = node.example
          ? "app:example"
          : isAppRunning(node.app.status)
            ? "app:running"
            : "app:stopped";
        // The default app gets a star to mark it.
        if (node.app.default) {
          item.iconPath = new vscode.ThemeIcon("star-full", new vscode.ThemeColor("charts.yellow"));
        }
        // Double-click adds the app's folder to the workspace and reveals it.
        item.command = {
          command: "appLab.app.reveal",
          title: vscode.l10n.t("Reveal in Explorer"),
          arguments: [node],
        };
        return item;
      }
      case "message": {
        const item = new vscode.TreeItem(node.label, vscode.TreeItemCollapsibleState.None);
        item.contextValue = "message";
        return item;
      }
    }
  }

  async getChildren(node?: Node): Promise<Node[]> {
    try {
      if (!node) {
        return [
          { kind: "group", group: "myapps", label: vscode.l10n.t("My Apps") },
          { kind: "group", group: "examples", label: vscode.l10n.t("Examples") },
        ];
      }
      if (node.kind === "group") {
        const data = await this.loadGroup(node.group);
        const nodes: Node[] = data.apps.map((app) => ({
          kind: "app",
          app,
          example: node.group === "examples",
        }));
        if (node.group === "myapps") {
          for (const b of data.broken) {
            nodes.push({ kind: "message", label: `⚠ ${b.name ?? b.id}: ${b.error}` });
          }
        }
        return nodes.length ? nodes : [{ kind: "message", label: vscode.l10n.t("No apps") }];
      }
      return [];
    } catch (err) {
      return [{ kind: "message", label: err instanceof Error ? err.message : String(err) }];
    }
  }

  /** List a group from the daemon once, then serve from the cache. */
  private async loadGroup(group: Group): Promise<GroupData> {
    const cached = this.cache.get(group);
    if (cached) {
      return cached;
    }
    const client = await this.client();
    const res = await client.listApps({ filter: group === "examples" ? "examples" : "apps" });
    const data: GroupData = { apps: res.apps ?? [], broken: res.broken_apps ?? [] };
    for (const a of data.apps) {
      if (a.path) {
        this.byPath.set(a.path, a);
      }
    }
    this.cache.set(group, data);
    if (!this.loaded) {
      this.loaded = true;
      this.firstLoad.fire();
    }
    return data;
  }
}

export type AppsNode = Node;
