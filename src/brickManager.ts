import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";
import type { AppInfo, BrickConfigVariable, BrickInfo, BrickInstance } from "./api/types";

/** Brick operations: browse the catalog and add/configure/remove on an app. */
export class BrickManager {
  constructor(
    private readonly client: AppLabClient,
    private readonly onChanged: () => void,
  ) {}

  listCatalog(): Promise<BrickInfo[]> {
    return this.client.listBricks();
  }

  /** Create a new local (custom) brick scaffolded under the app's `bricks/` folder. */
  async createLocal(app: AppInfo): Promise<void> {
    const name = await vscode.window.showInputBox({
      title: vscode.l10n.t("New Local Brick"),
      prompt: vscode.l10n.t("Name for the new local brick in {0}", app.name),
      ignoreFocusOut: true,
      validateInput: (v) => (v.trim() ? undefined : vscode.l10n.t("Name is required")),
    });
    const trimmed = name?.trim();
    if (!trimmed) {
      return;
    }
    await this.client.createLocalAppBrick(app.id, trimmed);
    this.onChanged();
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
    const vars = detail?.config_variables ?? [];
    let config: Record<string, string> | undefined;
    if (vars.length) {
      const result = await this.collectConfig(
        vars,
        vscode.l10n.t("Configure brick: {0}", detail?.name ?? id),
        vscode.l10n.t("Add brick"),
      );
      if (!result) {
        return; // cancelled
      }
      // On add, omit blank values so the daemon keeps its defaults.
      const nonEmpty = Object.fromEntries(Object.entries(result).filter(([, v]) => v !== ""));
      config = Object.keys(nonEmpty).length ? nonEmpty : undefined;
    }
    await this.client.addAppBrick(app.id, id, config);
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
    const config = await this.collectConfig(
      vars,
      vscode.l10n.t("Configure brick: {0}", brick.name),
      vscode.l10n.t("Save configuration"),
    );
    if (!config) {
      return;
    }
    await this.client.patchAppBrick(app.id, brick.id, config);
    this.onChanged();
  }

  /**
   * Edit a brick's config variables as a single, revisitable form: a QuickPick
   * lists every field with its current value; picking one opens an input box and
   * returns to the list, so partial input survives and required fields are
   * validated only at commit. Returns a complete `name → value` map (blank for
   * unset), or `undefined` if the user cancelled.
   */
  private async collectConfig(
    vars: BrickConfigVariable[],
    title: string,
    commitLabel: string,
  ): Promise<Record<string, string> | undefined> {
    const values = new Map<string, string>();
    for (const v of vars) {
      if (v.value) {
        values.set(v.name, v.value);
      }
    }
    type Item = vscode.QuickPickItem & { variable?: BrickConfigVariable; commit?: boolean };
    for (;;) {
      const fields: Item[] = vars.map((v) => {
        const cur = values.get(v.name);
        const shown = cur && cur.length ? cur : vscode.l10n.t("(not set)");
        return {
          label: v.name,
          description: v.required ? `${shown}  ${vscode.l10n.t("(required)")}` : shown,
          detail: v.description,
          variable: v,
        };
      });
      const items: Item[] = [
        ...fields,
        { label: "", kind: vscode.QuickPickItemKind.Separator },
        { label: `$(check) ${commitLabel}`, commit: true },
      ];
      const pick = await vscode.window.showQuickPick(items, { title, ignoreFocusOut: true });
      if (!pick) {
        return undefined; // cancelled
      }
      if (pick.commit) {
        const missing = vars
          .filter((v) => v.required && !(values.get(v.name) ?? "").length)
          .map((v) => v.name);
        if (missing.length) {
          vscode.window.showWarningMessage(
            vscode.l10n.t("Fill in required fields first: {0}", missing.join(", ")),
          );
          continue;
        }
        return Object.fromEntries(vars.map((v) => [v.name, values.get(v.name) ?? ""]));
      }
      const v = pick.variable;
      if (!v) {
        continue;
      }
      const input = await vscode.window.showInputBox({
        title,
        prompt: v.description ? `${v.name} — ${v.description}` : v.name,
        value: values.get(v.name) ?? "",
        ignoreFocusOut: true,
      });
      if (input === undefined) {
        continue; // back to the field list
      }
      if (input === "") {
        values.delete(v.name);
      } else {
        values.set(v.name, input);
      }
    }
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
