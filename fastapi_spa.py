import os
from typing import Tuple

from fastapi.staticfiles import StaticFiles


class SinglePageApplication(StaticFiles):
    def __init__(self, directory: os.PathLike, index="index.html") -> None:
        self.index = index
        super().__init__(directory=directory, packages=None, html=True, check_dir=True)

    async def lookup_path(self, path: str) -> Tuple[str, os.stat_result]:
        """Returns a static file if one exists at the requested path, or falls back to
        serving the index if not (preserving all path information)."""
        full_path, stat_result = await super().lookup_path(path)
        if stat_result is None:
            return await super().lookup_path(self.index)

        return (full_path, stat_result)
