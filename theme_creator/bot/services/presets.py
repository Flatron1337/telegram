"""Built-in curated theme presets for Telegram Desktop and Android."""

from __future__ import annotations

from dataclasses import dataclass

from bot.models.color import Color, PaletteTheme


@dataclass(frozen=True, slots=True)
class ThemePreset:
    id: str
    title: str
    emoji: str
    description: str
    dark_theme: PaletteTheme
    light_theme: PaletteTheme


def _create_cyberpunk_rem_preset() -> ThemePreset:
    dark = PaletteTheme(
        is_dark=True,
        background=Color(11, 12, 16),
        surface=Color(20, 24, 33),
        surface_variant=Color(31, 40, 51),
        text_primary=Color(240, 246, 252),
        text_secondary=Color(139, 148, 158),
        accent=Color(0, 229, 255),
        accent_text=Color(0, 0, 0),
        out_bubble=Color(14, 56, 82),
        out_bubble_text=Color(255, 255, 255),
        out_bubble_subtext=Color(165, 214, 255),
        in_bubble=Color(22, 27, 34),
        in_bubble_text=Color(240, 246, 252),
        in_bubble_subtext=Color(139, 148, 158),
        divider=Color(33, 38, 45),
    )
    light = PaletteTheme(
        is_dark=False,
        background=Color(240, 246, 250),
        surface=Color(255, 255, 255),
        surface_variant=Color(222, 234, 242),
        text_primary=Color(15, 23, 42),
        text_secondary=Color(100, 116, 139),
        accent=Color(0, 160, 200),
        accent_text=Color(255, 255, 255),
        out_bubble=Color(218, 244, 252),
        out_bubble_text=Color(8, 47, 73),
        out_bubble_subtext=Color(2, 132, 199),
        in_bubble=Color(255, 255, 255),
        in_bubble_text=Color(15, 23, 42),
        in_bubble_subtext=Color(100, 116, 139),
        divider=Color(226, 232, 240),
    )
    return ThemePreset(
        id="cyberpunk_rem",
        title="Cyberpunk Rem",
        emoji="💙",
        description="Неоново-голубой киберпанк на обсидианово-чёрном фоне",
        dark_theme=dark,
        light_theme=light,
    )


def _create_cyberpunk_ram_preset() -> ThemePreset:
    dark = PaletteTheme(
        is_dark=True,
        background=Color(11, 12, 16),
        surface=Color(25, 18, 28),
        surface_variant=Color(42, 24, 46),
        text_primary=Color(245, 240, 246),
        text_secondary=Color(168, 145, 171),
        accent=Color(255, 42, 133),
        accent_text=Color(255, 255, 255),
        out_bubble=Color(79, 18, 48),
        out_bubble_text=Color(255, 255, 255),
        out_bubble_subtext=Color(255, 179, 212),
        in_bubble=Color(28, 20, 31),
        in_bubble_text=Color(245, 240, 246),
        in_bubble_subtext=Color(168, 145, 171),
        divider=Color(48, 30, 54),
    )
    light = PaletteTheme(
        is_dark=False,
        background=Color(253, 242, 248),
        surface=Color(255, 255, 255),
        surface_variant=Color(252, 231, 243),
        text_primary=Color(30, 15, 25),
        text_secondary=Color(131, 24, 67),
        accent=Color(219, 39, 119),
        accent_text=Color(255, 255, 255),
        out_bubble=Color(251, 207, 232),
        out_bubble_text=Color(131, 24, 67),
        out_bubble_subtext=Color(190, 24, 93),
        in_bubble=Color(255, 255, 255),
        in_bubble_text=Color(30, 15, 25),
        in_bubble_subtext=Color(157, 23, 77),
        divider=Color(244, 215, 230),
    )
    return ThemePreset(
        id="cyberpunk_ram",
        title="Cyberpunk Ram",
        emoji="💖",
        description="Неоново-розовый глитч-стиль с глубокими пурпурными оттенками",
        dark_theme=dark,
        light_theme=light,
    )


