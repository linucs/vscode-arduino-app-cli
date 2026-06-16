import numpy as np
from _typeshed import Incomplete

class SoundEffect:
    @staticmethod
    def overdrive(drive: float = 100.0) -> np.ndarray:
        """
        Apply overdrive effect to the audio signal.
        Args:
            signal (np.ndarray): Input audio signal.
            drive (float): Overdrive intensity factor.
        Returns:
            np.ndarray: Processed audio signal with overdrive effect.
        """
    fs: int
    depth_ms: Incomplete
    rate_hz: Incomplete
    mix: Incomplete
    @staticmethod
    def chorus(depth_ms: int = 10, rate_hz: float = 0.25, mix: float = 0.5) -> np.ndarray:
        """
        Apply chorus effect to the audio signal.
        Args:
            signal (np.ndarray): Input audio signal.
            depth_ms (float): Depth of the chorus effect in milliseconds.
            rate_hz (float): Rate of the LFO in Hz.
            mix (float): Mix ratio between dry and wet signals (0.0 to 1.0).
        Returns:
            np.ndarray: Processed audio signal with chorus effect.
        """
    attack: Incomplete
    decay: Incomplete
    sustain: Incomplete
    release: Incomplete
    @staticmethod
    def adsr(attack: float = 0.015, decay: float = 0.2, sustain: float = 0.5, release: float = 0.35):
        """
        Apply ADSR (attack/decay/sustain/release) envelope to the audio signal.
        Args:
            attack (float): Attack time in seconds.
            decay (float): Decay time in seconds.
            sustain (float): Sustain level (0.0 to 1.0).
            release (float): Release time in seconds.
        """
    depth: Incomplete
    rate: Incomplete
    @staticmethod
    def tremolo(depth: float = 0.5, rate: float = 5.0): ...
    @staticmethod
    def vibrato(depth: float = 0.02, rate: float = 0.5): ...
    bit_depth: Incomplete
    reduction: Incomplete
    @staticmethod
    def bitcrusher(bits: int = 4, reduction: int = 6): ...
    oct_up: Incomplete
    oct_down: Incomplete
    @staticmethod
    def octaver(oct_up: bool = True, oct_down: bool = False): ...
