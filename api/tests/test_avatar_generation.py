from __future__ import annotations

from api.services import avatar


def test_public_avatar_url_uses_api_static_route(monkeypatch):
    monkeypatch.setenv("PUBLIC_API_URL", "https://api.example.com/")
    image_uri = (avatar.GENERATED_AVATAR_DIR / "lunatides.jpg").resolve().as_uri()

    url = avatar._public_avatar_url(image_uri)

    assert url == "https://api.example.com/generated/avatars/lunatides.jpg"
