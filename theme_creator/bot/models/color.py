from __future__ import annotations

from dataclasses import dataclass


def _hsl_to_rgb(hue: float, saturation: float, lightness: float) -> tuple[int, int, int]:
    h = hue % 1.0
    s = max(0.0, min(1.0, saturation))
    light = max(0.0, min(1.0, lightness))

    if s == 0.0:
        val = round(light * 255)
        return val, val, val

    c = (1.0 - abs(2.0 * light - 1.0)) * s
    x = c * (1.0 - abs((h * 6.0) % 2.0 - 1.0))
    m = light - c / 2.0

    sector = int(h * 6.0)
    sector_map = [
        (c, x, 0.0),
        (x, c, 0.0),
        (0.0, c, x),
        (0.0, x, c),
        (x, 0.0, c),
        (c, 0.0, x),
    ]
    r_f, g_f, b_f = sector_map[min(sector, 5)]
    return (
        round((r_f + m) * 255),
        round((g_f + m) * 255),
        round((b_f + m) * 255),
    )


def _rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    r_f, g_f, b_f = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r_f, g_f, b_f)
    min_c = min(r_f, g_f, b_f)
    delta = max_c - min_c
    lightness = (max_c + min_c) / 2.0

    if delta == 0.0:
        return 0.0, 0.0, lightness

    saturation = delta / (2.0 - max_c - min_c) if lightness > 0.5 else delta / (max_c + min_c)

    if max_c == r_f:
        hue = ((g_f - b_f) / delta) % 6.0
    elif max_c == g_f:
        hue = ((b_f - r_f) / delta) + 2.0
    else:
        hue = ((r_f - g_f) / delta) + 4.0

    return (hue / 6.0) % 1.0, saturation, lightness


