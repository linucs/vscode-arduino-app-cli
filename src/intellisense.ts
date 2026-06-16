import * as fs from "node:fs";
import * as fsp from "node:fs/promises";
import * as path from "node:path";
import * as vscode from "vscode";
import type { AppLabClient } from "./appLabClient";
import type { AppInfo } from "./api/types";

const CPPTOOLS_EXT = "ms-vscode.cpptools";
const PYTHON_EXT = "ms-python.python";
const CONFIG_NAME = "Arduino";
/** Marks the `typings/arduino` dir as ours and records the stub version. */
const STUBS_MARKER = ".arduino-stubs";

/** Flags extracted from a single compile_commands.json entry. */
export interface ParsedCommand {
  includes: string[];
  defines: string[];
  compilerPath: string;
  /** e.g. "gnu++17" / "c++17", or "" if none. */
  std: string;
  /** Target/arch flags (-mcpu, -mthumb, -march, …) for the compiler query. */
  compilerArgs: string[];
}

interface CompileCommandEntry {
  directory: string;
  command?: string;
  arguments?: string[];
  file: string;
}

/**
 * Generates a cpptools `c_cpp_properties.json` for an app's MCU sketch so
 * IntelliSense resolves the Arduino (Zephyr) core, the board's defines, and every
 * library the sketch includes — none of which are visible from the `.ino` alone.
 *
 * Unlike the standalone arduino-cli extension, this stack has no way to generate a
 * compilation database on demand: the App Lab daemon embeds arduino-cli in-process
 * (unreachable from here) and only compiles as part of `app start` (compile +
 * flash). The one artifact we can use is the `compile_commands.json` arduino-cli
 * drops into `<app>/.cache/sketch/` during that build, so we read and translate
 * it. It is always the real build the device used, with the correct toolchain.
 *
 * The same `configure` action also installs Python type stubs for the Arduino
 * framework (`arduino.app_utils` / `arduino.app_bricks.*`), which lives only in the
 * app's Docker image — see {@link ensureStubs}. C++ and Python IntelliSense are one
 * feature: one command, one setting, both artifacts.
 */
export class IntelliSenseManager {
  private cpptoolsHintShown = false;
  private pythonHintShown = false;
  private stubsVersionCache: string | undefined;

  constructor(
    private readonly client: AppLabClient,
    private readonly output: vscode.OutputChannel,
    private readonly context: vscode.ExtensionContext,
  ) {}

  /** Whether auto-regeneration after a run is enabled. */
  autoEnabled(): boolean {
    return vscode.workspace
      .getConfiguration("appLab")
      .get<boolean>("intellisense.autoConfigure", true);
  }

  /**
   * Set up IntelliSense for the app: install the Arduino Python stubs (always) and
   * translate the sketch's last compilation database into `c_cpp_properties.json`
   * (when a build exists). `silent` suppresses user-facing messages (used by the
   * post-run auto-trigger).
   */
  async configure(app: AppInfo, opts: { silent?: boolean } = {}): Promise<void> {
    const appPath = app.path ?? (await this.client.getApp(app.id)).path;
    if (!appPath) {
      if (!opts.silent) {
        vscode.window.showWarningMessage(
          vscode.l10n.t("Could not resolve the app's location on disk."),
        );
      }
      return;
    }
    const root = this.resolveRoot(appPath);

    // Python first, so a sketch that hasn't been built yet still gets working
    // Python IntelliSense.
    await this.ensureStubs(root, opts);

    // C++ side: the compilation database only exists after a build.
    const dbPath = path.join(appPath, ".cache", "sketch", "compile_commands.json");
    let raw: string;
    try {
      raw = await fsp.readFile(dbPath, "utf8");
    } catch {
      // Don't auto-run (that flashes the MCU); the Python stubs are already in
      // place, so report this as a partial success and point the user at Run.
      if (!opts.silent) {
        vscode.window.showInformationMessage(
          vscode.l10n.t(
            "Python stubs installed. Run the app once to build the sketch for C++ IntelliSense.",
          ),
        );
      }
      return;
    }

    let entries: CompileCommandEntry[];
    try {
      entries = JSON.parse(raw);
    } catch (err) {
      this.output.appendLine(`[intellisense] could not parse ${dbPath}: ${asMessage(err)}`);
      return;
    }

    const entry = pickSketchEntry(entries);
    if (!entry) {
      this.output.appendLine("[intellisense] no sketch entry in compile_commands.json");
      return;
    }

    if (!opts.silent) {
      this.maybeHintCpptools();
    }

    const parsed = parseCompileCommand(entry);
    const forced = resolveForcedInclude(entry, parsed.includes);
    const config = buildCppProperties(parsed, forced);
    await this.writeConfig(root, config);

    this.output.appendLine(
      `[intellisense] wrote c_cpp_properties.json (${parsed.includes.length} include paths, ${parsed.defines.length} defines)`,
    );
    if (!opts.silent) {
      vscode.window.showInformationMessage(
        vscode.l10n.t("IntelliSense configured for {0}.", app.name),
      );
    }
  }

