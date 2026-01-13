import os
import sys
import shutil
import pygame

# Headless pygame: no real window
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()


class TerminalRenderer:
    """
    A drop-in terminal renderer that replaces pygame's display backend.
    It renders a pygame Surface to the terminal using ▀, ▄, █ blocks.
    """

    def __init__(self, term_width=None, term_height=None):

        # Detect terminal size
        cols, rows = shutil.get_terminal_size()

        self.term_width = term_width if term_width else cols
        self.term_height = term_height if term_height else rows

        # Game resolution (framebuffer) – set by pygame.display.set_mode
        self.src_width = 1
        self.src_height = 1
        self.surface = pygame.Surface((1, 1))

        # ANSI sequences
        self.home = "\033[H"
        self.reset = "\033[0m"
        self.alt_on = "\033[?1049h"
        self.alt_off = "\033[?1049l"
        self.hide_cursor = "\033[?25l"
        self.show_cursor = "\033[?25h"

    # ------------------------------------------------------------
    #  PUBLIC WINDOW API
    # ------------------------------------------------------------

    def max_window(self):
        """Resize renderer to fill the entire terminal."""
        cols, rows = shutil.get_terminal_size()
        self.window_size(cols, rows)

    def fullscreen(self):
        """Alias for max_window()."""
        self.max_window()

    def window_size(self, width, height):
        """Manually set terminal grid size (characters)."""
        self.term_width = max(1, int(width))
        self.term_height = max(1, int(height))

    def scale_factor(self, factor):
        """
        Scale the terminal window by a factor.
        factor > 1 = fewer chars (zoom in)
        factor < 1 = more chars (zoom out)
        """
        new_w = max(1, int(self.term_width * factor))
        new_h = max(1, int(self.term_height * factor))
        self.window_size(new_w, new_h)

    # ------------------------------------------------------------
    #  DISPLAY PATCHING
    # ------------------------------------------------------------
    def patch_pygame_display(self):
        """
        Replace pygame's display functions so the game uses the terminal renderer
        without modifying game code.
        """

        def fake_set_mode(size, flags=0, depth=0):
            w, h = size
            self.src_width = w
            self.src_height = h
            self.surface = pygame.Surface((w, h))
            return self.surface

        pygame.display.set_mode = fake_set_mode

        def fake_flip():
            self.render()

        pygame.display.flip = fake_flip

        def fake_update(rect=None):
            self.render()

        pygame.display.update = fake_update

    # ------------------------------------------------------------
    #  TERMINAL CONTROL
    # ------------------------------------------------------------
    def enter(self):
        sys.stdout.write(self.alt_on + self.hide_cursor + self.reset)
        sys.stdout.flush()
        sys.stdout.write("\033[2J" + self.home)
        sys.stdout.flush()

    def exit(self):
        sys.stdout.write(self.reset + self.show_cursor + self.alt_off)
        sys.stdout.flush()

    def get_surface(self):
        return self.surface

    # ------------------------------------------------------------
    #  PIXEL VISIBILITY
    # ------------------------------------------------------------
    @staticmethod
    def _visible(r, g, b, a, threshold=20):
        if a < 10:
            return False
        return (r > threshold) or (g > threshold) or (b > threshold)

    # ------------------------------------------------------------
    #  FRAME CONVERSION (Y-SCALING FIXED)
    # ------------------------------------------------------------
    def _to_terminal_frame(self):
        """
        Convert the pygame surface into a terminal frame using:
        - █ full block (top+bottom)
        - ▀ upper half block (top only)
        - ▄ lower half block (bottom only)

        Game can use ANY resolution.
        We scale it to the terminal pixel grid:
            term_width × (term_height × 2)
        """

        if self.src_width <= 0 or self.src_height <= 0:
            return ""

        target_w = self.term_width
        target_h = self.term_height * 2

        # ⭐ Correct scaling: ALWAYS scale framebuffer to terminal pixel grid
        scaled = pygame.transform.smoothscale(
            self.surface, (target_w, target_h)
        )

        lines = []

        for row in range(self.term_height):
            y_top = row * 2
            y_bottom = y_top + 1
            chunks = []

            for x in range(self.term_width):
                r1, g1, b1, a1 = scaled.get_at((x, y_top))
                r2, g2, b2, a2 = scaled.get_at((x, y_bottom))

                top = self._visible(r1, g1, b1, a1)
                bot = self._visible(r2, g2, b2, a2)

                if not top and not bot:
                    chunks.append(" ")
                elif top and not bot:
                    chunks.append(f"\033[38;2;{r1};{g1};{b1}m▀\033[0m")
                elif bot and not top:
                    chunks.append(f"\033[38;2;{r2};{g2};{b2}m▄\033[0m")
                else:
                    chunks.append(
                        f"\033[38;2;{r1};{g1};{b1}m"
                        f"\033[48;2;{r2};{g2};{b2}m█\033[0m"
                    )

            lines.append("".join(chunks))

        return "\n".join(lines)

    # ------------------------------------------------------------
    #  RENDER
    # ------------------------------------------------------------
    def render(self):
        frame = self._to_terminal_frame()
        sys.stdout.write(self.home + frame + self.reset)
        sys.stdout.flush()
 