@dataclass(frozen=True, slots=True)
class Color:
    """Represents an 8-bit sRGB color with color space conversions and contrast utilities."""

    r: int
    g: int
    b: int

    def __post_init__(self) -> None:
        for channel_name, val in (("r", self.r), ("g", self.g), ("b", self.b)):
            if not (0 <= val <= 255):
                msg = f"Color channel '{channel_name}' must be between 0 and 255, got {val}"
                raise ValueError(msg)

    @property
    def rgb(self) -> tuple[int, int, int]:
        return self.r, self.g, self.b

    @property
    def hex(self) -> str:
        """Standard 6-character hex format (#rrggbb)."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    @property
    def hex_argb(self) -> str:
        """8-character hex format with full opacity (#ffrrggbb)."""
        return f"#ff{self.r:02x}{self.g:02x}{self.b:02x}"

    @property
    def int_argb(self) -> int:
        """Signed 32-bit integer representation used by Telegram Android (.attheme)."""
        unsigned = (0xFF << 24) | (self.r << 16) | (self.g << 8) | self.b
        return unsigned - 0x100000000 if unsigned >= 0x80000000 else unsigned

    def with_alpha_int(self, alpha: int) -> int:
        """Signed 32-bit integer with custom alpha channel (0-255)."""
        if not (0 <= alpha <= 255):
            msg = f"Alpha must be between 0 and 255, got {alpha}"
            raise ValueError(msg)
        unsigned = (alpha << 24) | (self.r << 16) | (self.g << 8) | self.b
        return unsigned - 0x100000000 if unsigned >= 0x80000000 else unsigned

    def with_alpha_hex(self, alpha: int) -> str:
        """Hex format with custom alpha prefix (#aarrggbb)."""
        clamped = max(0, min(255, alpha))
        return f"#{clamped:02x}{self.r:02x}{self.g:02x}{self.b:02x}"


    @classmethod
    def from_hex(cls, value: str) -> Color:
        clean = value.strip().lstrip("#")
        if len(clean) == 3:
            clean = "".join(ch * 2 for ch in clean)
        if len(clean) == 8:
            clean = clean[2:]
        if len(clean) != 6:
            msg = f"Invalid hex color string: {value}"
            raise ValueError(msg)
        r = int(clean[0:2], 16)
        g = int(clean[2:4], 16)
        b = int(clean[4:6], 16)
        return cls(r, g, b)

    @classmethod
    def from_hsl(cls, h: float, s: float, lightness: float) -> Color:
        """Construct from HSL (h in [0, 1], s in [0, 1], lightness in [0, 1])."""
        r, g, b = _hsl_to_rgb(h, s, lightness)
        return cls(r, g, b)

    def to_hsl(self) -> tuple[float, float, float]:
        """Returns tuple of (hue, saturation, lightness) normalized in [0, 1]."""
        return _rgb_to_hsl(self.r, self.g, self.b)

    def relative_luminance(self) -> float:
        """Calculate relative luminance using WCAG 2.1 standard sRGB gamma transformation."""

        def _linearize(channel: float) -> float:
            return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

        r_lin = _linearize(self.r / 255.0)
        g_lin = _linearize(self.g / 255.0)
        b_lin = _linearize(self.b / 255.0)
        return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

    def contrast_ratio(self, other: Color) -> float:
        """Calculate WCAG 2.1 contrast ratio between two colors (range: 1.0 to 21.0)."""
        l1 = self.relative_luminance()
        l2 = other.relative_luminance()
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

    def blend(self, other: Color, weight: float) -> Color:
        """Linear blend with another color. weight=0 returns self, weight=1 returns other."""
        clamped_w = max(0.0, min(1.0, weight))
        inv_w = 1.0 - clamped_w
        return Color(
            r=round(self.r * inv_w + other.r * clamped_w),
            g=round(self.g * inv_w + other.g * clamped_w),
            b=round(self.b * inv_w + other.b * clamped_w),
        )

    def lighten(self, factor: float) -> Color:
        """Shift lightness towards white (factor in [0, 1])."""
        white = Color(255, 255, 255)
        return self.blend(white, factor)

    def darken(self, factor: float) -> Color:
        """Shift lightness towards black (factor in [0, 1])."""
        black = Color(0, 0, 0)
        return self.blend(black, factor)

    def adjust_hsl(
        self,
        h_offset: float = 0.0,
        s_factor: float = 1.0,
        l_factor: float = 1.0,
    ) -> Color:
        """Adjust HSL channels with scale factors and offsets."""
        h, s, lightness = self.to_hsl()
        return Color.from_hsl(
            h=(h + h_offset) % 1.0,
            s=s * s_factor,
            lightness=lightness * l_factor,
        )

    def ensure_contrast(self, background: Color, min_ratio: float = 4.5) -> Color:
        """Adjust lightness until the color satisfies the WCAG 2.1 min contrast ratio."""
        if self.contrast_ratio(background) >= min_ratio:
            return self

        target_lighter = background.relative_luminance() < 0.5
        adjusted = self
        for _ in range(30):
            adjusted = adjusted.lighten(0.04) if target_lighter else adjusted.darken(0.04)
            if adjusted.contrast_ratio(background) >= min_ratio:
                return adjusted

        return Color(255, 255, 255) if target_lighter else Color(0, 0, 0)



@dataclass(frozen=True, slots=True)
class DominantColor:
    """Color extracted from an image with its population score and classification."""

    color: Color
    weight: float
    saturation: float
    lightness: float


@dataclass(frozen=True, slots=True)
class PaletteTheme:
    """Semantic color mapping representing an adaptive Telegram theme."""

    is_dark: bool
    background: Color
    surface: Color
    surface_variant: Color
    text_primary: Color
    text_secondary: Color
    accent: Color
    accent_text: Color
    out_bubble: Color
    out_bubble_text: Color
    out_bubble_subtext: Color
    in_bubble: Color
    in_bubble_text: Color
    in_bubble_subtext: Color
    divider: Color
    in_bubble_alpha: int = 255
    out_bubble_alpha: int = 255

    def with_transparency(self, in_alpha: int = 255, out_alpha: int = 255) -> PaletteTheme:
        """Return a copy of the theme with adjusted bubble transparency levels (0-255)."""
        return PaletteTheme(
            is_dark=self.is_dark,
            background=self.background,
            surface=self.surface,
            surface_variant=self.surface_variant,
            text_primary=self.text_primary,
            text_secondary=self.text_secondary,
            accent=self.accent,
            accent_text=self.accent_text,
            out_bubble=self.out_bubble,
            out_bubble_text=self.out_bubble_text,
            out_bubble_subtext=self.out_bubble_subtext,
            in_bubble=self.in_bubble,
            in_bubble_text=self.in_bubble_text,
            in_bubble_subtext=self.in_bubble_subtext,
            divider=self.divider,
            in_bubble_alpha=max(0, min(255, in_alpha)),
            out_bubble_alpha=max(0, min(255, out_alpha)),
        )

