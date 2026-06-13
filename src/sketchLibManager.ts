import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";
import type { AppInfo, SketchLibrary } from "./api/types";

/** MCU C++ sketch library management (add/remove), backed by arduino-cli. */
export class SketchLibManager {
  constructor(
    private readonly client: AppLabClient,
    private readonly onChanged: () => void,
  ) {}

  /** Search the Arduino catalog and add the chosen library to the app's sketch. */
  async add(app: AppInfo): Promise<void> {
    const search = await vscode.window.showInputBox({
      title: vscode.l10n.t("Add Sketch Library"),
      prompt: vscode.l10n.t("Search the Arduino library catalog"),
    });
    if (search === undefined) {
      return;
    }
    const results = await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: vscode.l10n.t("Searching libraries…") },
      () => this.client.listLibraries({ search: search || undefined, limit: 50 }),
    );
    if (!results.length) {
      vscode.window.showInformationMessage(vscode.l10n.t("No libraries found."));
      return;
    }
    const pick = await vscode.window.showQuickPick(
      results.map((l) => ({
        label: l.name,
        description: l.latest,
        detail: l.sentence,
        lib: l,
      })),
      { title: vscode.l10n.t("Add Sketch Library"), matchOnDescription: true },
    );
    if (!pick) {
      return;
    }
    const ref = await this.pickVersion(pick.lib.name, pick.lib.versions);
    if (!ref) {
      return;
    }
    await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: vscode.l10n.t("Adding {0}…", ref) },
      () => this.client.addSketchLib(app.id, ref, { addDeps: true }),
    );
    this.onChanged();
  }

  private async pickVersion(name: string, versions?: string[]): Promise<string | undefined> {
    if (!versions || versions.length <= 1) {
      return name;
    }
    const pick = await vscode.window.showQuickPick(
      [vscode.l10n.t("Latest"), ...versions],
      { title: vscode.l10n.t("Version for {0}", name) },
    );
    if (!pick) {
      return undefined;
    }
    return pick === vscode.l10n.t("Latest") ? name : `${name}@${pick}`;
  }

  async remove(app: AppInfo, lib: SketchLibrary): Promise<void> {
    const ok = await vscode.window.showWarningMessage(
      vscode.l10n.t('Remove library "{0}" from {1}?', lib.name, app.name),
      { modal: true },
      vscode.l10n.t("Remove"),
    );
    if (!ok) {
      return;
    }
    const ref = lib.version ? `${lib.name}@${lib.version}` : lib.name;
    await this.client.removeSketchLib(app.id, ref, { removeDeps: true });
    this.onChanged();
  }
}
