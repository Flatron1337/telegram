from __future__ import annotations

import io
import zipfile

from PIL import Image

from bot.models.color import PaletteTheme
from bot.services.theme_generators.tdesktop_keys import (
    EXTRA_TDESKTOP_SPECS,
    TDESKTOP_PALETTE_SPECS,
)


class TDesktopThemeGenerator:
    """Generates Telegram Desktop themes (.tdesktop-theme packages) with full key coverage."""

    def generate_palette_text(self, theme: PaletteTheme) -> str:
        """Render the complete colors.tdesktop-palette string with correct dependency order."""
        entries = self._build_palette_entries(theme)
        lines = [f"{key}: {val};" for key, val in entries.items()]
        return "// Telegram Desktop theme palette\n" + "\n".join(lines) + "\n"

    def _build_palette_entries(self, theme: PaletteTheme) -> dict[str, str]:
        over_tint = 0.06 if theme.is_dark else 0.04
        surf_over = (
            theme.surface.lighten(over_tint).hex
            if theme.is_dark
            else theme.surface.darken(over_tint).hex
        )
        accent_over = (
            theme.accent.darken(0.08).hex if theme.is_dark else theme.accent.lighten(0.08).hex
        )

        in_alpha = getattr(theme, "in_bubble_alpha", 255)
        out_alpha = getattr(theme, "out_bubble_alpha", 255)
        in_bubble_val = (
            theme.in_bubble.with_alpha_hex(in_alpha)
            if in_alpha < 255
            else theme.in_bubble.hex
        )
        out_bubble_val = (
            theme.out_bubble.with_alpha_hex(out_alpha)
            if out_alpha < 255
            else theme.out_bubble.hex
        )

        role_map = {
            "SURF": theme.surface.hex,
            "TXT": theme.text_primary.hex,
            "TXT_SEC": theme.text_secondary.hex,
            "ACCENT": theme.accent.hex,
            "ACCENT_OVER": accent_over,
            "WHITE": theme.accent_text.hex,
            "IN_BUBBLE": in_bubble_val,
            "OUT_BUBBLE": out_bubble_val,
            "SURF_OVER": surf_over,
        }


        entries: dict[str, str] = {}
        for key, role in TDESKTOP_PALETTE_SPECS + EXTRA_TDESKTOP_SPECS:
            if key in entries:
                continue
            if role.startswith("RAW:"):
                entries[key] = role[4:]
            else:
                entries[key] = role_map.get(role, theme.text_primary.hex)

        return entries

    def generate_theme_package(
        self,
        theme: PaletteTheme,
        source_image: Image.Image | None = None,
    ) -> bytes:
        """Build a standard .tdesktop-theme ZIP archive."""
        palette_content = self.generate_palette_text(theme).encode("utf-8")
        buf = io.BytesIO()

        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("colors.tdesktop-palette", palette_content)
            archive.writestr("colors.tdesktop-theme", palette_content)

            if source_image is not None:
                img = source_image.convert("RGB")
                max_side = 2560
                if max(img.width, img.height) > max_side:
                    img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

                wp_buf = io.BytesIO()
                img.save(wp_buf, format="JPEG", quality=88, optimize=True)
                archive.writestr("background.jpg", wp_buf.getvalue())

        return buf.getvalue()
