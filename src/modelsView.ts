import * as vscode from "vscode";
import type { ModelInfo } from "./api/types";
import type { DaemonState } from "./appRegistry";

type Node = { kind: "model"; model: ModelInfo } | { kind: "message"; label: string };

/** AI models list. Custom models are deletable; built-ins are not. */
export class ModelsTreeProvider implements vscode.TreeDataProvider<Node> {
  private readonly emitter = new vscode.EventEmitter<Node | undefined>();
  readonly onDidChangeTreeData = this.emitter.event;

  constructor(
    private readonly load: () => Promise<ModelInfo[]>,
    private readonly daemonState: () => DaemonState,
  ) {}

  refresh(): void {
    this.emitter.fire(undefined);
  }

  getTreeItem(node: Node): vscode.TreeItem {
    if (node.kind === "message") {
      return new vscode.TreeItem(node.label, vscode.TreeItemCollapsibleState.None);
    }
    const item = new vscode.TreeItem(node.model.name, vscode.TreeItemCollapsibleState.None);
    item.description = node.model.is_builtin ? vscode.l10n.t("built-in") : undefined;
    item.contextValue = node.model.is_builtin ? "model:builtin" : "model:custom";
    item.iconPath = new vscode.ThemeIcon("circuit-board");
    item.tooltip = node.model.id;
    return item;
  }

  async getChildren(): Promise<Node[]> {
    // Daemon unreachable: render an empty tree so the `viewsWelcome` panel
    // (Reconnect button + hint) shows, instead of a cryptic error row.
    if (this.daemonState() === "disconnected") {
      return [];
    }
    try {
      const models = await this.load();
      return models.length
        ? models.map((model) => ({ kind: "model" as const, model }))
        : [{ kind: "message", label: vscode.l10n.t("No models") }];
    } catch (err) {
      return [{ kind: "message", label: err instanceof Error ? err.message : String(err) }];
    }
  }
}

export type ModelsNode = Node;
