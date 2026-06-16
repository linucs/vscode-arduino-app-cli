from _typeshed import Incomplete
from arduino.app_peripherals.speaker import ALSASpeaker as ALSASpeaker, BaseSpeaker as BaseSpeaker, Speaker as Speaker
from arduino.app_utils import Logger as Logger, brick as brick
from typing import Literal

logger: Incomplete
type WaveType = Literal['sine', 'square', 'sawtooth', 'triangle']

class WaveGenerator:
    """
    Continuous wave generator brick for audio synthesis.

    This brick generates continuous audio waveforms (sine, square, sawtooth, triangle)
    and streams them to a Speaker in real-time. It provides smooth transitions
    between frequency and amplitude changes using configurable envelope parameters.

    The generator runs continuously in a background thread, producing audio blocks
    with minimal latency.
    """
    def __init__(self, speaker: BaseSpeaker | None = None, wave_type: WaveType = 'sine', attack: float = 0.01, release: float = 0.03, glide: float = 0.02) -> None:
        '''
        Initialize the WaveGenerator brick.

        Args:
            speaker (BaseSpeaker): Pre-configured Speaker instance. If None, WaveGenerator
                will create an internal Speaker optimized for real-time synthesis. If provided,
                ensure it uses np.float32 format and appropriate latency settings.
            wave_type (WaveType): Initial waveform type (default: "sine").
            attack (float): Attack time for amplitude envelope in seconds (default: 0.01).
            release (float): Release time for amplitude envelope in seconds (default: 0.03).
            glide (float): Frequency glide time (portamento) in seconds (default: 0.02).

            Example external Speaker configuration:
            ```python
            speaker = Speaker(
                device="plughw:CARD=MyCard,DEV=0",
                sample_rate=Speaker.RATE_48K,
                channels=2,
                format=np.float32,
            )
            ```

        Raises:
            SpeakerException: If no USB speaker is found or device is busy.
        '''
    @property
    def wave_type(self) -> WaveType:
        '''
        Get or set the current waveform type.

        Args:
            wave_type (WaveType): One of "sine", "square", "sawtooth", "triangle".

        Returns:
            WaveType: Current waveform type ("sine", "square", "sawtooth", "triangle").
        '''
    @wave_type.setter
    def wave_type(self, wave_type: WaveType): ...
    @property
    def sample_rate(self) -> int:
        """
        Get the audio sample rate in Hz.

        Returns:
            int: Sample rate in Hz.

        Raises:
            RuntimeError: If no speaker is configured.
        """
    @property
    def block_duration(self) -> float:
        """
        Get the duration of each audio block in seconds.

        Returns:
            float: Block duration in seconds.
        """
    @property
    def frequency(self) -> float:
        """
        Get or set the current output frequency in Hz.

        The frequency will smoothly transition to the new value over the
        configured glide time.

        Args:
            frequency (float): Target frequency in Hz (typically 20-8000 Hz).

        Returns:
            float: Current output frequency in Hz.

        Raises:
            ValueError: If the frequency is negative.
        """
    @frequency.setter
    def frequency(self, freq: float): ...
    @property
    def amplitude(self) -> float:
        """
        Get or set the current output amplitude.

        The amplitude will smoothly transition to the new value over the
        configured attack/release time.

        Args:
            amplitude (float): Target amplitude in range [0.0, 1.0].

        Returns:
            float: Current output amplitude (0.0-1.0).

        Raises:
            ValueError: If the amplitude is not in range [0.0, 1.0].
        """
    @amplitude.setter
    def amplitude(self, amp: float): ...
    @property
    def attack(self) -> float:
        """
        Get or set the current attack time in seconds.

        Attack time controls how quickly the amplitude rises to the target value.

        Args:
            attack (float): Attack time in seconds.

        Returns:
            float: Current attack time in seconds.

        Raises:
            ValueError: If the attack time is negative.
        """
    @attack.setter
    def attack(self, attack: float): ...
    @property
    def release(self) -> float:
        """
        Get or set the current release time in seconds.

        Release time controls how quickly the amplitude falls to the target value.

        Args:
            release (float): Release time in seconds.

        Returns:
            float: Current release time in seconds.

        Raises:
            ValueError: If the release time is negative.
        """
    @release.setter
    def release(self, release: float): ...
    @property
    def glide(self) -> float:
        """
        Get the current frequency glide time in seconds (portamento).

        Glide time controls how quickly the frequency transitions to the target value.

        Args:
            glide (float): Frequency glide time in seconds.

        Returns:
            float: Current frequency glide time in seconds.

        Raises:
            ValueError: If the glide time is negative.
        """
    @glide.setter
    def glide(self, glide: float): ...
    @property
    def volume(self) -> int | None:
        """
        Get or set the wave generator volume level.

        Args:
            volume (int): Hardware volume level (0-100).

        Returns:
            int: Current volume level (0-100).

        Raises:
            ValueError: If the volume is not in range [0, 100].
        """
    @volume.setter
    def volume(self, volume: int): ...
    @property
    def state(self) -> dict:
        """
        Get current generator state.

        Returns:
            dict: Dictionary containing current frequency, amplitude, wave type, etc.
        """
    def start(self) -> None:
        """
        Start the wave generator and audio output.

        This starts the speaker device too.
        """
    def stop(self) -> None:
        """
        Stop the wave generator and audio output.

        This stops the speaker device too.
        """
