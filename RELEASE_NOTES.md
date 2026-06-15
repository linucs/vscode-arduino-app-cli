# Arduino App CLI — Release Notes

Build, run, and monitor **Arduino UNO Q** apps in **plain VS Code** — without leaving the editor. A thin wrapper around the [`arduino-app-cli`](https://github.com/arduino/arduino-app-cli) daemon: it talks to the App Lab daemon running on the board and gives you tree views, buttons, and a live console for what it already does.

> **Requires the `arduino-app-cli` daemon** reachable from the extension (on the UNO Q board or a host running App Lab). It isn't bundled — that's what keeps the extension small. Prefer building sketches with the official `arduino-cli` toolchain? Install the sister extension [**Arduino CLI IDE**](https://marketplace.visualstudio.com/items?itemName=linucs.vscode-arduino-cli-ide).

---

## v0.1.0 — 2026-06-14 — first public release

- **App Lab views** — an Activity Bar container with **Examples**, **Brick Catalog**, and **Models** trees, plus per-app **Project Bricks** and **Project Libraries** views in the Explorer.
- **App lifecycle** — create, import, run, stop, restart, and delete apps; stream build and run progress to a live **Console**; export apps and copy examples to edit; set a default app and open an app's exposed port.
- **Bricks** — browse the catalog, add bricks to an app, configure their variables, rename, and remove them.
- **Models** — list models, import an Edge Impulse project, view details, and delete.
- **Sketch (MCU) C++ libraries** — search the Arduino catalog and add or remove per-app libraries.
- **Serial monitor & plotter** — a monitor terminal over the daemon WebSocket with configurable line ending and auto-reconnect, and a real-time data plotter.
- **Python environment** — optional managed virtual-environment setup.
- **System utilities** — show version, configuration, and properties; reconnect to the daemon; update and cleanup; network mode, keyboard layout, and board naming.
- **AI assistant integration** — install a Claude/Copilot skill describing the CLI.
- **Localization** — the UI is translated into 14 languages.
- **Get Started walkthrough** — a guided tour shown on first install.

---

**Install:** [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=linucs.vscode-arduino-app-cli) · [Open VSX](https://open-vsx.org/extension/linucs/vscode-arduino-app-cli) · or download the `.vsix` from the release.

Found a bug or have an idea? [Open an issue](https://github.com/linucs/vscode-arduino-app-cli/issues). For the structured, technical history see the [full changelog](https://github.com/linucs/vscode-arduino-app-cli/blob/main/CHANGELOG.md).
