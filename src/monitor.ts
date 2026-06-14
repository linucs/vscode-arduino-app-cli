import * as vscode from "vscode";
import type { AppLabClient, MonitorSocket } from "./appLabClient";
import type { AppInfo } from "./api/types";

type LineEnding = "none" | "lf" | "cr" | "crlf";
const EOL: Record<LineEnding, string> = { none: "", lf: "\n", cr: "\r", crlf: "\r\n" };
const EOL_LABEL: Record<LineEnding, string> = { none: "No line ending", lf: "LF", cr: "CR", crlf: "CRLF" };

/**
 * Serial monitor as a VS Code Pseudoterminal backed by the daemon's WebSocket.
 * Bytes from the MCU are written to the terminal; typed input is line-buffered
 * and sent on Enter with the configured line ending. Ported from the sibling's
 * gRPC-duplex `serialMonitor.ts` to a `ws` socket.
 */
export class SerialMonitor implements vscode.Disposable {
  private terminal: vscode.Terminal | undefined;
  private socket: MonitorSocket | undefined;
  private readonly writeEmitter = new vscode.EventEmitter<string>();
  private readonly closeEmitter = new vscode.EventEmitter<void>();
  private lineBuf = "";
  private logBuf: string[] = [];
  private lineEndingStatus: vscode.StatusBarItem;

  constructor(
    private readonly client: AppLabClient,
    /**
     * Optional sink for each decoded serial chunk, used to feed the serial
     * plotter when the user selects "Serial Monitor" as its source.
     */
    private readonly onData?: (text: string) => void,
  ) {
    this.lineEndingStatus = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 98);
    this.lineEndingStatus.command = "appLab.setMonitorLineEnding";
  }

  private get lineEnding(): LineEnding {
    return vscode.workspace.getConfiguration("appLab").get<LineEnding>("monitor.lineEnding", "lf");
  }

  async open(app?: AppInfo): Promise<void> {
    if (this.terminal) {
      this.terminal.show();
      return;
    }
    const sock = this.client.openMonitor(app?.id);
    this.socket = sock;
    sock.on("open", () => this.writeEmitter.fire(`\x1b[2m[monitor connected]\x1b[0m\r\n`));
    sock.on("data", (chunk: Buffer) => {
      const text = chunk.toString("utf8");
      this.logBuf.push(text);
      this.onData?.(text);
      this.writeEmitter.fire(text.replace(/\n/g, "\r\n"));
    });
    sock.on("error", (err: Error) => this.writeEmitter.fire(`\x1b[31m[error] ${err.message}\x1b[0m\r\n`));
    sock.on("close", () => this.writeEmitter.fire(`\x1b[2m[monitor closed]\x1b[0m\r\n`));

    const pty: vscode.Pseudoterminal = {
      onDidWrite: this.writeEmitter.event,
      onDidClose: this.closeEmitter.event,
      open: () => this.updateStatus(),
      close: () => this.teardown(),
      handleInput: (data: string) => this.handleInput(data),
    };
    this.terminal = vscode.window.createTerminal({
      name: app ? `Serial: ${app.name}` : "Serial Monitor",
      pty,
    });
    this.terminal.show();
    this.lineEndingStatus.show();
  }

  private handleInput(data: string): void {
    // Enter sends the buffered line with the configured ending.
    if (data === "\r") {
      const payload = this.lineBuf + EOL[this.lineEnding];
      this.socket?.send(payload);
      this.writeEmitter.fire("\r\n");
      this.lineBuf = "";
      return;
    }
    if (data === "\x7f") {
      // Backspace
      if (this.lineBuf.length > 0) {
        this.lineBuf = this.lineBuf.slice(0, -1);
        this.writeEmitter.fire("\b \b");
      }
      return;
    }
    this.lineBuf += data;
    this.writeEmitter.fire(data);
  }

  async setLineEnding(): Promise<void> {
    const pick = await vscode.window.showQuickPick(
      (Object.keys(EOL) as LineEnding[]).map((k) => ({ label: EOL_LABEL[k], value: k })),
      { title: vscode.l10n.t("Serial Monitor Line Ending") },
    );
    if (!pick) {
      return;
    }
    await vscode.workspace
      .getConfiguration("appLab")
      .update("monitor.lineEnding", pick.value, vscode.ConfigurationTarget.Global);
    this.updateStatus();
  }

  async saveLog(): Promise<void> {
    if (!this.logBuf.length) {
      vscode.window.showInformationMessage(vscode.l10n.t("Nothing to save yet."));
      return;
    }
    const target = await vscode.window.showSaveDialog({
      title: vscode.l10n.t("Save Serial Monitor Log"),
      filters: { Log: ["log", "txt"] },
    });
    if (!target) {
      return;
    }
    await vscode.workspace.fs.writeFile(target, Buffer.from(this.logBuf.join(""), "utf8"));
  }

  private updateStatus(): void {
    this.lineEndingStatus.text = `$(arrow-down) ${EOL_LABEL[this.lineEnding]}`;
    this.lineEndingStatus.tooltip = vscode.l10n.t("Serial monitor line ending");
  }

  private teardown(): void {
    this.socket?.close();
    this.socket = undefined;
    this.terminal = undefined;
    this.lineBuf = "";
    this.lineEndingStatus.hide();
  }

  dispose(): void {
    this.teardown();
    this.writeEmitter.dispose();
    this.closeEmitter.dispose();
    this.lineEndingStatus.dispose();
  }
}