  // --- internals -------------------------------------------------------------

  /** The workspace root the editor config is written to (or the app dir). */
  private resolveRoot(appPath: string): string {
    const folder =
      vscode.workspace.getWorkspaceFolder(vscode.Uri.file(appPath)) ??
      vscode.workspace.workspaceFolders?.[0];
    return folder?.uri.fsPath ?? appPath;
  }

  /**
   * Copy the bundled Arduino Python stubs into `<root>/typings/arduino` so Pylance
   * resolves `arduino.app_utils` / `arduino.app_bricks.*`. `typings` is Pylance's
   * default `stubPath`, so no settings change is needed.
   *
   * Idempotent: a marker file records the shipped stub version; we skip the copy
   * when it already matches (keeps the silent after-run path cheap). A `typings/
   * arduino` we didn't create is left untouched.
   */
  private async ensureStubs(root: string, opts: { silent?: boolean }): Promise<void> {
    const src = path.join(this.context.extensionPath, "stubs", "arduino");
    const dest = path.join(root, "typings", "arduino");
    const markerPath = path.join(dest, STUBS_MARKER);
    const version = await this.stubsVersion();

    const existingMarker = await fsp.readFile(markerPath, "utf8").catch(() => undefined);
    if (existingMarker === undefined && (await exists(dest))) {
      // A typings/arduino we didn't create — never clobber the user's own stubs.
      if (!opts.silent) {
        vscode.window.showWarningMessage(
          vscode.l10n.t(
            "typings/arduino already exists and wasn't created by the extension — leaving it untouched.",
          ),
        );
      }
      return;
    }
    if (existingMarker?.trim() === version) {
      return; // already current
    }

    await fsp.rm(dest, { recursive: true, force: true });
    await fsp.cp(src, dest, { recursive: true });
    await fsp.writeFile(markerPath, version + "\n");
    this.output.appendLine(`[intellisense] installed Python stubs (${version}) into ${dest}`);
    await this.silenceMissingSourceWarning();

    if (!opts.silent) {
      this.warnIfStubPathMoved();
      this.maybeHintPython();
    }
  }

  /**
   * Silence Pylance's `reportMissingModuleSource` for this workspace. We ship
   * stubs only — the real `arduino_app_bricks` package lives in the app's Docker
   * image, not on the host — so Pylance resolves types from the `.pyi` but warns
   * that it can't find the runtime source. That warning is expected here and would
   * fire on every `import arduino.*`, so we turn it off (workspace-scoped, merged
   * into existing overrides). Written via the config API so `.vscode/settings.json`
   * comments/formatting survive.
   */
  private async silenceMissingSourceWarning(): Promise<void> {
    try {
      const cfg = vscode.workspace.getConfiguration("python.analysis");
      const current = cfg.get<Record<string, string>>("diagnosticSeverityOverrides") ?? {};
      if (current.reportMissingModuleSource === "none") {
        return;
      }
      await cfg.update(
        "diagnosticSeverityOverrides",
        { ...current, reportMissingModuleSource: "none" },
        vscode.ConfigurationTarget.Workspace,
      );
    } catch (err) {
      this.output.appendLine(
        `[intellisense] could not set diagnosticSeverityOverrides: ${asMessage(err)}`,
      );
    }
  }

