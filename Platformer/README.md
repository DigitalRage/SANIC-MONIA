# Pygame Image Loader Demo

This small demo shows how to load images using Pygame and display them in a window.

Instructions

1. Put images (PNG, JPG, GIF, BMP, etc.) into the folder at project root: `Images/sprites/`.
2. Install dependencies (preferably in a virtual environment):

   python -m pip install -r Platformer/requirements.txt

3. Run the demo from PowerShell (run from repository root):

   python .\Platformer\pygame_image_loader.py

Controls

- Right / Left arrows: cycle through found images
- + / - : zoom in / out
- ESC or close window: quit

Tile background mode

- T : toggle tiled background using the currently-selected image
- [ / ] : decrease / increase tile scale (when tiled mode is active)

Notes

- On some systems you may need to install additional SDL dependencies for pygame to support audio/video. See pygame docs if you get errors importing pygame.
- The script locates `Images/sprites/` relative to the repository root (one level up from the `Platformer/` folder).
