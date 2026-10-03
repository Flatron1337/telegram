from __future__ import annotations

import io

from PIL import Image

from bot.models.color import PaletteTheme
from bot.services.theme_generators.android_keys import (
    ACCENT_ALT_KEYS,
    ACCENT_KEYS,
    ALPHA_SPECS,
    BACKGROUND_KEYS,
    CONTRAST_TEXT_KEYS,
    SURFACE_KEYS,
    TEXT_PRIMARY_KEYS,
    TEXT_SECONDARY_KEYS,
    TRANSPARENT_KEYS,
)


class AndroidThemeGenerator:
    """Generates Telegram Android themes (.attheme files and packages) with full key coverage."""

    def generate_theme_text(
        self,
        theme: PaletteTheme,
        name: str = "Custom Theme",
        author: str = "@theme_creator1337bot",
    ) -> str:
        """Render standard .attheme key-value mappings using signed 32-bit ARGB integers."""
        entries = self._build_theme_entries(theme)
        headers = [
            f"#name={name}",
            f"#author={author}",
            f"#dark={'true' if theme.is_dark else 'false'}",
        ]
        lines = [f"{key}={val}" for key, val in sorted(entries.items())]
        return "\n".join(headers + lines) + "\n"

    def _build_theme_entries(self, theme: PaletteTheme) -> dict[str, int]:
        entries = self._build_base_role_entries(theme)
        entries.update(self._build_alpha_entries(theme))
        entries.update(self._build_bubble_entries(theme))
        entries.update(self._build_component_entries(theme))
        return entries

    def _build_base_role_entries(self, theme: PaletteTheme) -> dict[str, int]:
        surf = theme.surface.int_argb
        bg = theme.background.int_argb
        txt = theme.text_primary.int_argb
        txt_sec = theme.text_secondary.int_argb
        accent = theme.accent.int_argb
        accent_alt = (
            theme.accent.lighten(0.08).int_argb
            if theme.is_dark
            else theme.accent.darken(0.08).int_argb
        )
        acc_txt = theme.accent_text.int_argb

        entries: dict[str, int] = {}
        for key in SURFACE_KEYS:
            entries[key] = surf
        for key in BACKGROUND_KEYS:
            entries[key] = bg
        for key in TEXT_PRIMARY_KEYS:
            entries[key] = txt
        for key in TEXT_SECONDARY_KEYS:
            entries[key] = txt_sec
        for key in ACCENT_KEYS:
            entries[key] = accent
        for key in ACCENT_ALT_KEYS:
            entries[key] = accent_alt
        for key in CONTRAST_TEXT_KEYS:
            entries[key] = acc_txt
        for key in TRANSPARENT_KEYS:
            entries[key] = 0

        return entries

    def _build_alpha_entries(self, theme: PaletteTheme) -> dict[str, int]:
        role_colors = {
            "surface": theme.surface,
            "text_primary": theme.text_primary,
            "accent": theme.accent,
            "out_bubble": theme.out_bubble,
            "text_secondary": theme.text_secondary,
        }
        entries: dict[str, int] = {}
        for key, role, alpha in ALPHA_SPECS:
            color = role_colors.get(role, theme.text_primary)
            entries[key] = color.with_alpha_int(alpha)
        return entries

    def _build_bubble_entries(self, theme: PaletteTheme) -> dict[str, int]:
        accent = theme.accent.int_argb
        acc_txt = theme.accent_text.int_argb
        in_alpha = getattr(theme, "in_bubble_alpha", 255)
        out_alpha = getattr(theme, "out_bubble_alpha", 255)
        in_bg = theme.in_bubble.with_alpha_int(in_alpha)
        in_txt = theme.in_bubble_text.int_argb
        in_date = theme.in_bubble_subtext.int_argb
        out_bg = theme.out_bubble.with_alpha_int(out_alpha)
        out_txt = theme.out_bubble_text.int_argb
        out_date = theme.out_bubble_subtext.int_argb

        in_sel_alpha = max(0, min(255, in_alpha - 30))
        out_sel_alpha = max(0, min(255, out_alpha - 30))

        return {
            # In-bubbles & audio
            "chat_inBubble": in_bg,
            "chat_inBubbleSelected": theme.in_bubble.with_alpha_int(in_sel_alpha),
            "chat_inBubbleShadow": 0,
            "chat_inText": in_txt,
            "chat_messageTextIn": in_txt,
            "chat_inTimeText": in_date,
            "chat_inTimeSelectedText": in_date,
            "chat_inAudioProgress": accent,
            # Out-bubbles & audio
            "chat_outBubble": out_bg,
            "chat_outBubbleSelected": theme.out_bubble.with_alpha_int(out_sel_alpha),
            "chat_outBubbleShadow": 0,
            "chat_outText": out_txt,
            "chat_messageTextOut": out_txt,
            "chat_outTimeText": out_date,
            "chat_outTimeSelectedText": out_date,
            "chat_outAudioProgress": acc_txt,
        }

    def _build_component_entries(self, theme: PaletteTheme) -> dict[str, int]:
        surf = theme.surface.int_argb
        surf_var = theme.surface_variant.int_argb
        txt = theme.text_primary.int_argb
        txt_sec = theme.text_secondary.int_argb
        accent = theme.accent.int_argb
        acc_txt = theme.accent_text.int_argb
        divider = theme.divider.int_argb

        # WCAG 2.1 contrast enforcement for toolbar & menus (min ratio 4.5:1)
        ab_bg = theme.background
        ab_icon = theme.accent.ensure_contrast(ab_bg, 4.5).int_argb
        ab_title = theme.text_primary.ensure_contrast(ab_bg, 4.5).int_argb
        ab_subtitle = theme.text_secondary.ensure_contrast(ab_bg, 4.5).int_argb

        submenu_bg = theme.surface
        submenu_item = theme.text_primary.ensure_contrast(submenu_bg, 4.5).int_argb
        submenu_icon = theme.text_secondary.ensure_contrast(submenu_bg, 4.5).int_argb

        return {
            # Action Bar & Submenu (WCAG 2.1 compliant)
            "actionBarDefault": theme.background.int_argb,
            "actionBarDefaultIcon": ab_icon,
            "actionBarDefaultSearch": ab_icon,
            "actionBarDefaultTitle": ab_title,
            "actionBarDefaultSubtitle": ab_subtitle,
            "actionBarActionModeDefault": surf,
            "actionBarActionModeDefaultIcon": ab_icon,
            "actionBarDefaultSubmenuBackground": surf,
            "actionBarDefaultSubmenuItem": submenu_item,
            "actionBarDefaultSubmenuItemIcon": submenu_icon,
            "dialogBackground": surf,
            "dialogButton": accent,
            "dialogTextBlack": txt,
            "dialogTextGray": txt_sec,
            "dialogButtonSelector": surf_var,
            # Folder tabs
            "actionBarTabLine": accent,
            "actionBarTabActiveText": accent,
            "actionBarTabUnactiveText": txt_sec,
            "actionBarTabSelector": surf_var,
            "actionBarTabUnread": accent,
            "actionBarTabUnreadText": acc_txt,
            "actionBarTabUnreadMuted": surf_var,
            "actionBarTabUnreadMutedText": txt_sec,
            # Reactions & modern components
            "chat_reactions_active": accent,
            "chat_reactions_badge": accent,
            "chat_reactions_bubble": surf,
            "chat_reactionsContainerBackground": surf,
            "reactions_bubbleBackground": surf,
            "reactions_bubbleBorder": divider,
            "reactions_bubbleText": txt,
            "profile_verifiedCheck": accent,
            "profile_verifiedBackground": accent,
            "chat_replyLine": accent,
            # Switches & controls
            "divider": divider,
            "listSelectorSDK21": surf_var,
            "switchTrack": divider,
            "switchTrackChecked": theme.accent.with_alpha_int(128),
            "switchThumb": surf,
            "switchThumbChecked": accent,
            # Avatar placeholders
            "avatar_backgroundBlue": accent,
            "avatar_backgroundCyan": accent,
            "avatar_backgroundGreen": accent,
            "avatar_backgroundOrange": accent,
            "avatar_backgroundPink": accent,
            "avatar_backgroundRed": accent,
            "avatar_backgroundViolet": accent,
            "avatar_text": acc_txt,
        }

    def generate_theme_package(
        self,
        theme: PaletteTheme,
        source_image: Image.Image | None = None,
        name: str = "Custom Theme",
        author: str = "@theme_creator1337bot",
    ) -> bytes:
        """Create .attheme file with embedded wallpaper using standard WPS/WPE markers."""
        theme_content = self.generate_theme_text(
            theme, name=name, author=author
        ).encode("utf-8")

        if source_image is None:
            return theme_content

        img = source_image.convert("RGB")
        max_side = 2560
        if max(img.width, img.height) > max_side:
            img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

        wp_buf = io.BytesIO()
        img.save(wp_buf, format="JPEG", quality=88, optimize=True)

        return theme_content + b"WPS\n" + wp_buf.getvalue() + b"\nWPE\n"
