from urllib.parse import urlparse

from rest_framework import serializers


def validate_youtube_only(value: str) -> None:
    """
    Разрешаем ссылки только на youtube.com (включая поддомены вроде www.youtube.com).
    Любые другие домены запрещены.
    """
    if not value:
        return

    parsed = urlparse(value)
    netloc = (parsed.netloc or "").lower()

    # URLField может дать netloc с портом: youtube.com:443
    host = netloc.split(":")[0]

    if not host.endswith("youtube.com"):
        raise serializers.ValidationError("Разрешены ссылки только на youtube.com.")
