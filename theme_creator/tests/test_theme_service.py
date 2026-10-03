from __future__ import annotations

import asyncio
import io
import zipfile

from PIL import Image

from bot.services.theme_service import ThemeService


def test_theme_service_process_image_async() -> None:
    async def _run() -> None:
        service = ThemeService()

        # Generate synthetic in-memory image
        img = Image.new("RGB", (100, 100), (20, 150, 220))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        raw_bytes = buf.getvalue()

        result = await service.process_image_async(raw_bytes)

        assert result.dark_preview_png.startswith(b"\x89PNG")
        assert result.light_preview_png.startswith(b"\x89PNG")

        # Verify that TDesktop archive is a valid zip containing expected files
        with zipfile.ZipFile(io.BytesIO(result.tdesktop_dark)) as arc:
            assert "colors.tdesktop-palette" in arc.namelist()
            assert "background.jpg" in arc.namelist()

        # Verify Android theme package format (native WPS/WPE marker)
        assert b"chat_inBubble=" in result.android_dark
        assert b"WPS\n" in result.android_dark
        assert b"\nWPE\n" in result.android_dark

        # Verify pure lightweight themes (no wallpaper)
        assert result.android_dark_pure is not None
        assert b"chat_inBubble=" in result.android_dark_pure
        assert b"WPS\n" not in result.android_dark_pure
        assert len(result.android_dark_pure) < 40_000

        assert result.tdesktop_dark_pure is not None
        with zipfile.ZipFile(io.BytesIO(result.tdesktop_dark_pure)) as arc_pure:
            assert "colors.tdesktop-palette" in arc_pure.namelist()
            assert "background.jpg" not in arc_pure.namelist()

        # Verify iOS theme payload (.tgios-theme YAML)
        assert b"basedOn: day" in result.ios_dark
        assert b"dark: true" in result.ios_dark
        assert b"basedOn: day" in result.ios_light
        assert b"dark: false" in result.ios_light

    asyncio.run(_run())


def test_theme_service_process_preset() -> None:
    async def _run() -> None:
        service = ThemeService()
        result = await service.process_preset_async("cyberpunk_rem")

        assert result.dark_preview_png.startswith(b"\x89PNG")
        assert result.light_preview_png.startswith(b"\x89PNG")
        assert b"Cyberpunk Rem Dark" in result.android_dark
        assert b"WPS\n" not in result.android_dark
        assert b"Cyberpunk Rem Dark" in result.ios_dark
        assert b"Cyberpunk Rem Light" in result.ios_light
        assert result.dark_theme.accent.hex == "#00e5ff"

    asyncio.run(_run())


