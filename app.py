import os
import requests
from flask import Flask, request, send_file, jsonify
from io import BytesIO
import urllib.parse

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "Thai Text API ✅",
        "info": "SVG solution with Google Fonts - Perfect Thai support",
        "endpoints": {
            "/text-on-image": "POST - Add Thai text to image",
            "/test": "GET - Test Thai rendering",
            "/pure-svg": "GET - Generate Thai SVG"
        }
    })

@app.route('/test')
def test():
    """ทดสอบการแสดงผลภาษาไทย"""
    
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&amp;display=swap');
      .thai-text {
        font-family: 'Noto Sans Thai', sans-serif;
        font-size: 36px;
        fill: white;
        text-anchor: middle;
        dominant-baseline: central;
      }
    </style>
  </defs>
  <rect width="800" height="400" fill="#1976D2"/>
  <text x="400" y="150" class="thai-text">ทั้งที่ยังรัก</text>
  <text x="400" y="200" class="thai-text">ที่นี่ ยิ้ม สิ้นสุด</text>
  <text x="400" y="250" class="thai-text">สวัสดีครับ</text>
  <text x="400" y="350" style="font-family: Arial; font-size: 20px; fill: #4CAF50; text-anchor: middle;">✅ SVG with Google Fonts: Perfect Thai rendering!</text>
</svg>'''
    
    return send_file(
        BytesIO(svg_content.encode('utf-8')),
        mimetype='image/svg+xml',
        as_attachment=True,
        download_name='thai_test.svg'
    )

@app.route('/text-on-image', methods=['POST'])
def add_text():
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 100))
        y = int(data.get('y', 100))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF')
        
        if not img_url:
            return jsonify({"error": "ต้องมี img_url"}), 400
        
        # สร้าง SVG ที่มีรูปพื้นหลัง + ข้อความไทย
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&amp;display=swap');
      .thai-text {{
        font-family: 'Noto Sans Thai', sans-serif;
        font-size: {font_size}px;
        fill: {color};
        text-anchor: start;
        dominant-baseline: hanging;
      }}
    </style>
  </defs>
  <image href="{img_url}" width="800" height="600" preserveAspectRatio="xMidYMid slice"/>
  <text x="{x}" y="{y}" class="thai-text">{text}</text>
</svg>'''
        
        return send_file(
            BytesIO(svg_content.encode('utf-8')),
            mimetype='image/svg+xml',
            as_attachment=True,
            download_name='result.svg'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pure-svg')
def pure_svg():
    """สร้าง SVG ภาษาไทยอย่างเดียว"""
    text = request.args.get('text', 'สวัสดีครับ')
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&amp;display=swap');
      .thai-text {{
        font-family: 'Noto Sans Thai', sans-serif;
        font-size: 48px;
        fill: white;
        text-anchor: middle;
        dominant-baseline: central;
      }}
    </style>
  </defs>
  <rect width="800" height="400" fill="#1976D2"/>
  <text x="400" y="200" class="thai-text">{text}</text>
</svg>'''
    
    return send_file(
        BytesIO(svg_content.encode('utf-8')),
        mimetype='image/svg+xml',
        as_attachment=True,
        download_name='thai_svg.svg'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)