  /** The shipped stub version, from `stubs/STUBS_VERSION` (cached). */
  private async stubsVersion(): Promise<string> {
    if (this.stubsVersionCache === undefined) {
      const file = path.join(this.context.extensionPath, "stubs", "STUBS_VERSION");
      this.stubsVersionCache = (await fsp.readFile(file, "utf8").catch(() => "")).trim() || "unknown";
    }
    return this.stubsVersionCache;
  }

  /** Warn if the user moved `python.analysis.stubPath` off the default `typings`. */
  private warnIfStubPathMoved(): void {
    const stubPath = vscode.workspace
      .getConfiguration("python")
      .get<string>("analysis.stubPath", "typings");
    if (stubPath && stubPath !== "typings") {
      vscode.window.showWarningMessage(
        vscode.l10n.t(
          "Arduino stubs were written to 'typings', but python.analysis.stubPath is '{0}', so they won't be picked up.",
          stubPath,
        ),
      );
    }
  }

  private async writeConfig(
    root: string,
    arduinoConfig: Record<string, unknown>,
  ): Promise<void> {
    const vscodeDir = path.join(root, ".vscode");
    await fsp.mkdir(vscodeDir, { recursive: true });
    const file = path.join(vscodeDir, "c_cpp_properties.json");

    let existing: { version?: number; configurations?: Record<string, unknown>[] } = {};
    try {
      existing = JSON.parse(await fsp.readFile(file, "utf8"));
    } catch {
      // no existing file (or unparseable) — start fresh
    }
    const merged = mergeConfiguration(existing, arduinoConfig);
    await fsp.writeFile(file, JSON.stringify(merged, null, 2) + "\n");
  }

  private maybeHintCpptools(): void {
    if (this.cpptoolsHintShown) {
      return;
    }
    if (vscode.extensions.getExtension(CPPTOOLS_EXT)) {
      return;
    }
    this.cpptoolsHintShown = true;
    void vscode.window
      .showInformationMessage(
        vscode.l10n.t("IntelliSense uses the C/C++ extension, which isn't installed."),
        vscode.l10n.t("Install"),
      )
      .then((choice) => {
        if (choice) {
          void vscode.commands.executeCommand(
            "workbench.extensions.installExtension",
            CPPTOOLS_EXT,
          );
        }
      });
  }

  private maybeHintPython(): void {
    if (this.pythonHintShown) {
      return;
    }
    if (vscode.extensions.getExtension(PYTHON_EXT)) {
      return;
    }
    this.pythonHintShown = true;
    void vscode.window
      .showInformationMessage(
        vscode.l10n.t("Python IntelliSense uses the Python extension, which isn't installed."),
        vscode.l10n.t("Install"),
      )
      .then((choice) => {
        if (choice) {
          void vscode.commands.executeCommand(
            "workbench.extensions.installExtension",
            PYTHON_EXT,
          );
        }
      });
  }
}

function asMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

/** Whether a filesystem path exists. */
async function exists(p: string): Promise<boolean> {
  return fsp.stat(p).then(
    () => true,
    () => false,
  );
}

// --- pure helpers (unit-testable) -------------------------------------------

/**
 * Split a compiler command string into argv, honoring quotes that appear
 * anywhere in a token (e.g. `-I"/Program Files/x"` → `-I/Program Files/x`).
 */
export function tokenize(command: string): string[] {
  const out: string[] = [];
  let cur = "";
  let quote: '"' | "'" | null = null;
  let started = false;
  for (const c of command) {
    if (quote) {
      if (c === quote) {
        quote = null;
      } else {
        cur += c;
      }
    } else if (c === '"' || c === "'") {
      quote = c;
      started = true;
    } else if (/\s/.test(c)) {
      if (started) {
        out.push(cur);
        cur = "";
        started = false;
      }
    } else {
      cur += c;
      started = true;
    }
  }
  if (started) {
    out.push(cur);
  }
  return out;
}

/**
 * Tokenize the contents of a GCC `@response-file`: whitespace separates tokens,
 * single/double quotes group, and a backslash escapes the next character — so
 * `-DVER=\"1.2\"` becomes the single token `-DVER="1.2"`. The backslash handling
 * is why this can't reuse {@link tokenize} (which is for shell-style commands).
 */
