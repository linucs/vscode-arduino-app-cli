import * as vscode from "vscode";
import type { BrickInfo } from "./api/types";

type Node = { kind: "brick"; brick: BrickInfo } | { kind: "message"; label: string };

/** Global brick catalog. Adding to an app is done via the row context menu. */
export class BricksTreeProvider implements vscode.TreeDataProvider<Node> {
  private readonly emitter = new vscode.EventEmitter<Node | undefined>();
  readonly onDidChangeTreeData = this.emitter.event;

  constructor(private readonly load: () => Promise<BrickInfo[]>) {}

  refresh(): void {
    this.emitter.fire(undefined);
  }

  getTreeItem(node: Node): vscode.TreeItem {
    if (node.kind === "message") {
      return new vscode.TreeItem(node.label, vscode.TreeItemCollapsibleState.None);
    }
    const item = new vscode.TreeItem(node.brick.name, vscode.TreeItemCollapsibleState.None);
    item.description = node.brick.category;
    item.tooltip = node.brick.description;
    item.contextValue = "catalogBrick";
    item.id = node.brick.id;
    item.iconPath = new vscode.ThemeIcon("package");
    return item;
  }

  async getChildren(): Promise<Node[]> {
    try {
      const bricks = await this.load();
      return bricks.length
        ? bricks.map((brick) => ({ kind: "brick" as const, brick }))
        : [{ kind: "message", label: vscode.l10n.t("No bricks") }];
    } catch (err) {
      return [{ kind: "message", label: err instanceof Error ? err.message : String(err) }];
    }
  }
}

export type BricksNode = Node;
