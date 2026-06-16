from .effects import *
from .composition import MusicComposition as MusicComposition
from .generator import WaveSamplesBuilder as WaveSamplesBuilder
from .loaders import ABCNotationLoader as ABCNotationLoader
from _typeshed import Incomplete
from arduino.app_peripherals.speaker import Speaker as Speaker
from arduino.app_utils import Logger as Logger, brick as brick
from collections import OrderedDict
from typing import Iterable

logger: Incomplete

class LRUDict(OrderedDict):
    """A dictionary-like object with a fixed size that evicts the least recently used items."""
    maxsize: Incomplete
    def __init__(self, maxsize: int = 128, *args, **kwargs) -> None: ...
    def __getitem__(self, key): ...
    def __setitem__(self, key, value) -> None: ...

class SoundGeneratorStreamer:
    SAMPLE_RATE: Incomplete
    A4_FREQUENCY: float
    SEMITONE_MAP: Incomplete
    NOTE_DURATTION: Incomplete
    A4_SEMITONE_INDEX: Incomplete
    time_signature: Incomplete
    def __init__(self, bpm: int = 120, time_signature: tuple = (4, 4), octaves: int = 8, wave_form: str = 'sine', master_volume: float = 1.0, sound_effects: list = None) -> None:
        '''Initialize the SoundGeneratorStreamer. Generates sound blocks for streaming, without internal playback.
        Args:
            bpm (int): The tempo in beats per minute for note duration calculations.
            time_signature (tuple): The time signature as (numerator, denominator).
            octaves (int): Number of octaves to generate notes for (starting from octave
                0 up to octaves-1).
            wave_form (str): The type of wave form to generate. Supported values
                are "sine" (default), "square", "triangle" and "sawtooth".
            master_volume (float): The master volume level (0.0 to 1.0).
            sound_effects (list, optional): List of sound effect instances to apply to the audio
                signal (e.g., [SoundEffect.adsr()]). See SoundEffect class for available effects.
        '''
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def set_wave_form(self, wave_form: str):
        '''
        Set the wave form type for sound generation.
        Args:
            wave_form (str): The type of wave form to generate. Supported values
                are "sine", "square", "triangle" and "sawtooth".
        '''
    def set_master_volume(self, volume: float):
        """
        Set the master volume level.
        Args:
            volume (float): Volume level (0.0 to 1.0).
        """
    def set_bpm(self, bpm: int):
        """
        Set the tempo in beats per minute.
        Args:
            bpm (int): Tempo in beats per minute.
        """
    def set_effects(self, effects: list):
        """
        Set the list of sound effects to apply to the audio signal.
        Args:
            effects (list): List of sound effect instances (e.g., [SoundEffect.adsr()]).
        """
    def play_polyphonic(self, notes: list[list[tuple[str, float]]], as_tone: bool = False, volume: float = None) -> tuple[bytes, float]:
        """Generate audio for multiple note sequences mixed together (polyphony).

        Produces multi-track audio by mixing a list of sequences, where each
        sequence is a list of (note, duration) tuples.

        Args:
            notes (list[list[tuple[str, float]]]): List of sequences, each a list of (note, duration) tuples.
            as_tone (bool): If True, interpret duration values as seconds instead of note fractions.
            volume (float, optional): Volume level (0.0 to 1.0). If None, uses master volume.

        Returns:
            tuple[np.ndarray, float]: The mixed audio block (float32) and its duration in seconds.
        """
    def play_chord(self, notes: list[str], note_duration: float | str = ..., volume: float = None) -> bytes:
        """Generate audio for a chord of simultaneous notes.

        Args:
            notes (list[str]): List of musical notes (e.g., ['A4', 'C#5', 'E5']).
            note_duration (float | str): Duration as a note fraction (like 1/4, 1/8) or symbol ('W', 'H', 'Q', etc.).
            volume (float, optional): Volume level (0.0 to 1.0). If None, uses master volume.

        Returns:
            np.ndarray: The audio block of the chord (float32).
        """
    def play(self, note: str, note_duration: float | str = ..., volume: float = None) -> bytes:
        """Generate audio samples for a single musical note.

        Args:
            note (str): The musical note to generate (e.g., 'A4', 'C#5', 'REST').
            note_duration (float | str): Duration as a note fraction (like 1/4, 1/8) or symbol ('W', 'H', 'Q', etc.).
            volume (float, optional): Volume level (0.0 to 1.0). If None, uses master volume.

        Returns:
            np.ndarray: The audio block (float32), or None if the note is invalid.
        """
    def play_tone(self, note: str, duration: float = 0.25, volume: float = None) -> bytes:
        """Generate audio samples for a note with duration in seconds.

        Unlike ``play()`` which interprets duration as a musical note fraction,
        this method takes the duration directly in seconds.

        Args:
            note (str): The musical note to generate (e.g., 'A4', 'C#5', 'REST').
            duration (float): Duration in seconds (default 0.25).
            volume (float, optional): Volume level (0.0 to 1.0). If None, uses master volume.

        Returns:
            np.ndarray: The audio block (float32), or None if the note is invalid.
        """
    def play_abc(self, abc_string: str, volume: float = None) -> Iterable[tuple[bytes, float]]:
        """Generate audio samples from an ABC notation string.

        Yields one audio block per note in the parsed ABC sequence.  The parser
        is ABC 2.1 standard compliant (key signatures, accidentals, tuplets,
        broken rhythm, multimeasure rests, etc.).  See
        :class:`ABCNotationLoader` for the full feature list and limitations.

        Args:
            abc_string (str): ABC notation string defining the sequence of notes.
            volume (float, optional): Volume level (0.0 to 1.0). If None, uses master volume.

        Yields:
            tuple[np.ndarray, float]: Audio block (float32) and its duration in seconds.
        """
    def play_wav(self, wav_file: str) -> tuple[bytes, float]:
        """Load a WAV file and return its raw PCM data.

        Results are cached (up to 250 KB total) for repeated playback.

        Args:
            wav_file (str): The WAV audio file path.

        Returns:
            tuple[bytes, float]: Raw PCM audio data and its duration in seconds.
        """

