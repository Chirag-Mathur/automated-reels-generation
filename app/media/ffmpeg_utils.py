import subprocess
import os
import shlex
import textwrap

def generate_srt_file(caption: str, output_srt_path: str, words_per_line: int = 8):
    """
    Generates a simple SubRip (.srt) subtitle file from a block of text.
    Args:
        caption: The full text of the caption.
        output_srt_path: The path to save the .srt file.
        words_per_line: How many words to wrap to a new line.
    """
    # Wrap the text to the specified number of words per line
    wrapped_text = textwrap.fill(caption, width=words_per_line * 6) # Approximate width
    
    # Create the content for the .srt file
    # This will show the entire caption for a very long duration (1 hour)
    # FFmpeg will automatically cut it to the video's length.
    srt_content = f"""1
00:00:00,000 --> 01:00:00,000
{wrapped_text}
"""
    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

def generate_video_with_overlay_and_caption(
    background_video_path: str,
    background_music_path: str,
    font_path: str,
    caption: str,
    output_path: str,
    resolution: str = "1080x1920",
    overlay_opacity: float = 0.7,
    font_size: int = 12,
    font_color: str = "white",
    words_per_line: int = 8
):
    """
    Generate a video with a full-screen black overlay and multi-line caption using ffmpeg.
    Args:
        background_video_path: Path to the background video.
        background_music_path: Path to the background music.
        font_path: Path to the .ttf font file.
        caption: Text to overlay on the video.
        output_path: Path to save the output video.
        resolution: Output resolution (default 1080x1920).
        overlay_opacity: Opacity of the black overlay (0-1).
        font_size: Size of the caption font.
        font_color: Color of the caption text.
        words_per_line: Number of words per line for wrapping.
    """
    width, height = map(int, resolution.split('x'))
    temp_srt_path = "caption.srt"
    
    # --- FIX: Generate an SRT file for robust text handling ---
    generate_srt_file(caption, temp_srt_path, words_per_line=words_per_line)

    # Full screen overlay
    drawbox = f"drawbox=x=0:y=0:w={width}:h={height}:color=black@{overlay_opacity}:t=fill"
    
    # Use subtitles filter with system font fallback for better compatibility
    subtitles = (
        f"subtitles={temp_srt_path}:force_style='FontName=Arial,"
        f"FontSize={font_size},PrimaryColour=&HFFFFFF,Alignment=10'"
    )
    
    filter_complex = f"[0:v]scale={width}:{height},format=yuv420p,{drawbox},{subtitles}[v]"
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", background_video_path,
        "-i", background_music_path,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "1:a",
        "-shortest",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Video successfully generated at: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred with FFmpeg: {e}")
    finally:
        # Clean up the temporary SRT file
        if os.path.exists(temp_srt_path):
            os.remove(temp_srt_path)

# --- Example Usage ---
if __name__ == '__main__':
    # Create dummy files for testing
    if not os.path.exists("background.mp4"):
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=size=1920x1080:rate=30:duration=10", "background.mp4"])
    if not os.path.exists("background.mp3"):
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo:duration=10", "background.mp3"])
    
    # NOTE: You must provide a valid path to a .ttf font file on your system.
    # For macOS: "/System/Library/Fonts/Helvetica.ttc"
    # For Windows: "C:/Windows/Fonts/arial.ttf"
    # For Linux: "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font_file_path = "/System/Library/Fonts/Helvetica.ttc" # <-- CHANGE THIS TO A FONT ON YOUR SYSTEM

    long_caption = (
        "This is a very long caption designed to test the automatic text wrapping functionality. "
        "The subtitles filter in FFmpeg should handle this gracefully, breaking it into multiple "
        "lines and ensuring that none of the text is cropped or pushed off the screen, which was the "
        "primary issue with the previous drawtext implementation. This method is far more robust."
    )

    generate_video_with_overlay_and_caption(
        background_video_path="background.mp4",
        background_music_path="background.mp3",
        font_path=font_file_path,
        caption=long_caption,
        output_path="output_video.mp4"
    )