export function tokenizeResponseFile(text: string): string[] {
  const out: string[] = [];
  let cur = "";
  let quote: '"' | "'" | null = null;
  let started = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === "\\" && i + 1 < text.length) {
      cur += text[++i];
      started = true;
    } else if (quote) {
      if (c === quote) {
        quote = null;
      } else {
        cur += c;
      }
    } else if (c === '"' || c === "'") {
      quote = c;
      started = true;
    } else if (/\s/.test(c)) {
      if (started) {
        out.push(cur);
        cur = "";
        started = false;
      }
    } else {
      cur += c;
      started = true;
    }
  }
  if (started) {
    out.push(cur);
  }
  return out;
}

/**
 * Expand GCC `@file` response-file arguments in place. `@file` tells the compiler
 * to read that file and substitute its whitespace-separated contents as if they
 * appeared on the command line — a standard GCC feature used to pass more flags
 * than the OS command-length limit allows.
 *
 * Nested `@file`s expand recursively (depth-guarded); an unreadable file is left
 * as its literal token, matching GCC (which treats a missing `@file` literally).
 * `readFile` is injectable for tests.
 */
export function expandResponseFiles(
  argv: string[],
  baseDir: string,
  readFile: (p: string) => string = (p) => fs.readFileSync(p, "utf8"),
  depth = 0,
): string[] {
  if (depth > 16) {
    return argv; // cycle / abuse guard
  }
  const out: string[] = [];
  for (const arg of argv) {
    if (arg.length > 1 && arg.startsWith("@")) {
      const ref = arg.slice(1);
      const file = path.isAbsolute(ref) ? ref : path.join(baseDir, ref);
      let content: string;
      try {
        content = readFile(file);
      } catch {
        out.push(arg); // unreadable — leave literal (GCC semantics)
        continue;
      }
      out.push(
        ...expandResponseFiles(
          tokenizeResponseFile(content),
          path.dirname(file),
          readFile,
          depth + 1,
        ),
      );
    } else {
      out.push(arg);
    }
  }
  return out;
}

/**
 * Extract include dirs, defines, compiler path and -std from a DB entry.
 *
 * `@response-file` args are expanded first (see {@link expandResponseFiles}), and
 * the GCC `-iprefix` + `-iwithprefixbefore`/`-iwithprefix` include mechanism is
 * resolved. Plain `-I`/`-isystem`/`-D` still work unchanged. `readFile` is
 * injectable for tests.
 */
export function parseCompileCommand(
  entry: CompileCommandEntry,
  readFile: (p: string) => string = (p) => fs.readFileSync(p, "utf8"),
): ParsedCommand {
  const raw = entry.arguments ?? tokenize(entry.command ?? "");
  const argv = expandResponseFiles(raw, entry.directory ?? "", readFile);
  const includes: string[] = [];
  const defines: string[] = [];
  const compilerArgs: string[] = [];
  const compilerPath = argv[0] ?? "";
  let std = "";
  // Set by `-iprefix`; each following `-iwithprefix[before] dir` resolves against
  // it (GCC concatenates literally), e.g. `.../include/` + `freertos/...`.
  let prefix = "";
  const withPrefix = (dir: string): string => path.normalize(prefix + dir);

  for (let i = 1; i < argv.length; i++) {
    const a = argv[i];
    if (a === "-I" || a === "-isystem" || a === "-iquote") {
      if (argv[i + 1]) {
        includes.push(argv[++i]);
      }
    } else if (a === "-iprefix") {
      prefix = argv[++i] ?? prefix;
    } else if (a === "-iwithprefixbefore" || a === "-iwithprefix") {
      if (argv[i + 1]) {
        includes.push(withPrefix(argv[++i]));
      }
    } else if (a.startsWith("-iwithprefixbefore")) {
      includes.push(withPrefix(a.slice("-iwithprefixbefore".length)));
    } else if (a.startsWith("-iwithprefix")) {
      includes.push(withPrefix(a.slice("-iwithprefix".length)));
    } else if (a.startsWith("-iprefix")) {
      prefix = a.slice("-iprefix".length);
    } else if (a.startsWith("-isystem")) {
      includes.push(a.slice(8));
    } else if (a.startsWith("-iquote")) {
      includes.push(a.slice("-iquote".length));
    } else if (a.startsWith("-I")) {
      includes.push(a.slice(2));
    } else if (a === "-D") {
      if (argv[i + 1]) {
        defines.push(argv[++i]);
      }
    } else if (a.startsWith("-D")) {
      defines.push(a.slice(2));
    } else if (a.startsWith("-std=")) {
      std = a.slice(5);
    } else if (/^-m/.test(a) || a.startsWith("-march")) {
      // Target/arch flags so cpptools queries the right multilib + ARM defines.
      compilerArgs.push(a);
    }
  }

  // De-dupe include dirs while preserving order.
  const seen = new Set<string>();
  const uniqueIncludes = includes.filter((i) => (seen.has(i) ? false : (seen.add(i), true)));

  return { includes: uniqueIncludes, defines, compilerPath, std, compilerArgs };
}