class SoundGenerator(SoundGeneratorStreamer):
    external_speaker: bool
    def __init__(self, output_device: Speaker = None, bpm: int = 120, time_signature: tuple = (4, 4), octaves: int = 8, wave_form: str = 'sine', master_volume: float = 1.0, sound_effects: list = None) -> None:
        '''Initialize the SoundGenerator.

        Args:
            output_device (Speaker, optional): The output device to play sound through.
                When omitted, SoundGenerator creates an internal shared speaker so
                multiple instances can overlap playback on the same device.
            bpm (int): The tempo in beats per minute for note duration calculations.
            time_signature (tuple): The time signature as (numerator, denominator).
            octaves (int): Number of octaves to generate notes for (starting from octave
                0 up to octaves-1).
            wave_form (str): The type of wave form to generate. Supported values
                are "sine" (default), "square", "triangle" and "sawtooth".
            master_volume (float): The master volume level (0.0 to 1.0).
            sound_effects (list, optional): List of sound effect instances to apply to the audio
                signal (e.g., [SoundEffect.adsr()]). See SoundEffect class for available effects.
        '''
    def start(self) -> None:
        """Start the sound generator and its internal speaker (if not external)."""
    def stop(self) -> None:
        """Stop playback, halt any running sequence, and close the internal speaker."""
    def set_master_volume(self, volume: float):
        """
        Set the master volume level.
        Args:
            volume (float): Volume level (0.0 to 1.0).
        """
    def set_effects(self, effects: list):
        """
        Set the list of sound effects to apply to the audio signal.
        Args:
            effects (list): List of sound effect instances (e.g., [SoundEffect.adsr()]).
        """
    def play_polyphonic(self, notes: list[list[tuple[str, float]]], as_tone: bool = False, volume: float = None, block: bool = False):
        """
        Play multiple sequences of musical notes simultaneously (poliphony).
        It is possible to play multi track music by providing a list of sequences,
        where each sequence is a list of tuples (note, duration).
        Duration is in notes fractions (e.g., 1/4 for quarter note).
        Args:
            notes (list[list[tuple[str, float]]]): List of sequences, each sequence is a list of tuples (note, duration).
            as_tone (bool): If True, play as tones, considering duration in seconds
            volume (float, optional): Volume level (0.0 to 1.0). If None, uses master volume.
            block (bool): If True, block until the entire sequence has been played.
        """
    def play_composition(self, composition: MusicComposition, block: bool | None = None, loop: bool = False, play_for: float | None = None):
        """
        Play a MusicComposition object.

        Configures the SoundGenerator with the composition's settings and plays
        the sequence using play_step_sequence.

        The composition format is interpreted as a list of steps, where each step
        is a list of (note, duration) tuples to play simultaneously.

        Args:
            composition (MusicComposition): The composition to play.
            block (bool | None): Controls whether this call waits for playback.
                - True: wait until the current playback session ends. When
                  ``loop=True`` and ``play_for`` is not set, this may block
                  indefinitely until ``stop_sequence()`` or ``stop()`` is called
                  from another thread.
                - False: start playback and return immediately.
                - None: choose automatically based on the playback mode. Finite
                  playback blocks, infinite looping returns immediately, and
                  timed looping (``loop=True`` with ``play_for`` set) blocks
                  until the timed stop completes. This is the recommended
                  default for most scripts and examples.
            loop (bool): If True, loop the composition until ``stop_sequence()``
                is called or until ``play_for`` expires.
            play_for (float | None): When looping, stop automatically after the
                given number of seconds. Requires ``loop=True``.
        """
    def play_chord(self, notes: list[str], note_duration: float | str = ..., volume: float = None, block: bool = False):
        """
        Play a chord consisting of multiple musical notes simultaneously for a specified duration and volume.
        Args:
            notes (list[str]): List of musical notes to play (e.g., ['A4', 'C#5', 'E5']).
            note_duration (float | str): Duration of the chord as a float (like 1/4, 1/8) or a symbol ('W', 'H', 'Q', etc.).
            volume (float, optional): Volume level (0.0 to 1.0). If None, uses master volume.
            block (bool): If True, block until the entire chord has been played.
        """
    def play(self, note: str, note_duration: float | str = ..., volume: float = None, block: bool = False):
        """
        Play a musical note for a specified duration and volume.
        Args:
            note (str): The musical note to play (e.g., 'A4', 'C#5', 'REST').
            note_duration (float | str): Duration of the note as a float (like 1/4, 1/8) or a symbol ('W', 'H', 'Q', etc.).
            volume (float, optional): Volume level (0.0 to 1.0). If None, uses master volume.
            block (bool): If True, block until the entire note has been played.
        """
    def play_tone(self, note: str, duration: float = 0.25, volume: float = None, block: bool = False):
        """Play a musical note with duration specified in seconds.

        Unlike ``play()`` which interprets duration as a musical note fraction,
        this method takes the duration directly in seconds.

        Args:
            note (str): The musical note to play (e.g., 'A4', 'C#5', 'REST').
            duration (float): Duration in seconds (default 0.25).
            volume (float, optional): Volume level (0.0 to 1.0). If None, uses master volume.
            block (bool): If True, block until the entire note has been played.
        """
    def play_abc(self, abc_string: str, volume: float = None, block: bool = False):
        """Play a sequence of musical notes defined in ABC notation.

        The parser is ABC 2.1 standard compliant (key signatures, accidentals,
        tuplets, broken rhythm, multimeasure rests, etc.).  See
        :class:`ABCNotationLoader` for the full feature list and limitations.

        Args:
            abc_string (str): ABC notation string defining the sequence of notes.
            volume (float, optional): Volume level (0.0 to 1.0). If None, uses master volume.
            block (bool): If True, block until the entire sequence has been played.
        """
    def play_wav(self, wav_file: str, block: bool = False):
        """Play a WAV audio file through the output device.

        Args:
            wav_file (str): The WAV audio file path.
            block (bool): If True, block until the entire WAV file has been played.
        """
    def play_step_sequence(self, sequence: list[list[str]], note_duration: float | str = ..., bpm: int = None, loop: bool = False, on_step_callback: callable = None, on_complete_callback: callable = None, volume: float = None):
        '''
        Play a step sequence with automatic timing.
        This method handles all the complexity of buffer management internally,
        allowing the app to simply provide the sequence and let the brick manage playback.

        Args:
            sequence (list[list[str]]): List of steps, where each step is a list of notes.
                Empty list or None means REST (silence) for that step.
                Example: [[\'C4\'], [\'E4\', \'G4\'], [], [\'C5\']]
            note_duration (float | str): Duration of each step as a float (like 1/16) or symbol (\'E\', \'Q\', etc.).
            bpm (int, optional): Tempo in beats per minute. If None, uses instance BPM.
            loop (bool): If True, the sequence will loop indefinitely until stop_sequence() is called.
            on_step_callback (callable, optional): Callback function called for each step.
                Signature: on_step_callback(current_step: int, total_steps: int)
            on_complete_callback (callable, optional): Callback function called when sequence completes (only if loop=False).
                Signature: on_complete_callback()
            volume (float, optional): Volume level (0.0 to 1.0). If None, uses master volume.

        Returns:
            None: Returns immediately after starting playback thread.

        Example:
            ```python
            # Simple melody with chords
            sequence = [
                ["C4"],  # Step 0: Single note
                ["E4", "G4"],  # Step 1: Chord
                [],  # Step 2: REST
                ["C5"],  # Step 3: High note
            ]
            sound_gen.play_step_sequence(sequence, note_duration=1 / 16, bpm=120)
            ```
        '''
    def stop_sequence(self) -> None:
        """
        Stop the currently playing step sequence.

        Signals the playback thread to stop and closes the internal speaker to
        immediately drop any pending audio in the ALSA buffer.  The speaker is
        transparently restarted on the next play call via _ensure_speaker_ready.
        """
    def is_sequence_playing(self) -> bool:
        """
        Check if a step sequence is currently playing.

        Returns:
            bool: True if a sequence is playing, False otherwise.
        """
