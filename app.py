import os
from flask import Flask, request, render_template
from video_analyzer import download_youtube_video, analyze_video

app = Flask(__name__)

DEFAULT_URL = "https://youtube.com/shorts/jgmtWPeXsb4"
DEFAULT_PROMPT = (
    "Provide a detailed step-by-step transcript, describe what visual events occur, "
    "and summarize the core point of this video."
)


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        url = request.form.get('url', DEFAULT_URL)
        prompt = request.form.get('prompt', DEFAULT_PROMPT)
        local_filename = "/tmp/temp_clip.mp4"
        try:
            download_youtube_video(url, local_filename)
            result = analyze_video(local_filename, prompt)
        except Exception as e:
            error = str(e)
        finally:
            if os.path.exists(local_filename):
                os.remove(local_filename)
    return render_template('index.html', result=result, error=error,
                           default_url=DEFAULT_URL, default_prompt=DEFAULT_PROMPT)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
