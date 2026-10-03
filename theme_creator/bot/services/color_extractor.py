from __future__ import annotations

import io
import random
from typing import BinaryIO

from PIL import Image, ImageDraw, ImageFont

from bot.models.color import Color, DominantColor, PaletteTheme


def _resolve_font(size: int) -> tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, bool]:
    """Load system TrueType font with Unicode support, or fallback to default."""
    candidate_paths = [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]
    for font_path in candidate_paths:
        try:
            return ImageFont.truetype(font_path, size=size), True
        except (OSError, ValueError):
            continue
    return ImageFont.load_default(), False


class ColorExtractor:
    """Extracts dominant palettes and generates accessible Telegram themes."""

    def __init__(self, sample_size: int = 120, max_clusters: int = 6) -> None:
        self.sample_size = sample_size
        self.max_clusters = max_clusters

    def extract_from_bytes(self, image_bytes: bytes | BinaryIO) -> list[DominantColor]:
        """Load an image from bytes or stream and extract dominant colors."""
        if isinstance(image_bytes, bytes):
            stream = io.BytesIO(image_bytes)
        else:
            stream = image_bytes

        with Image.open(stream) as img:
            return self.extract_from_image(img)

    def extract_from_image(self, image: Image.Image) -> list[DominantColor]:
        """Extract dominant colors using accelerated k-means clustering."""
        rgb_img = image.convert("RGB")
        rgb_img.thumbnail((self.sample_size, self.sample_size), Image.Resampling.BILINEAR)

        rgb_bytes = rgb_img.tobytes()
        pixels: list[tuple[int, int, int]] = [
            (rgb_bytes[i], rgb_bytes[i + 1], rgb_bytes[i + 2]) for i in range(0, len(rgb_bytes), 3)
        ]
        if not pixels:
            fallback = Color(40, 120, 200)
            return [DominantColor(fallback, 1.0, 0.6, 0.5)]

        centroids = self._kmeans(pixels, k=self.max_clusters, iterations=12)
        return centroids

    def _kmeans(
        self,
        pixels: list[tuple[int, int, int]],
        k: int,
        iterations: int,
    ) -> list[DominantColor]:
        """Perform k-means clustering on RGB pixel samples."""
        k = min(k, len(pixels))
        rng = random.Random(42)

        # K-means++ initialization for diversified starting centroids
        initial_centroids: list[tuple[float, float, float]] = [
            tuple(float(c) for c in rng.choice(pixels))  # type: ignore[assignment]
        ]

        while len(initial_centroids) < k:
            distances: list[float] = []
            for px in pixels:
                px_f = (float(px[0]), float(px[1]), float(px[2]))
                min_d_sq = min(
                    (px_f[0] - c[0]) ** 2 + (px_f[1] - c[1]) ** 2 + (px_f[2] - c[2]) ** 2
                    for c in initial_centroids
                )
                distances.append(min_d_sq)

            total_dist = sum(distances)
            if total_dist == 0.0:
                break

            threshold = rng.uniform(0.0, total_dist)
            current_sum = 0.0
            chosen = pixels[0]
            for px, dist in zip(pixels, distances, strict=True):
                current_sum += dist
                if current_sum >= threshold:
                    chosen = px
                    break
            initial_centroids.append((float(chosen[0]), float(chosen[1]), float(chosen[2])))

        centroids = initial_centroids

        # Run fixed number of iterations
        cluster_counts = [0] * len(centroids)
        for _ in range(iterations):
            sums = [[0.0, 0.0, 0.0] for _ in centroids]
            cluster_counts = [0] * len(centroids)

            for px in pixels:
                pr, pg, pb = px
                best_idx = 0
                best_dist = float("inf")
                for c_idx, c in enumerate(centroids):
                    d_sq = (pr - c[0]) ** 2 + (pg - c[1]) ** 2 + (pb - c[2]) ** 2
                    if d_sq < best_dist:
                        best_dist = d_sq
                        best_idx = c_idx

                sums[best_idx][0] += pr
                sums[best_idx][1] += pg
                sums[best_idx][2] += pb
                cluster_counts[best_idx] += 1

            new_centroids: list[tuple[float, float, float]] = []
            for c_idx, count in enumerate(cluster_counts):
                if count > 0:
                    new_centroids.append(
                        (
                            sums[c_idx][0] / count,
                            sums[c_idx][1] / count,
                            sums[c_idx][2] / count,
                        )
                    )
                else:
                    new_centroids.append(centroids[c_idx])
            centroids = new_centroids

        total_pixels = len(pixels)
        results: list[DominantColor] = []
        for c, count in zip(centroids, cluster_counts, strict=True):
            if count == 0:
                continue
            color = Color(
                r=max(0, min(255, round(c[0]))),
                g=max(0, min(255, round(c[1]))),
                b=max(0, min(255, round(c[2]))),
            )
            _, s, l_val = color.to_hsl()
            weight = count / total_pixels
            results.append(
                DominantColor(
                    color=color,
                    weight=weight,
                    saturation=s,
                    lightness=l_val,
                )
            )

        # Sort with a bonus on saturation to prioritize expressive colors over gray noise
        results.sort(key=lambda item: item.weight * 0.6 + item.saturation * 0.4, reverse=True)
        return results

    def select_accent(self, dominants: list[DominantColor], is_dark: bool) -> Color:
        """Select vibrant accent color ensuring proper lightness for the theme mode."""
        if not dominants:
            return Color(45, 136, 255)

        # Find candidate with highest chroma and reasonable lightness
        vibrant_candidates = [
            d for d in dominants if d.saturation >= 0.20 and 0.15 <= d.lightness <= 0.85
        ]

        base = vibrant_candidates[0].color if vibrant_candidates else dominants[0].color
        h, s, _ = base.to_hsl()

        # If image is almost completely grayscale, add subtle pleasant blue saturation
        s_target = max(0.40, s)

        # Ensure accent has comfortable lightness in target theme
        target_lightness = 0.58 if is_dark else 0.42
        return Color.from_hsl(h, s_target, target_lightness)

    def generate_theme(
        self,
        dominants: list[DominantColor],
        is_dark: bool,
    ) -> PaletteTheme:
        """Build an accessible color palette adapted for dark or light Telegram interface."""
        accent = self.select_accent(dominants, is_dark)
        primary_hue = accent.to_hsl()[0]

        if is_dark:
            # Dark theme: deep tinted background with layered surfaces
            bg = Color.from_hsl(primary_hue, 0.12, 0.08)
            surface = Color.from_hsl(primary_hue, 0.10, 0.13)
            surface_variant = Color.from_hsl(primary_hue, 0.10, 0.18)
            text_primary = Color(245, 247, 250)
            text_secondary = Color(156, 163, 175)
            divider = Color.from_hsl(primary_hue, 0.08, 0.20)

            in_bubble = surface_variant
            in_bubble_text = text_primary
            in_bubble_subtext = text_secondary

            # Outgoing bubble: harmonious accent tint or direct accent
            out_bubble = accent.adjust_hsl(s_factor=0.85, l_factor=0.80)
            out_bubble_text = self._best_readable_text(out_bubble)
            out_bubble_subtext = (
                out_bubble_text.darken(0.3)
                if out_bubble_text.r > 128
                else out_bubble_text.lighten(0.3)
            )

        else:
            # Light theme: clean tinted white background
            bg = Color.from_hsl(primary_hue, 0.06, 0.96)
            surface = Color(255, 255, 255)
            surface_variant = Color.from_hsl(primary_hue, 0.08, 0.91)
            text_primary = Color(24, 28, 33)
            text_secondary = Color(107, 114, 128)
            divider = Color.from_hsl(primary_hue, 0.06, 0.86)

            in_bubble = Color(255, 255, 255)
            in_bubble_text = text_primary
            in_bubble_subtext = text_secondary

            out_bubble = (
                accent.lighten(0.80)
                if accent.contrast_ratio(Color(255, 255, 255)) > 5.0
                else accent.lighten(0.75)
            )
            out_bubble_text = self._best_readable_text(out_bubble)
            out_bubble_subtext = text_secondary

        accent_text = self._best_readable_text(accent)

        return PaletteTheme(
            is_dark=is_dark,
            background=bg,
            surface=surface,
            surface_variant=surface_variant,
            text_primary=text_primary,
            text_secondary=text_secondary,
            accent=accent,
            accent_text=accent_text,
            out_bubble=out_bubble,
            out_bubble_text=out_bubble_text,
            out_bubble_subtext=out_bubble_subtext,
            in_bubble=in_bubble,
            in_bubble_text=in_bubble_text,
            in_bubble_subtext=in_bubble_subtext,
            divider=divider,
        )

    def _best_readable_text(self, bg: Color) -> Color:
        """Select pure white or dark charcoal guaranteeing highest WCAG contrast."""
        white = Color(255, 255, 255)
        charcoal = Color(17, 24, 39)
        c_white = bg.contrast_ratio(white)
        c_dark = bg.contrast_ratio(charcoal)
        return white if c_white >= c_dark else charcoal

    def _draw_bubbles(self, draw: ImageDraw.ImageDraw, theme: PaletteTheme) -> None:
        font_main, has_unicode = _resolve_font(15)
        font_small, _ = _resolve_font(11)

        in_msg = "Привет! Как тебе эта тема?" if has_unicode else "Hey! How do you like this theme?"
        out_msg = (
            "Выглядит стильно! Цвета идеально подходят 🔥"
            if has_unicode
            else "Looks amazing! Colors match perfectly."
        )

        in_x1, in_y1, in_x2, in_y2 = 40, 70, 460, 140
        draw.rounded_rectangle((in_x1, in_y1, in_x2, in_y2), radius=14, fill=theme.in_bubble.rgb)
        draw.text(
            (in_x1 + 18, in_y1 + 16),
            in_msg,
            font=font_main,
            fill=theme.in_bubble_text.rgb,
        )
        draw.text(
            (in_x2 - 55, in_y2 - 22), "12:45", font=font_small, fill=theme.in_bubble_subtext.rgb
        )

        out_x1, out_y1, out_x2, out_y2 = 280, 160, 720, 230
        draw.rounded_rectangle(
            (out_x1, out_y1, out_x2, out_y2), radius=14, fill=theme.out_bubble.rgb
        )
        draw.text(
            (out_x1 + 18, out_y1 + 16),
            out_msg,
            font=font_main,
            fill=theme.out_bubble_text.rgb,
        )
        draw.text(
            (out_x2 - 55, out_y2 - 22), "12:46", font=font_small, fill=theme.out_bubble_subtext.rgb
        )

    def _draw_swatch_bar(
        self,
        draw: ImageDraw.ImageDraw,
        theme: PaletteTheme,
        card_w: int,
        card_h: int,
        swatch_y: int,
    ) -> None:
        font_main, _ = _resolve_font(15)
        font_small, _ = _resolve_font(11)

        draw.line([(0, swatch_y), (card_w, swatch_y)], fill=theme.divider.rgb, width=1)
        draw.rectangle([(0, swatch_y + 1), (card_w, card_h)], fill=theme.surface.rgb)

        title = f"{'Dark' if theme.is_dark else 'Light'} Theme Palette"
        draw.text((40, swatch_y + 20), title, font=font_main, fill=theme.text_primary.rgb)

        swatches: list[tuple[str, Color]] = [
            ("Background", theme.background),
            ("Surface", theme.surface),
            ("Accent", theme.accent),
            ("Out Bubble", theme.out_bubble),
            ("In Bubble", theme.in_bubble),
            ("Text", theme.text_primary),
        ]
        start_x, width, height, gap = 40, 100, 50, 16

        for idx, (label, color) in enumerate(swatches):
            sx = start_x + idx * (width + gap)
            sy = swatch_y + 60
            draw.rounded_rectangle(
                (sx, sy, sx + width, sy + height),
                radius=8,
                fill=color.rgb,
                outline=theme.divider.rgb,
                width=1,
            )
            draw.text((sx, sy + height + 8), label, font=font_small, fill=theme.text_secondary.rgb)
            draw.text(
                (sx, sy + height + 24),
                color.hex.upper(),
                font=font_small,
                fill=theme.text_primary.rgb,
            )

    def render_preview_card(
        self,
        theme: PaletteTheme,
        source_image: Image.Image | None = None,
    ) -> bytes:
        """Render a visual preview card displaying generated bubbles and color swatches."""
        card_w, card_h = 760, 480
        img = Image.new("RGB", (card_w, card_h), theme.background.rgb)
        draw = ImageDraw.Draw(img)

        if source_image is not None:
            wp = source_image.convert("RGB").copy()
            wp.thumbnail((card_w, 280), Image.Resampling.BILINEAR)
            wp_x = (card_w - wp.width) // 2
            dimmed = Image.new("RGB", wp.size, theme.background.rgb)
            blended_wp = Image.blend(wp, dimmed, 0.45 if theme.is_dark else 0.25)
            img.paste(blended_wp, (wp_x, 0))

        self._draw_bubbles(draw, theme)
        self._draw_swatch_bar(draw, theme, card_w, card_h, swatch_y=280)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()
