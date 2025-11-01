#sudocode yay
import subprocess
import platform

def overlay_pdfs(base_pdf, overlay_pdf, output_pdf):
    """
    Overlays one PDF on top of another using Ghostscript via subprocess.

    Args:
        base_pdf (str): The path to the base PDF file.
        overlay_pdf (str): The path to the PDF to be overlaid.
        output_pdf (str): The path to save the combined output PDF.
    """
    if platform.system() == "Windows":
        gs_command = "gswin64c.exe"  # For 64-bit Windows
    else:
        gs_command = "gs"  # For macOS and Linux

    command = [
        gs_command,
        "-o", output_pdf,
        "-sDEVICE=pdfwrite",
        "-dBATCH",
        "-dNOPAUSE",
        "-q",
        "-f", base_pdf,
        "-f", overlay_pdf
    ]

    print(f"Executing command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Overlay successful. Output file: {output_pdf}")
    except FileNotFoundError:
        print(f"Error: Ghostscript command '{gs_command}' not found. "
            "Please ensure Ghostscript is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during Ghostscript execution: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Example usage:
    # Ensure 'base.pdf' and 'overlay.pdf' exist in the same directory as the script.
    base_file = "base.pdf"
    overlay_file = "overlay.pdf"
    output_file = "output.pdf"

    overlay_pdfs(base_file, overlay_file, output_file)

def collision(rect1, rect2):
    return 
def main_game_loop():
    #not done
    pass
def enemy_game_loop():
    #not done
    pass
def player_game_loop():
    #not done
    pass
def entity_game_loop():
    #not done
    pass