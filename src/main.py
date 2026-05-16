from __future__ import annotations

import uvicorn

from src.core.config import settings


def main() -> None:
    uvicorn.run("src.api.server:app", host=settings.app.host, port=settings.app.port, reload=False)


if __name__ == "__main__":
    main()

