import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";
import type { ResourcesSnapshot } from "./api/types";

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
      vscode.l10n.t("Arduino App Studio {0}", v.version),
      vscode.l10n.t("Reconnect"),
    );
    if (action) {
      await vscode.commands.executeCommand("appLab.reconnect");
    }
  }

  async showConfig(): Promise<void> {
    const cfg = await this.client.getConfig();
    await this.openJson(cfg, vscode.l10n.t("Arduino App Studio configuration"));
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

  /**
   * Check for updates and, if any, list the upgradable packages in a modal and
   * offer to apply them in one flow (no separate "apply" step needed).
   */
  async checkUpdate(): Promise<void> {
    const info = await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: vscode.l10n.t("Checking for updates…") },
      () => this.client.checkUpdate(),
    );
    const updates = info?.updates ?? [];
    if (!updates.length) {
      vscode.window.showInformationMessage(vscode.l10n.t("System is up to date."));
      return;
    }
    const detail = updates
      .map((p) =>
        vscode.l10n.t("{0}: {1} → {2}", p.name ?? "?", p.from_version ?? "?", p.to_version ?? "?"),
      )
      .join("\n");
    const ok = await vscode.window.showWarningMessage(
      vscode.l10n.t("{0} package(s) can be updated.", updates.length),
      { modal: true, detail },
      vscode.l10n.t("Update"),
    );
    if (ok) {
      await this.runUpdate();
    }
  }

  /** Apply a system update directly (with its own confirmation). */
  async applyUpdate(): Promise<void> {
    const ok = await vscode.window.showWarningMessage(
      vscode.l10n.t("Apply system update now?"),
      { modal: true },
      vscode.l10n.t("Update"),
    );
    if (ok) {
      await this.runUpdate();
    }
  }

  /** Stream the update process to the output channel with a progress notification. */
  private async runUpdate(): Promise<void> {
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

  /** Show CPU / memory / disk usage in a compact toast (read from the SSE stream). */
  async showResources(): Promise<void> {
    const snap = await this.collectResources();
    const parts: string[] = [];
    if (snap.cpu) {
      const v = snap.cpu.used_percent ?? 0;
      parts.push(`${vscode.l10n.t("CPU")} ${Math.round(v <= 1 ? v * 100 : v)}%`);
    }
    if (snap.mem) {
      parts.push(`${vscode.l10n.t("Memory")} ${usage(snap.mem.used, snap.mem.total)}`);
    }
    if (snap.disk) {
      parts.push(`${vscode.l10n.t("Disk")} ${usage(snap.disk.used, snap.disk.total)}`);
    }
    if (!parts.length) {
      vscode.window.showWarningMessage(vscode.l10n.t("Could not read system resources."));
      return;
    }
    vscode.window.showInformationMessage(parts.join("  ·  "));
  }

  /**
   * Open the resources SSE stream, gather one cpu/mem/disk sample (or whatever
   * arrives within a short window), then abort and return the snapshot.
   */
  private collectResources(): Promise<ResourcesSnapshot> {
    return new Promise((resolve) => {
      const snap: ResourcesSnapshot = {};
      const ctrl = new AbortController();
      let settled = false;
      const finish = (): void => {
        if (settled) {
          return;
        }
        settled = true;
        clearTimeout(timer);
        ctrl.abort();
        resolve(snap);
      };
      const timer = setTimeout(finish, 2500);
      this.client
        .systemResourcesEvents(
          {
            onRaw: (e) => {
              const d = e.data as Record<string, number> | undefined;
              if (!d) {
                return;
              }
              if (e.event === "cpu" || e.event === "stats") {
                snap.cpu = d as unknown as ResourcesSnapshot["cpu"];
              } else if (e.event === "mem") {
                snap.mem = d as unknown as ResourcesSnapshot["mem"];
              } else if (e.event === "disk") {
                snap.disk = d as unknown as ResourcesSnapshot["disk"];
              }
              if (snap.cpu && snap.mem && snap.disk) {
                finish();
              }
            },
            onError: () => finish(),
          },
          ctrl.signal,
        )
        .catch(() => finish());
    });
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
    const custom = vscode.l10n.t("Custom…");
    const items: vscode.QuickPickItem[] = KEYBOARD_LAYOUTS.map((l) => ({
      label: l.label,
      description: l.code,
    }));
    items.push({ label: "", kind: vscode.QuickPickItemKind.Separator }, { label: custom });
    const pick = await vscode.window.showQuickPick(items, {
      title: vscode.l10n.t("Select keyboard layout"),
      matchOnDescription: true,
    });
    if (!pick) {
      return;
    }
    let code: string | undefined;
    if (pick.label === custom) {
      code = (
        await vscode.window.showInputBox({
          title: vscode.l10n.t("Custom keyboard layout"),
          prompt: vscode.l10n.t("Layout code (e.g. us, it, de)"),
          validateInput: (v) => (v.trim() ? undefined : vscode.l10n.t("Layout code is required")),
        })
      )?.trim();
    } else {
      code = pick.description;
    }
    if (!code) {
      return;
    }
    await this.runCli(["system", "keyboard", code], vscode.l10n.t("Setting keyboard layout…"));
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

/**
 * Common keyboard layouts offered in the picker. Labels are intentionally plain
 * (not localized) — they name the layout, not UI chrome — so they need no
 * per-locale translation. A "Custom…" entry covers anything not listed.
 */
const KEYBOARD_LAYOUTS: { label: string; code: string }[] = [
  { label: "English (US)", code: "us" },
  { label: "English (UK)", code: "gb" },
  { label: "Italian", code: "it" },
  { label: "German", code: "de" },
  { label: "French", code: "fr" },
  { label: "Spanish", code: "es" },
  { label: "Portuguese", code: "pt" },
  { label: "Portuguese (Brazil)", code: "br" },
  { label: "Dutch", code: "nl" },
  { label: "Swedish", code: "se" },
  { label: "Norwegian", code: "no" },
  { label: "Danish", code: "dk" },
  { label: "Finnish", code: "fi" },
  { label: "Swiss", code: "ch" },
  { label: "Czech", code: "cz" },
  { label: "Polish", code: "pl" },
  { label: "Hungarian", code: "hu" },
  { label: "Russian", code: "ru" },
  { label: "Turkish", code: "tr" },
  { label: "Japanese", code: "jp" },
  { label: "Korean", code: "kr" },
];

/** "512 MB / 2.0 GB (25%)" — used + total with percentage. */
function usage(used: number, total: number): string {
  const pct = total > 0 ? Math.round((used / total) * 100) : 0;
  return vscode.l10n.t("{0} / {1} ({2}%)", formatBytes(used), formatBytes(total), pct);
}

/** Human-readable bytes (B/KB/MB/GB/TB). */
function formatBytes(n: number): string {
  if (!Number.isFinite(n) || n <= 0) {
    return "0 B";
  }
  const units = ["B", "KB", "MB", "GB", "TB"];
  let v = n;
  let i = 0;
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024;
    i++;
  }
  return `${v >= 10 || i === 0 ? Math.round(v) : v.toFixed(1)} ${units[i]}`;
}
