---
name: arduino-app-cli
description: |
  Build, run, monitor and troubleshoot Arduino App Lab apps on the Arduino UNO Q
  using `arduino-app-cli`. Use whenever the user works on an App Lab app (its
  Python code, its MCU sketch, its bricks or AI models), asks about
  `arduino-app-cli`, the App Lab daemon/REST API, or the UNO Q dual-brain board.
---

# Arduino App Lab assistant

ALWAYS read `.claude/skills/arduino-app-cli/reference.md` before answering an
Arduino App Lab question — it is the authoritative reference for the CLI command
tree, the daemon REST/SSE API, the app on-disk layout, and the MCU/sketch and
Python halves of an app. Do not answer from memory.

Key facts to keep in mind:

- An **app** is the unit of work. It lives under `~/ArduinoApps/<app>/` and may
  contain a **Python** half (`python/main.py`, runs in Docker on the Linux CPU)
  and/or a **sketch** half (`sketch/sketch.ino`, C++ on the MCU). At least one is
  required. The two halves talk over the Arduino router via `Arduino_RouterBridge`.
- **Run = `arduino-app-cli app start <app>`**: it compiles + flashes the sketch to
  the MCU *and* starts the Python side. There is no separate compile/upload command.
- The board runs the daemon as a systemd service on `127.0.0.1:8800`. Prefer the
  CLI for scripting; the daemon REST API (with SSE for logs/start/stop/status and a
  WebSocket serial monitor) is what GUIs use.
- **MCU C++ libraries** are managed per app via the daemon's
  `/v1/apps/{id}/sketch/libraries` endpoints (no CLI subcommand); they edit
  `sketch/sketch.yaml`. **Python deps** go in `python/requirements.txt` and are
  installed inside the container.
- The board is a fixed FQBN (`arduino:zephyr:unoq`) — there is no board selection.

Drive everything through the `arduino-app-cli` binary (use `--format json` for
machine-readable output) or the daemon REST API. There are no wrapper tools.
