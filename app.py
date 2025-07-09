import os
from flask import Flask, request, send_file, jsonify
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "Thai Text API ✅",
        "info": "SVG solution with Google Fonts - Perfect Thai support",
        "endpoints": {
            "/text-on-image": "POST - Add Thai text to image (returns SVG)",
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
    """เพิ่มข้อความบนรูป"""
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 100))
        y = int(data.get('y', 100))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF')
        align = data.get('align', 'left')  # left, center, right
        valign = data.get('valign', 'top')  # top, middle, bottom
        
        if not img_url:
            return jsonify({"error": "img_url is required"}), 400
        
        # จัดการ text alignment
        text_anchor = 'start'  # default
        if align == 'center':
            text_anchor = 'middle'
        elif align == 'right':
            text_anchor = 'end'
        
        # จัดการ vertical alignment
        dominant_baseline = 'hanging'  # default (top)
        if valign == 'middle':
            dominant_baseline = 'central'
        elif valign == 'bottom':
            dominant_baseline = 'alphabetic'
        
        # จัดการข้อความหลายบรรทัด
        lines = text.split('\n') if '\n' in text else [text]
        text_elements = ""
        line_height = font_size * 1.2
        
        for i, line in enumerate(lines):
            line_y = y + (i * line_height)
            text_elements += f'  <text x="{x}" y="{line_y}" class="thai-text">{line}</text>\n'
        
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
        text-anchor: {text_anchor};
        dominant-baseline: {dominant_baseline};
      }}
    </style>
  </defs>
  <image href="{img_url}" width="800" height="600" preserveAspectRatio="xMidYMid slice"/>
{text_elements}</svg>'''
        
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
    font_size = request.args.get('font_size', '48')
    bg_color = request.args.get('bg', '#1976D2')
    text_color = request.args.get('color', 'white')
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&amp;display=swap');
      .thai-text {{
        font-family: 'Noto Sans Thai', sans-serif;
        font-size: {font_size}px;
        fill: {text_color};
        text-anchor: middle;
        dominant-baseline: central;
      }}
    </style>
  </defs>
  <rect width="800" height="400" fill="{bg_color}"/>
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