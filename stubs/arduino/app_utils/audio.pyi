from _typeshed import Incomplete

class SineGenerator:
    """Generate sine-wave audio blocks with amplitude envelope smoothing.

    This class produces contiguous sine-wave blocks while maintaining internal
    state (phase, last amplitude, last frequency) so consecutive calls do not
    introduce discontinuities. It uses preallocated NumPy buffers and performs
    in-place operations for efficiency.

    Attributes:
        sample_rate (int): Audio sample rate in Hz.
        attack (float): Attack time for amplitude smoothing in seconds.
        release (float): Release time for amplitude smoothing in seconds.
        glide (float): Glide time for frequency smoothing in seconds.
    """
    sample_rate: Incomplete
    attack: float
    release: float
    glide: float
    def __init__(self, sample_rate: int) -> None:
        """Create a new SineGenerator.

        Args:
            sample_rate (int): The playback sample rate (Hz) used to compute
                phase increments and buffer sizes.
        """
    def reset(self) -> None:
        """Reset internal generator state.

        Resets phase, last frequency and current amplitude to silence. Useful
        when reinitializing playback or ensuring a known baseline before
        tests.
        """
    def get_state(self) -> dict:
        """Return a snapshot of internal generator state.

        Returns a small dict containing ``phase``, ``amp_current`` and
        ``freq_last`` suitable for serialization or for later restoration via
        :meth:`set_state`.

        Returns:
            dict: {'phase': float, 'amp_current': float, 'freq_last': float}
        """
    def set_state(self, state: dict) -> None:
        """Restore internal generator state from a snapshot.

        Args:
            state (dict): State dict with keys ``phase``, ``amp_current`` and
                ``freq_last``. Missing keys are ignored and current values are
                preserved.
        """
    def set_envelope_params(self, attack: float, release: float, glide: float) -> None:
        """Update attack and release envelope parameters.

        Args:
            attack (float): Attack time in seconds (time to rise to target
                amplitude when increasing amplitude).
            release (float): Release time in seconds (time to fall to target
                amplitude when decreasing amplitude).
            glide (float): Glide time in seconds (time to reach target frequency).
        """
    def generate_block(self, freq: float, amp_target: float, block_dur: float, master_volume: float):
        """Generate a block of float32 audio samples.

        The generator keeps internal phase continuity across calls. Amplitude is
        smoothed between the previous amplitude and ``amp_target`` using the
        configured ``attack`` and ``release`` times. Returned buffer is a
        NumPy view (float32) into an internal preallocated array and is valid
        until the next call to this method.

        Args:
            freq (float): Target frequency in Hz for this block.
            amp_target (float): Target amplitude in range [0.0, 1.0].
            block_dur (float): Duration of the requested block in seconds.
            master_volume (float, optional): Global gain multiplier. Defaults
                to 1.0.

        Returns:
            numpy.ndarray: A 1-D float32 NumPy array containing the generated
            audio samples for the requested block.
        """
