import * as path from "node:path";
import * as fs from "node:fs/promises";
import * as vscode from "vscode";
import { resolveActiveWorkspaceRoot } from "../workspaceRoot";

const SKILL_REL = path.join(".claude", "skills", "arduino-app-cli");
const COPILOT_INSTRUCTIONS_REL = path.join(
  ".github",
  "instructions",
  "arduino-app-cli.instructions.md",
);

/**
 * Set up the shared AI-assistant config for this workspace.
 *
 * The single source of truth is the skill at `.claude/skills/arduino-app-cli/`
 * (`SKILL.md` + `reference.md`, shipped in the .vsix). The two hosts discover
 * guidance differently, so we materialise it for each:
 *
 * - **Claude Code** natively discovers Agent Skills under `.claude/skills/`,
 *   reads `SKILL.md`, and lazily loads `reference.md` when the skill triggers.
 *   We just copy the skill dir.
 * - **GitHub Copilot** does NOT read `.claude/skills/`. In VS Code it reads
 *   instruction files from `.github/instructions/*.instructions.md`, gated by an
 *   `applyTo` glob. We *derive* that file from the very same `SKILL.md` (strip its
 *   frontmatter, prepend an `applyTo: "**"` header) so Copilot gets the exact
 *   guidance Claude reads natively — one source of truth, no hand-written copy to
 *   drift.
 */
export async function installAiAssistants(
  context: vscode.ExtensionContext,
): Promise<void> {
  const root = await resolveActiveWorkspaceRoot(
    vscode.l10n.t("Select the folder to set up the Arduino App Studio AI assistant in"),
  );
  if (!root) {
    vscode.window.showWarningMessage(
      vscode.l10n.t("Open a workspace folder first to install the Arduino App Studio skill."),
    );
    return;
  }

  const srcDir = path.join(context.extensionPath, SKILL_REL);

  try {
    const destDir = path.join(root, SKILL_REL);
    await fs.cp(srcDir, destDir, { recursive: true });
    await writeCopilotInstructions(srcDir, root);
  } catch (err) {
    vscode.window.showErrorMessage(
      vscode.l10n.t(
        "Could not install the Arduino App Studio skill: {0}",
        err instanceof Error ? err.message : String(err),
      ),
    );
    return;
  }

  vscode.window.showInformationMessage(
    vscode.l10n.t(
      "Arduino App Studio AI assistant configured: skill installed for Claude Code and GitHub Copilot in this folder.",
    ),
  );
}

async function writeCopilotInstructions(
  srcDir: string,
  root: string,
): Promise<void> {
  const skill = await fs.readFile(path.join(srcDir, "SKILL.md"), "utf8");

  const header = [
    "---",
    'applyTo: "**"',
    "---",
    "",
    "<!-- Generated from .claude/skills/arduino-app-cli/SKILL.md by the Arduino App Studio extension",
    '     ("Arduino App Studio: Set Up AI Assistant"). Edits here are overwritten on re-install —',
    "     change the skill instead. -->",
    "",
    "The following is MANDATORY whenever the user works on an Arduino App",
    "(apps, bricks, models, sketches) or asks about `arduino-app-cli`. Follow it",
    "exactly — the directives below are not optional.",
    "",
    "---",
    "",
  ].join("\n");

  const content = header + stripFrontmatter(skill).trimStart() + "\n";

  const destPath = path.join(root, COPILOT_INSTRUCTIONS_REL);
  await fs.mkdir(path.dirname(destPath), { recursive: true });
  await fs.writeFile(destPath, content, "utf8");
}

/** Drop a leading `---`…`---` YAML frontmatter block, if present. */
function stripFrontmatter(md: string): string {
  const m = /^---\r?\n[\s\S]*?\r?\n---\r?\n/.exec(md);
  return m ? md.slice(m[0].length) : md;
}
