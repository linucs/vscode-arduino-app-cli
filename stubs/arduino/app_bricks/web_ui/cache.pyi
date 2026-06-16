from starlette.responses import Response as Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope as Scope

class NonCachedStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response: ...
