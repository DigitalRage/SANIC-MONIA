"""Simple Pygame image loader demo.

Place some images in the repository folder `Images/sprites/` (relative to the project root).
Run this script from the `Platformer` folder or from project root. It will open a window and let
you cycle through found images with Left/Right arrows. ESC or window close quits.

Windows PowerShell example to run:
  python .\Platformer\pygame_image_loader.py
"""
from __future__ import annotations
import os
import sys
import glob
import pygame


def find_sprite_dir() -> str:
    # Script is inside Platformer/, Images/ is at project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.normpath(os.path.join(script_dir, os.pardir))
    sprites_dir = os.path.join(repo_root, 'Images', 'sprites')
    return sprites_dir


def load_image_paths(sprites_dir: str) -> list[str]:
    exts = ('*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.webp')
    paths: list[str] = []
    for e in exts:
        paths.extend(glob.glob(os.path.join(sprites_dir, e)))
    paths.sort()
    return paths


def load_images(paths: list[str]) -> list[pygame.Surface]:
    images: list[pygame.Surface] = []
    for p in paths:
        try:
            img = pygame.image.load(p)
            # Use convert_alpha for images with transparency
            if img.get_alpha() is not None:
                img = img.convert_alpha()
            else:
                img = img.convert()
            images.append(img)
        except Exception as e:
            print(f"Failed to load {p}: {e}")
    return images


def scale_to_fit(img: pygame.Surface, max_w: int, max_h: int) -> pygame.Surface:
    w, h = img.get_size()
    if w <= max_w and h <= max_h:
        return img
    scale = min(max_w / w, max_h / h)
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return pygame.transform.smoothscale(img, new_size)


def main():
    sprites_dir = find_sprite_dir()
    if not os.path.isdir(sprites_dir):
        print(f"Sprites folder not found: {sprites_dir}")
        sys.exit(1)

    image_paths = load_image_paths(sprites_dir)
    if not image_paths:
        print(f"No images found in: {sprites_dir}")
        sys.exit(1)

    pygame.init()
    pygame.display.set_caption('Pygame Image Loader')
    screen_w, screen_h = 1000, 700
    screen = pygame.display.set_mode((screen_w, screen_h))
    clock = pygame.time.Clock()

    images = load_images(image_paths)
    if not images:
        print('No valid images could be loaded.')
        pygame.quit()
        sys.exit(1)

    font = pygame.font.SysFont(None, 22)
    idx = 0
    zoom = 1.0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT:
                    idx = (idx + 1) % len(images)
                elif event.key == pygame.K_LEFT:
                    idx = (idx - 1) % len(images)
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    zoom = min(3.0, zoom + 0.1)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    zoom = max(0.1, zoom - 0.1)

        screen.fill((30, 30, 30))

        img = images[idx]
        # Apply zoom then scale to fit screen area with margin
        w, h = img.get_size()
        zoomed = pygame.transform.rotozoom(img, 0, zoom)
        draw_img = scale_to_fit(zoomed, int(screen_w * 0.95), int(screen_h * 0.9))

        dw, dh = draw_img.get_size()
        screen.blit(draw_img, ((screen_w - dw) // 2, (screen_h - dh) // 2))

        # filename text
        filename = os.path.basename(image_paths[idx])
        text = f"{idx+1}/{len(images)} - {filename}  (Left/Right cycle, +/- zoom, ESC quit)"
        txt_surf = font.render(text, True, (230, 230, 230))
        screen.blit(txt_surf, (10, screen_h - 30))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    main()
