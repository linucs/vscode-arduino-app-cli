# Arduino App CLI for VS Code

A lightweight VS Code extension that wraps the **Arduino App CLI**
(`arduino-app-cli`) so you can build, run and monitor **Arduino UNO Q** apps
without leaving the editor.

The UNO Q is a dual-brain board: a Linux CPU that runs **Python** apps (in Docker)
and an Arduino **MCU** that runs **C++ sketches**. An *app* bundles both halves
plus reusable **bricks** and optional AI **models**. This extension is a thin
layer over the same daemon the official App Lab GUI uses — your files stay plain
files on disk, edited with VS Code's native editor.

## Why you'll like it

- 🪶 **Thin** — talks to the on-board `arduino-app-cli` daemon over REST/SSE (and a
  WebSocket for the serial monitor); no heavyweight runtime.
- 🧰 **In-editor** — Apps / Bricks / Models trees, an app-scoped **Run / Stop**, a
  live **Console**, and a serial monitor terminal.
- 🧠 **Native files** — edit `python/main.py` and `sketch/sketch.ino` directly,
  with IntelliSense for both halves — C++ from the sketch's last build and Python
  stubs for the Arduino framework.

## Getting started

1. **Check `arduino-app-cli`** on your Arduino UNO Q (it ships as a systemd service listening on `127.0.0.1:8800`).
2. **Open the board in VS Code** — typically via **Remote-SSH**, so the extension runs on the board next to the daemon and your `~/ArduinoApps` workspace.
3. Open the **Arduino App CLI** view in the Activity Bar. Your apps appear under **My Apps** and ready-made templates under **Examples**.
4. Pick an app and click **Run** ▶ — it compiles & flashes the sketch to the MCU and
   starts the Python side, streaming progress to the Console.

## Features

| Area | What you get |
| --- | --- |
| **Apps** | New / Run / Stop / Restart / Delete, Console (logs), Export / Import, Copy & Edit (examples), Set Default, Open Exposed Port |
| **Bricks** | Browse the catalog, add to an app, configure variables, rename, remove |
| **Models** | List, import an Edge Impulse project, delete, view details |
| **Sketch (MCU) C++ libraries** | Search the Arduino catalog and add/remove per-app libraries |
| **IntelliSense** | One **Configure IntelliSense** command sets up both: `.vscode/c_cpp_properties.json` from the sketch's last build (C/C++ extension resolves the Arduino core, board defines and libraries) and `.vscode/typings/arduino/**` Python stubs (with `python.analysis.stubPath` pointed at them) so Pylance resolves `arduino.app_utils` / `arduino.app_bricks.*` |
| **Serial monitor** | A terminal over the daemon WebSocket, with line-ending control and log save |
| **System** | Version, configuration, properties, system update, cleanup, network mode, keyboard, board name |
| **AI assistant** | One command installs a Claude/Copilot skill describing the CLI |

The **Run / Stop / Console / Serial Monitor** controls are *app-scoped*: they act
on whichever app owns the file you're editing (resolved by the nearest `app.yaml`),
and also appear on each app in the tree, in the editor toolbar, and the status bar.

## Settings

| Key | Default | Description |
| --- | --- | --- |
| `appLab.daemon.host` | `127.0.0.1` | Daemon host. |
| `appLab.daemon.port` | `8800` | Daemon port (on-board systemd service). |
| `appLab.cliPath` | `arduino-app-cli` | CLI binary, used for CLI-only commands (clean-cache, system init/cleanup/…). |
| `appLab.apiKey` | `""` | Optional `X-API-Key` header. |
| `appLab.monitor.lineEnding` | `lf` | Serial monitor line ending. |
| `appLab.logs.tail` | `200` | Lines requested when opening a console. |
| `appLab.intellisense.autoConfigure` | `true` | Refresh IntelliSense (C++ config + Python stubs) automatically after each successful run. |

## Requirements

- VS Code **1.120+**.
- `arduino-app-cli` installed on the Arduino UNO Q.
- Reaching the board over Remote-SSH (recommended) or a tunnel to its daemon.

## For developers

```bash
yarn install
yarn compile     # type-check + lint + l10n gate + bundle
yarn test        # SSE parser + mock-daemon transport tests
yarn vsix        # build a .vsix
```

The transport core (`src/appLabClient.ts`, `src/sseParser.ts`, `src/daemon.ts`)
has no VS Code dependency and is unit-tested against a mock daemon. See
[`.claude/docs`](.claude/docs) for the phased design.
