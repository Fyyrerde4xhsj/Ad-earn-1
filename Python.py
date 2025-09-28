from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import re

app = Flask(__name__)

def is_valid_youtube_url(url):
    youtube_regex = re.compile(
        r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$'
    )
    return youtube_regex.match(url)

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not is_valid_youtube_url(url):
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        ydl_opts = {'quiet': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            video_info = {
                'title': info.get('title', ''),
                'thumbnail': info.get('thumbnail', ''),
                'formats': []
            }
            
            for fmt in info.get('formats', []):
                video_info['formats'].append({
                    'quality': fmt.get('format_note', 'Unknown'),
                    'format': fmt.get('ext', 'Unknown'),
                    'size': fmt.get('filesize', 'Unknown')
                })
            
            return jsonify({'success': True, 'videoInfo': video_info})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)