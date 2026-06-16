from _typeshed import Incomplete
from arduino.app_utils.logger import Logger as Logger

logger: Incomplete

class ABCNotationLoader:
    '''ABC notation parser — ABC 2.1 standard compliant.

    Parses ABC notation strings into ``(note, duration_in_seconds)`` tuples
    suitable for playback through the SoundGenerator brick.

    Supported ABC 2.1 features:
        - Information fields: ``X:``, ``T:``, ``M:``, ``L:``, ``Q:``, ``K:``
        - Key signatures: all major/minor keys, modes (dorian … locrian),
          ``K:none``, ``K:Hp``/``HP``, ``exp`` (explicit), inline accidental
          overrides (e.g. ``K:D =f ^c``)
        - Accidentals: prefix ``^``, ``^^``, ``_``, ``__``, ``=`` with
          bar-local propagation (pitch-class scope)
        - Octave modifiers: ``\'`` (up) and ``,`` (down), case-based octave
        - Duration notation: integer multiplier, ``/n``, ``n/m``, repeated
          slashes (``//`` = ``/4``, ``///`` = ``/8``)
        - Rests: ``z`` (visible), ``x`` (invisible), ``Z``/``X``
          (multimeasure, duration computed from ``M:``)
        - Broken rhythm: ``>``, ``>>``, ``<``, ``<<``
        - Tuplets: ``(p``, ``(p:q``, ``(p:q:r``
        - Chord brackets: ``[CEG]`` (flattened to sequential notes)
        - Grace notes ``{abc}``, decorations ``!ff!`` / ``+fermata+``,
          chord annotations ``"Cm"`` — stripped during pre-processing
        - Non-standard extension: ``%%transpose`` (octave shift)
        - Legacy extension: suffix ``#`` / ``b`` accidentals

    Known limitations (not implemented):
        - Multi-voice scores (``V:`` fields)
        - Repeat structures (``|:`` … ``:|``, numbered endings)
        - Ties (``-``) and slurs (``()``)
        - Inline information fields (``[K:Am]``)
        - ``%%propagate-accidentals`` directive (fixed pitch-class scope)
        - ``K:`` clef / transpose parameters
        - ``w:`` lyrics, ``s:`` symbol lines
    '''
    NOT_HANDLED_RESERVED_LINES: str
    @staticmethod
    def parse_abc_notation(abc_string: str, default_octave: int = 4) -> tuple[dict, list[tuple[str, float]]]:
        """Parse an ABC notation string into ``(note, duration_in_seconds)`` tuples.

        See :class:`ABCNotationLoader` for the full list of supported ABC 2.1
        features and known limitations.

        Args:
            abc_string (str): ABC notation string.
            default_octave (int): Default octave for uppercase notes (C4).

        Returns:
            Tuple[dict, List[Tuple[str, float]]]: Metadata dictionary and list
                of (note, duration) tuples.
        """
