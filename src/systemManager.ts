import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";

/**
 * System & configuration: version, config, properties, updates, resources, and
 * the board/system commands that exist only on the CLI (run via `cli()`).
 */
export class SystemManager {
  constructor(
    private readonly client: AppLabClient,
    private readonly output: vscode.OutputChannel,
  ) {}

  async showVersion(): Promise<void> {
    const v = await this.client.version();
    const action = await vscode.window.showInformationMessage(
      vscode.l10n.t("Arduino App CLI {0}", v.version),
      vscode.l10n.t("Reconnect"),
    );
    if (action) {
      await vscode.commands.executeCommand("appLab.reconnect");
    }
  }

  async showConfig(): Promise<void> {
    const cfg = await this.client.getConfig();
    await this.openJson(cfg, vscode.l10n.t("Arduino App configuration"));
  }

  async addProperty(): Promise<void> {
    const key = await vscode.window.showInputBox({ title: vscode.l10n.t("Add Property"), prompt: vscode.l10n.t("Key") });
    if (!key) {
      return;
    }
    const value = await vscode.window.showInputBox({ title: vscode.l10n.t("Add Property"), prompt: vscode.l10n.t("Value") });
    if (value === undefined) {
      return;
    }
    await this.client.putProperty(key, value);
    vscode.window.showInformationMessage(vscode.l10n.t("Property {0} set.", key));
  }

  async editProperty(): Promise<void> {
    const keys = await this.client.listProperties().catch(() => []);
    const key = await vscode.window.showQuickPick(keys, { title: vscode.l10n.t("Edit Property") });
    if (!key) {
      return;
    }
    const current = await this.client.getProperty(key).catch(() => "");
    const value = await vscode.window.showInputBox({
      title: vscode.l10n.t("Edit Property"),
      prompt: key,
      value: typeof current === "string" ? current : JSON.stringify(current),
    });
    if (value === undefined) {
      return;
    }
    await this.client.putProperty(key, value);
  }

  async deleteProperty(): Promise<void> {
    const keys = await this.client.listProperties().catch(() => []);
    const key = await vscode.window.showQuickPick(keys, { title: vscode.l10n.t("Delete Property") });
    if (!key) {
      return;
    }
    await this.client.deleteProperty(key);
  }

  async checkUpdate(): Promise<void> {
    const info = await this.client.checkUpdate();
    await this.openJson(info, vscode.l10n.t("Available updates"));
  }

  async applyUpdate(): Promise<void> {
    const ok = await vscode.window.showWarningMessage(
      vscode.l10n.t("Apply system update now?"),
      { modal: true },
      vscode.l10n.t("Update"),
    );
    if (!ok) {
      return;
    }
    this.output.show(true);
    await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: vscode.l10n.t("Updating system…"), cancellable: true },
      async (progress, token) => {
        const ctrl = new AbortController();
        token.onCancellationRequested(() => ctrl.abort());
        await this.client.updateEvents(
          {
            onProgress: (p) => progress.report({ message: `${p.name} ${Math.round((p.progress ?? 0) * 100)}%` }),
            onMessage: (m) => this.output.appendLine(m.message),
            onError: (e) => this.output.appendLine(`[error] ${e.message}`),
          },
          ctrl.signal,
        );
        await this.client.applyUpdate();
      },
    );
  }

  async showResources(): Promise<void> {
    const res = await this.client.resources();
    await this.openJson(res, vscode.l10n.t("System resources"));
  }

  // ---- CLI-only board/system commands ----

  async init(): Promise<void> {
    await this.runCli(["system", "init"], vscode.l10n.t("Initializing system…"));
  }

  async cleanup(): Promise<void> {
    await this.runCli(["system", "cleanup"], vscode.l10n.t("Cleaning up disk space…"));
  }

  async networkMode(): Promise<void> {
    const mode = await vscode.window.showQuickPick(["enable", "disable", "status"], {
      title: vscode.l10n.t("Network Mode"),
    });
    if (!mode) {
      return;
    }
    await this.runCli(["system", "network-mode", mode], vscode.l10n.t("Setting network mode…"));
  }

  async keyboard(): Promise<void> {
    const layout = await vscode.window.showInputBox({
      title: vscode.l10n.t("Keyboard Layout"),
      prompt: vscode.l10n.t("Layout (e.g. us, it, de) — leave blank to query"),
    });
    if (layout === undefined) {
      return;
    }
    await this.runCli(
      layout ? ["system", "keyboard", layout] : ["system", "keyboard"],
      vscode.l10n.t("Setting keyboard layout…"),
    );
  }

  async setName(): Promise<void> {
    const name = await vscode.window.showInputBox({ title: vscode.l10n.t("Set Board Name"), prompt: vscode.l10n.t("Name") });
    if (!name) {
      return;
    }
    await this.runCli(["system", "set-name", name], vscode.l10n.t("Setting board name…"));
  }

  private async runCli(args: string[], title: string): Promise<void> {
    this.output.show(true);
    await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title },
      async () => {
        const out = await this.client.cli(args);
        if (out.trim()) {
          this.output.appendLine(out.trim());
        }
      },
    );
  }

  private async openJson(data: unknown, _title: string): Promise<void> {
    const doc = await vscode.workspace.openTextDocument({
      content: JSON.stringify(data, null, 2),
      language: "json",
    });
    await vscode.window.showTextDocument(doc, { preview: true });
  }
}
