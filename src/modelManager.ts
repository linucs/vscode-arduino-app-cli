import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";
import type { ModelInfo } from "./api/types";

/** AI model operations: list / details / delete / import Edge Impulse project. */
export class ModelManager {
  constructor(
    private readonly client: AppLabClient,
    private readonly onChanged: () => void,
  ) {}

  list(): Promise<ModelInfo[]> {
    return this.client.listModels();
  }

  async importEi(): Promise<void> {
    const projectId = await vscode.window.showInputBox({
      title: vscode.l10n.t("Import Edge Impulse Model"),
      prompt: vscode.l10n.t("Edge Impulse project ID"),
      validateInput: (v) => (v.trim() ? undefined : vscode.l10n.t("Project ID is required")),
    });
    if (!projectId) {
      return;
    }
    await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: vscode.l10n.t("Importing model…") },
      () => this.client.installEiModel(projectId.trim()),
    );
    this.onChanged();
  }

  async delete(model: ModelInfo): Promise<void> {
    const ok = await vscode.window.showWarningMessage(
      vscode.l10n.t('Delete model "{0}"?', model.name),
      { modal: true },
      vscode.l10n.t("Delete"),
    );
    if (!ok) {
      return;
    }
    await this.client.deleteModel(model.id);
    this.onChanged();
  }

  async showDetails(model: ModelInfo): Promise<void> {
    const full = await this.client.getModel(model.id).catch(() => model);
    const doc = await vscode.workspace.openTextDocument({
      content: JSON.stringify(full, null, 2),
      language: "json",
    });
    await vscode.window.showTextDocument(doc, { preview: true });
  }
}