def _create_amoled_black_preset() -> ThemePreset:
    dark = PaletteTheme(
        is_dark=True,
        background=Color(0, 0, 0),
        surface=Color(18, 18, 18),
        surface_variant=Color(32, 32, 32),
        text_primary=Color(255, 255, 255),
        text_secondary=Color(160, 160, 160),
        accent=Color(64, 196, 255),
        accent_text=Color(0, 0, 0),
        out_bubble=Color(35, 35, 35),
        out_bubble_text=Color(255, 255, 255),
        out_bubble_subtext=Color(190, 190, 190),
        in_bubble=Color(20, 20, 20),
        in_bubble_text=Color(255, 255, 255),
        in_bubble_subtext=Color(160, 160, 160),
        divider=Color(28, 28, 28),
    )
    light = PaletteTheme(
        is_dark=False,
        background=Color(255, 255, 255),
        surface=Color(248, 249, 250),
        surface_variant=Color(233, 236, 239),
        text_primary=Color(0, 0, 0),
        text_secondary=Color(108, 117, 125),
        accent=Color(0, 122, 255),
        accent_text=Color(255, 255, 255),
        out_bubble=Color(227, 242, 253),
        out_bubble_text=Color(0, 0, 0),
        out_bubble_subtext=Color(33, 150, 243),
        in_bubble=Color(241, 243, 245),
        in_bubble_text=Color(0, 0, 0),
        in_bubble_subtext=Color(108, 117, 125),
        divider=Color(222, 226, 230),
    )
    return ThemePreset(
        id="amoled_black",
        title="AMOLED Pure Black",
        emoji="🖤",
        description="100% истинный чёрный фон для экономии батареи и идеального контраста",
        dark_theme=dark,
        light_theme=light,
    )


def _create_minimalist_pastel_preset() -> ThemePreset:
    dark = PaletteTheme(
        is_dark=True,
        background=Color(22, 20, 31),
        surface=Color(31, 27, 44),
        surface_variant=Color(45, 40, 62),
        text_primary=Color(243, 240, 255),
        text_secondary=Color(165, 158, 186),
        accent=Color(187, 155, 255),
        accent_text=Color(20, 10, 35),
        out_bubble=Color(54, 42, 82),
        out_bubble_text=Color(255, 255, 255),
        out_bubble_subtext=Color(215, 195, 255),
        in_bubble=Color(36, 31, 51),
        in_bubble_text=Color(243, 240, 255),
        in_bubble_subtext=Color(165, 158, 186),
        divider=Color(48, 42, 69),
    )
    light = PaletteTheme(
        is_dark=False,
        background=Color(248, 247, 252),
        surface=Color(255, 255, 255),
        surface_variant=Color(238, 235, 247),
        text_primary=Color(34, 30, 48),
        text_secondary=Color(114, 106, 138),
        accent=Color(126, 87, 194),
        accent_text=Color(255, 255, 255),
        out_bubble=Color(237, 231, 246),
        out_bubble_text=Color(49, 27, 146),
        out_bubble_subtext=Color(126, 87, 194),
        in_bubble=Color(255, 255, 255),
        in_bubble_text=Color(34, 30, 48),
        in_bubble_subtext=Color(114, 106, 138),
        divider=Color(228, 224, 240),
    )
    return ThemePreset(
        id="minimalist_pastel",
        title="Minimalist Pastel",
        emoji="🌸",
        description="Нежные пастельные оттенки лаванды с мягким визуальным балансом",
        dark_theme=dark,
        light_theme=light,
    )


THEME_PRESETS: dict[str, ThemePreset] = {
    "cyberpunk_rem": _create_cyberpunk_rem_preset(),
    "cyberpunk_ram": _create_cyberpunk_ram_preset(),
    "amoled_black": _create_amoled_black_preset(),
    "minimalist_pastel": _create_minimalist_pastel_preset(),
}
