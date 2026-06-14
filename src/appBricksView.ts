import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";
import type { AppInfo, BrickInstance, SketchLibrary } from "./api/types";

/** Which kind of attachment a tree lists for the active app. */
export type AppItemKind = "bricks" | "libs";

type Node =
  | { kind: "brick"; app: AppInfo; brick: BrickInstance }
  | { kind: "lib"; app: AppInfo; lib: SketchLibrary }
  | { kind: "message"; label: string };

/**
 * Bricks **or** Libraries for the **active app** — the app that owns the active
 * editor file. One instance drives the Bricks view, another the Libraries view;
 * the section is fixed per instance so each is its own folder-centric sidebar.
 *
 * The chosen items (bricks or sketch libraries attached to the active app) are
 * listed lazily from the daemon. Re-renders when the active app changes (not on
 * every status tick) and on manual refresh.
 */
export class AppItemsTreeProvider implements vscode.TreeDataProvider<Node> {
  private readonly emitter = new vscode.EventEmitter<Node | undefined>();
  readonly onDidChangeTreeData = this.emitter.event;

  /** The app id last rendered, so editor churn doesn't trigger needless re-lists. */
  private lastAppId: string | undefined;

  constructor(
    private readonly section: AppItemKind,
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
    if (node) {
      return [];
    }
    const app = this.getActiveApp();
    if (!app) {
      return [{ kind: "message", label: vscode.l10n.t("Open a file inside an app.") }];
    }
    try {
      const client = await this.client();
      if (this.section === "bricks") {
        const bricks = await client.listAppBricks(app.id);
        return bricks.length
          ? bricks.map((brick) => ({ kind: "brick", app, brick }))
          : [{ kind: "message", label: vscode.l10n.t("No bricks") }];
      }
      const libs = await client.getSketchLibs(app.id);
      return libs.length
        ? libs.map((lib) => ({ kind: "lib", app, lib }))
        : [{ kind: "message", label: vscode.l10n.t("No libraries") }];
    } catch (err) {
      return [{ kind: "message", label: err instanceof Error ? err.message : String(err) }];
    }
  }
}

export type AppItemsNode = Node;
