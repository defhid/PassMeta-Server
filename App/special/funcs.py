__all__ = (
    'loc',
)


def loc(default: str, ru: str) -> dict[str, str]:
    return {
        "default": default,
        "ru": ru,
    }