/** Choose the entry for the sketch's generated translation unit. */
export function pickSketchEntry(
  entries: CompileCommandEntry[],
): CompileCommandEntry | undefined {
  return (
    entries.find((e) => e.file?.endsWith(".ino.cpp")) ??
    entries.find((e) => /\.(cpp|cc|cxx)$/.test(e.file ?? "")) ??
    entries[0]
  );
}

/** Header names `#include`d by the given source text (angle + quote forms). */
export function parseIncludeSet(text: string): Set<string> {
  const set = new Set<string>();
  const re = /^\s*#\s*include\s*[<"]([^>"]+)[>"]/gm;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text))) {
    set.add(m[1]);
  }
  return set;
}

/**
 * Discover the header the Arduino preprocessor injected into the generated TU
 * (the first `#include`), resolved to an absolute path against the include dirs.
 * Falls back to scanning the include dirs for `Arduino.h`.
 */
export function resolveForcedInclude(
  entry: CompileCommandEntry,
  includes: string[],
): string | undefined {
  let header: string | undefined;
  try {
    const file = path.isAbsolute(entry.file)
      ? entry.file
      : path.join(entry.directory ?? "", entry.file);
    const text = fs.readFileSync(file, "utf8");
    const first = [...parseIncludeSet(text)][0];
    header = first;
  } catch {
    // unreadable TU — fall through to the Arduino.h fallback
  }
  const candidate = header ?? "Arduino.h";
  for (const dir of includes) {
    const abs = path.join(dir, candidate);
    if (fs.existsSync(abs)) {
      return abs;
    }
  }
  // Last resort: look specifically for Arduino.h anywhere in the include dirs.
  if (candidate !== "Arduino.h") {
    for (const dir of includes) {
      const abs = path.join(dir, "Arduino.h");
      if (fs.existsSync(abs)) {
        return abs;
      }
    }
  }
  return undefined;
}

/** Build the cpptools "Arduino" configuration object from parsed flags. */
export function buildCppProperties(
  parsed: ParsedCommand,
  forcedInclude: string | undefined,
): Record<string, unknown> {
  const isCpp = parsed.std.includes("++");
  const config: Record<string, unknown> = {
    name: CONFIG_NAME,
    includePath: [...parsed.includes, "${workspaceFolder}/**"],
    defines: parsed.defines,
    compilerPath: parsed.compilerPath,
    cStandard: "gnu11",
    cppStandard: isCpp ? parsed.std : "gnu++17",
  };
  // Omit intelliSenseMode so cpptools infers it (e.g. gcc-arm) from compilerPath
  // rather than defaulting to the host's (clang-x64 on macOS).
  if (parsed.compilerArgs.length) {
    config.compilerArgs = parsed.compilerArgs;
  }
  if (forcedInclude) {
    config.forcedInclude = [forcedInclude];
  }
  return config;
}

/** Insert/replace the "Arduino" configuration, preserving any others. */
export function mergeConfiguration(
  existing: { version?: number; configurations?: Record<string, unknown>[] },
  arduinoConfig: Record<string, unknown>,
): { version: number; configurations: Record<string, unknown>[] } {
  const configurations = Array.isArray(existing.configurations)
    ? existing.configurations.filter((c) => c?.name !== CONFIG_NAME)
    : [];
  configurations.unshift(arduinoConfig);
  return { version: existing.version ?? 4, configurations };
}
