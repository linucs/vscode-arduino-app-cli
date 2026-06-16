from _typeshed import Incomplete
from arduino.app_internal.core import EdgeImpulseRunnerFacade as EdgeImpulseRunnerFacade
from arduino.app_utils import Logger as Logger, SlidingWindowBuffer as SlidingWindowBuffer, brick as brick
from typing import Iterable

logger: Incomplete

class VibrationAnomalyDetection(EdgeImpulseRunnerFacade):
    """Detect vibration anomalies from accelerometer time-series using a pre-trained
    Edge Impulse model.

    This Brick buffers incoming samples into a sliding window sized to the model’s
    `input_features_count`, runs inference when a full window is available, extracts
    the **anomaly score**, and (optionally) invokes a user-registered callback when
    the score crosses a configurable threshold.

    Notes:
        - Requires an active Edge Impulse runner; model info is fetched at init.
        - The window size equals the model’s `input_features_count`; samples pushed
          via `accumulate_samples()` are flattened before inference.
        - The expected **units, axis order, and sampling rate** must match those
          used during model training (e.g., m/s² vs g, [ax, ay, az], 100 Hz).
        - A single callback is supported at a time (thread-safe registration).
    """
    def __init__(self, anomaly_detection_threshold: float = 1.0) -> None:
        """Initialize the vibration anomaly detector.

        Args:
            anomaly_detection_threshold (float): Threshold applied to the model’s
                anomaly score to decide whether to trigger the registered callback.
                This is the raw anomaly score, not a normalized confidence value;
                values above 1.0 are valid. Typical starting point is 1.0; tune
                based on your dataset.

        Raises:
            ValueError: If the Edge Impulse runner is unreachable, or if the model
                info is missing/invalid (e.g., non-positive `frequency` or
                `input_features_count`).
        """
    @property
    def anomaly_detection_threshold(self) -> float:
        """Raw anomaly score threshold used to decide when callbacks fire."""
    @anomaly_detection_threshold.setter
    def anomaly_detection_threshold(self, value: float) -> None:
        """Update the raw anomaly score threshold at runtime.

        The value is intentionally not clamped to ``[0.0, 1.0]`` because Edge
        Impulse anomaly scores are distances and can legitimately be greater
        than 1.0.
        """
    def accumulate_samples(self, sensor_samples: Iterable[float]) -> None:
        """Append one or more accelerometer samples to the sliding window buffer.

        Args:
            sensor_samples (Iterable[float]): A sequence of numeric values. This can
                be a single 3-axis sample `(ax, ay, az)`, multiple concatenated
                triples, or any iterable whose flattened length contributes toward
                the model’s `input_features_count`.

        Raises:
            ValueError: If `sensor_samples` is empty or None.

        Notes:
            - Ensure **units** match model training (convert g → m/s² if required).
            - Provide samples at approximately the model’s `frequency` to avoid
              under- or oversampling.
            - When the buffer reaches a full window, `loop()` will consume it.
        """
    def on_anomaly(self, callback: callable):
        """Register a handler to be invoked when an anomaly is detected.

        The callback signature can be one of:
            - `callback()`
            - `callback(anomaly_score: float)`
            - `callback(anomaly_score: float, classification: dict)`

        Args:
            callback (callable): Function to invoke when `anomaly_score >= threshold`.
                If a signature with `classification` is used and the model returns
                an auxiliary classification head, a dict with label scores is passed.

        Notes:
            - Registration is thread-safe and **replaces** any previously set handler.
            - No callback is invoked if no handler is registered or if the score is
              below the threshold.
        """
    def loop(self) -> None:
        """Non-blocking processing step; run this periodically.

        Behavior:
            - Pulls a full window from the buffer (if available).
            - Runs inference via `infer_from_features(...)`.
            - Extracts the anomaly score and, if `>= threshold`, invokes the
              registered callback (respecting its signature).

        Raises:
            StopIteration: Propagated if an internal shutdown condition is signaled.

        Notes:
            - Call at (or faster than) `1 / model_info.frequency` seconds.
            - Consumes **at most one** full window per call.
            - Handles transient queue conditions internally and throttles on errors
              to avoid tight loops.
        """
    def start(self) -> None:
        """Prepare the detector for a new session.

        Notes:
            - Flushes the internal buffer so the next window starts clean.
            - Call before beginning to stream new samples.
        """
    def stop(self) -> None:
        """Stop the detector and release transient resources.

        Notes:
            - Clears the internal buffer; does not alter the registered callback.
        """
