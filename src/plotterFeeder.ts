import { PlotterPanel } from "./plotterPanel";
import { splitLines, parseTelemetryLine } from "./telemetryParser";

/**
 * Bridges an arbitrary UTF-8 text stream to the {@link PlotterPanel}. It buffers
 * partial lines across chunks, parses each complete line as telemetry, and posts
 * any points to the live plotter.
 *
 * Decoupled from any specific source so the same feeder can be fed by EITHER the
 * serial-monitor WebSocket OR the Python log SSE stream — whichever the user
 * selects when opening the plotter. (In the sibling extension this logic lived
 * inside the serial monitor; here it stands alone.)
 */
export class PlotterFeeder {
  private lineBuf = "";

  /** Feed a raw text chunk (may contain partial/multiple lines). */
  feed(chunk: string): void {
    const plotter = PlotterPanel.current();
    if (!plotter?.alive) {
      return;
    }
    const { lines, rest } = splitLines(this.lineBuf, chunk);
    this.lineBuf = rest;
    const points = lines
      .map(parseTelemetryLine)
      .filter((p): p is NonNullable<typeof p> => p !== undefined);
    if (points.length > 0) {
      plotter.postData(points);
    }
  }

  /** Drop any buffered partial line (e.g. when switching source). */
  reset(): void {
    this.lineBuf = "";
  }
}
