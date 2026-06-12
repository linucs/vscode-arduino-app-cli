import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";
import type { AppInfo, BrickInfo, BrickInstance } from "./api/types";

/** Brick operations: browse the catalog and add/configure/remove on an app. */
export class BrickManager {
  constructor(
    private readonly client: AppLabClient,
    private readonly onChanged: () => void,
  ) {}

  listCatalog(): Promise<BrickInfo[]> {
    return this.client.listBricks();
  }

  /** Add a brick to the given app (or prompt to pick one from the catalog). */
  async addToApp(app: AppInfo, brickId?: string): Promise<void> {
    let id = brickId;
    if (!id) {
      const catalog = await this.client.listBricks();
      const pick = await vscode.window.showQuickPick(
        catalog.map((b) => ({ label: b.name, description: b.id, detail: b.description, id: b.id })),
        { title: vscode.l10n.t("Add Brick to {0}", app.name), matchOnDescription: true },
      );
      if (!pick) {
        return;
      }
      id = pick.id;
    }
    const detail = await this.client.getBrick(id).catch(() => undefined);
    const config: Record<string, string> = {};
    for (const v of detail?.config_variables ?? []) {
      const value = await vscode.window.showInputBox({
        title: vscode.l10n.t("Configure brick: {0}", detail?.name ?? id),
        prompt: v.description ? `${v.name} — ${v.description}` : v.name,
        value: v.value ?? "",
        ignoreFocusOut: true,
      });
      if (value === undefined) {
        return; // cancelled
      }
      if (value !== "") {
        config[v.name] = value;
      }
    }
    await this.client.addAppBrick(app.id, id, Object.keys(config).length ? config : undefined);
    this.onChanged();
  }

  async configure(app: AppInfo, brick: BrickInstance): Promise<void> {
    const vars =
      brick.config_variables ??
      (await this.client.getBrick(brick.id).catch(() => undefined))?.config_variables ??
      [];
    if (!vars.length) {
      vscode.window.showInformationMessage(vscode.l10n.t("This brick has no configurable variables."));
      return;
    }
    const config: Record<string, string> = {};
    for (const v of vars) {
      const value = await vscode.window.showInputBox({
        title: vscode.l10n.t("Configure brick: {0}", brick.name),
        prompt: v.description ? `${v.name} — ${v.description}` : v.name,
        value: v.value ?? "",
        ignoreFocusOut: true,
      });
      if (value === undefined) {
        return;
      }
      config[v.name] = value;
    }
    await this.client.patchAppBrick(app.id, brick.id, config);
    this.onChanged();
  }

  async remove(app: AppInfo, brick: BrickInstance): Promise<void> {
    const ok = await vscode.window.showWarningMessage(
      vscode.l10n.t('Remove brick "{0}" from {1}?', brick.name, app.name),
      { modal: true },
      vscode.l10n.t("Remove"),
    );
    if (!ok) {
      return;
    }
    await this.client.deleteAppBrick(app.id, brick.id);
    this.onChanged();
  }

  async rename(app: AppInfo, brick: BrickInstance): Promise<void> {
    const name = await vscode.window.showInputBox({
      title: vscode.l10n.t("Rename Brick"),
      value: brick.name,
    });
    if (!name || name === brick.name) {
      return;
    }
    await this.client.renameAppBrick(app.id, brick.id, name);
    this.onChanged();
  }

  async showDetails(brickId: string): Promise<void> {
    const brick = await this.client.getBrick(brickId);
    const md = new vscode.MarkdownString(
      `## ${brick.name}\n\n${brick.description ?? ""}\n\n${brick.readme ?? ""}`,
    );
    const doc = await vscode.workspace.openTextDocument({ content: md.value, language: "markdown" });
    await vscode.window.showTextDocument(doc, { preview: true });
  }
}
