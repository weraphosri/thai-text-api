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
        
        # Escape special characters for XML
        import html
        text = html.escape(text)
        
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

@app.route('/svg-to-png', methods=['POST'])
def svg_to_png():
    """รับ SVG content แล้วแปลงเป็น PNG"""
    try:
        data = request.get_json()
        svg_content = data.get('svg')
        
        if not svg_content:
            return jsonify({"error": "svg content is required"}), 400
        
        # แปลง SVG เป็น base64 data URL
        import base64
        svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        
        # สร้าง HTML ที่มี SVG + JavaScript สำหรับแปลงเป็น PNG
        html_converter = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SVG to PNG Converter</title>
</head>
<body>
    <div id="svg-container" style="display:none;">{svg_content}</div>
    <canvas id="canvas" width="800" height="600"></canvas>
    <a id="download" download="result.png">Download PNG</a>
    
    <script>
        // แปลง SVG เป็น PNG
        const svgContainer = document.getElementById('svg-container');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const downloadLink = document.getElementById('download');
        
        // สร้าง image จาก SVG
        const svgBlob = new Blob([svgContainer.innerHTML], {{type: 'image/svg+xml'}});
        const url = URL.createObjectURL(svgBlob);
        const img = new Image();
        
        img.onload = function() {{
            ctx.drawImage(img, 0, 0);
            
            // แปลงเป็น PNG
            canvas.toBlob(function(blob) {{
                const pngUrl = URL.createObjectURL(blob);
                downloadLink.href = pngUrl;
                
                // Auto download
                downloadLink.click();
            }}, 'image/png');
        }};
        
        img.src = url;
    </script>
</body>
</html>'''
        
        return html_converter, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/convert-to-png', methods=['POST'])
def convert_to_png():
    """Alternative: ใช้ external service แปลง SVG เป็น PNG"""
    try:
        data = request.get_json()
        svg_content = data.get('svg')
        
        if not svg_content:
            # ถ้าไม่มี svg ให้เรียก text-on-image ก่อน
            img_url = data.get('img_url')
            text = data.get('text', 'Hello')
            x = int(data.get('x', 100))
            y = int(data.get('y', 100))
            font_size = int(data.get('font_size', 48))
            color = data.get('font_color', '#FFFFFF')
            
            if not img_url:
                return jsonify({"error": "img_url or svg is required"}), 400
            
            # สร้าง SVG
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&amp;display=swap');
      .thai-text {{
        font-family: 'Noto Sans Thai', sans-serif;
        font-size: {font_size}px;
        fill: {color};
      }}
    </style>
  </defs>
  <image href="{img_url}" width="800" height="600" preserveAspectRatio="xMidYMid slice"/>
  <text x="{x}" y="{y}" class="thai-text">{text}</text>
</svg>'''
        
        # ส่งกลับ data URL ที่พร้อมใช้
        import base64
        svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        
        return jsonify({
            "success": True,
            "svg_data_url": f"data:image/svg+xml;base64,{svg_base64}",
            "svg_base64": svg_base64,
            "svg_content": svg_content,
            "note": "Use svg_data_url in img tag or convert with JavaScript"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500