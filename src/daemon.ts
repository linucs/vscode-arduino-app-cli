import * as vscode from "vscode";
import type { VersionResponse } from "./api/types";

/**
 * Resolves and tracks the connection to the arduino-app-cli daemon.
 *
 * On the Arduino UNO Q the daemon runs as a systemd service on 127.0.0.1:8800.
 * This extension is **connect-only**: it never spawns or stops a daemon — it
 * just probes for the existing one (with retries, to tolerate a momentarily busy
 * daemon) and reports it unreachable otherwise. Managing the daemon's lifecycle
 * is systemd's job, not ours.
 */
export class DaemonManager {
  constructor(private readonly output: vscode.OutputChannel) {}

  private cfg<T>(key: string, fallback: T): T {
    return vscode.workspace.getConfiguration("appLab").get<T>(key, fallback);
  }

  get host(): string {
    return this.cfg("daemon.host", "127.0.0.1");
  }

  get port(): number {
    return this.cfg("daemon.port", 8800);
  }

  get baseUrl(): string {
    return `http://${this.host}:${this.port}`;
  }

  /**
   * Resolve once the daemon answers; throw if it stays unreachable.
   *
   * The probe doubles as the version fetch: `/v1/version` is the daemon's
   * cheapest endpoint (a static string), so a successful probe already carries
   * the version — callers reuse it instead of issuing a second round-trip.
   */
  async start(): Promise<VersionResponse> {
    const version = await this.probeWithRetry();
    if (version) {
      return version;
    }
    throw new Error(
      vscode.l10n.t(
        "No arduino-app-cli daemon reachable at {0}. Is the arduino-app-cli service running? (systemctl status arduino-app-cli)",
        this.baseUrl,
      ),
    );
  }

  /** "Reconnect" is just a fresh probe — there is no local process to restart. */
  reconnect(): Promise<VersionResponse> {
    return this.start();
  }

  /**
   * Probe a few times before giving up — tolerates a momentarily busy daemon.
   * Returns the version payload on the first success (usually the first try when
   * the daemon is up), undefined if every attempt fails.
   */
  private async probeWithRetry(attempts = 3, timeoutMs = 1000): Promise<VersionResponse | undefined> {
    for (let i = 0; i < attempts; i++) {
      const version = await this.probe(timeoutMs);
      if (version) {
        return version;
      }
      await delay(300);
    }
    return undefined;
  }

  /** HTTP liveness probe with a bounded timeout; returns the version on success. */
  private async probe(timeoutMs = 1500): Promise<VersionResponse | undefined> {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      const res = await fetch(`${this.baseUrl}/v1/version`, { signal: ctrl.signal });
      if (!res.ok) {
        return undefined;
      }
      return (await res.json()) as VersionResponse;
    } catch {
      return undefined;
    } finally {
      clearTimeout(timer);
    }
  }
}

function delay(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}
