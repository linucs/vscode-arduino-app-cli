from _typeshed import Incomplete
from dataclasses import dataclass

ASREventType: Incomplete
ASREventTypeValues: Incomplete

@dataclass(frozen=True)
class ASREvent:
    type: ASREventType
    data: str | None = ...
