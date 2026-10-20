import os
import sys
import time
import yt_dlp
from google import genai
from google.genai import types


def download_youtube_video(url: str, output_path: str = "temp_clip.mp4") -> str:
    """Downloads a YouTube video or short at standard resolution."""
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': False,
        'overwrites': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path


def analyze_video(file_path: str, user_prompt: str) -> str:
    """Uploads video to Gemini Files API and generates an analysis."""
    client = genai.Client()

    print(f"Uploading {file_path} to Gemini API...")
    video_file = client.files.upload(file=file_path)
    print(f"File uploaded: {video_file.name}")

    # Wait for the file to finish server-side video processing
    while video_file.state.name == "PROCESSING":
        print("Waiting for video processing to complete...")
        time.sleep(3)
        video_file = client.files.get(name=video_file.name)

    if video_file.state.name == "FAILED":
        raise RuntimeError("Video processing failed on server.")

    print("Analyzing video content...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[video_file, user_prompt],
    )

    # Clean up file from cloud storage
    client.files.delete(name=video_file.name)
    return response.text


def main():
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://youtube.com/shorts/jgmtWPeXsb4"
    prompt = sys.argv[2] if len(sys.argv) > 2 else (
        "Provide a detailed step-by-step transcript, describe what visual events occur, "
        "and summarize the core point of this video."
    )

    local_filename = "temp_clip.mp4"
    try:
        download_youtube_video(target_url, local_filename)
        result = analyze_video(local_filename, prompt)
        print("\n" + "=" * 40 + " ANALYSIS RESULT " + "=" * 40 + "\n")
        print(result)
    finally:
        if os.path.exists(local_filename):
            os.remove(local_filename)


if __name__ == "__main__":
    main()
