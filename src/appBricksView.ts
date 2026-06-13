import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";
import type { AppInfo, BrickInstance, SketchLibrary } from "./api/types";

/** The two sub-sections shown for the active app. */
type Section = "bricks" | "libs";

type Node =
  | { kind: "section"; app: AppInfo; section: Section }
  | { kind: "brick"; app: AppInfo; brick: BrickInstance }
  | { kind: "lib"; app: AppInfo; lib: SketchLibrary }
  | { kind: "message"; label: string };

/**
 * Bricks & Libraries for the **active app** — the app that owns the active
 * editor file. Replaces the per-app sections that used to nest under the
 * (now removed) My-Apps tree, so brick/library management stays folder-centric.
 *
 * Two top-level sections (Bricks / Libraries) list what's attached to the
 * active app, loaded lazily from the daemon. Re-renders when the active app
 * changes (not on every status tick) and on manual refresh.
 */
export class AppBricksTreeProvider implements vscode.TreeDataProvider<Node> {
  private readonly emitter = new vscode.EventEmitter<Node | undefined>();
  readonly onDidChangeTreeData = this.emitter.event;

  /** The app id last rendered, so editor churn doesn't trigger needless re-lists. */
  private lastAppId: string | undefined;

  constructor(
    private readonly client: () => Promise<AppLabClient>,
    private readonly getActiveApp: () => AppInfo | undefined,
  ) {}

  /** Hard refresh (e.g. after add/remove). */
  refresh(): void {
    this.emitter.fire(undefined);
  }

  /** Re-render only when the active app actually changed identity. */
  onActiveChanged(): void {
    const id = this.getActiveApp()?.id;
    if (id !== this.lastAppId) {
      this.lastAppId = id;
      this.emitter.fire(undefined);
    }
  }

  getTreeItem(node: Node): vscode.TreeItem {
    switch (node.kind) {
      case "section": {
        const bricks = node.section === "bricks";
        const item = new vscode.TreeItem(
          bricks ? vscode.l10n.t("Bricks") : vscode.l10n.t("Libraries"),
          vscode.TreeItemCollapsibleState.Expanded,
        );
        item.iconPath = new vscode.ThemeIcon(bricks ? "package" : "library");
        item.contextValue = `appsection:${node.section}`;
        return item;
      }
      case "brick": {
        const item = new vscode.TreeItem(node.brick.name, vscode.TreeItemCollapsibleState.None);
        item.description = node.brick.category || undefined;
        item.tooltip = node.brick.model
          ? vscode.l10n.t("Model: {0}", node.brick.model)
          : node.brick.category || undefined;
        item.iconPath = new vscode.ThemeIcon("package");
        item.contextValue = "appBrick";
        return item;
      }
      case "lib": {
        const item = new vscode.TreeItem(node.lib.name, vscode.TreeItemCollapsibleState.None);
        item.description = node.lib.version || undefined;
        item.iconPath = new vscode.ThemeIcon("library");
        item.contextValue = "appLib";
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
    const app = this.getActiveApp();
    try {
      if (!node) {
        if (!app) {
          return [{ kind: "message", label: vscode.l10n.t("Open a file inside an app.") }];
        }
        return [
          { kind: "section", app, section: "bricks" },
          { kind: "section", app, section: "libs" },
        ];
      }
      if (node.kind === "section") {
        return this.loadSection(node);
      }
      return [];
    } catch (err) {
      return [{ kind: "message", label: err instanceof Error ? err.message : String(err) }];
    }
  }

  /** Lazily list the active app's bricks or sketch libraries. */
  private async loadSection(node: Extract<Node, { kind: "section" }>): Promise<Node[]> {
    const client = await this.client();
    if (node.section === "bricks") {
      const bricks = await client.listAppBricks(node.app.id);
      return bricks.length
        ? bricks.map((brick) => ({ kind: "brick", app: node.app, brick }))
        : [{ kind: "message", label: vscode.l10n.t("No bricks") }];
    }
    const libs = await client.getSketchLibs(node.app.id);
    return libs.length
      ? libs.map((lib) => ({ kind: "lib", app: node.app, lib }))
      : [{ kind: "message", label: vscode.l10n.t("No libraries") }];
  }
}

export type AppBricksNode = Node;
