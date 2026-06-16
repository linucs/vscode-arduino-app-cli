from _typeshed import Incomplete
from arduino.app_utils import Logger as Logger

logger: Incomplete

class JSONParser:
    silent: Incomplete
    def __init__(self, silent: bool = False) -> None: ...
    def parse(self, item: str) -> dict: ...
    def process(self, item): ...
