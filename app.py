import os
import requests
from flask import Flask, request, send_file, jsonify
from io import BytesIO
import urllib.parse
import html

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "Thai Text API ✅",
        "info": "SVG solution with multiple Thai fonts - Perfect Thai support",
        "endpoints": {
            "/text-on-image": "POST - Add Thai text to image",
            "/test": "GET - Test Thai rendering",
            "/pure-svg": "GET - Generate Thai SVG",
            "/multi-line": "POST - Add multi-line Thai text"
        }
    })

@app.route('/test')
def test():
    """ทดสอบการแสดงผลภาษาไทย"""
    
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&amp;family=Sarabun:wght@400;700&amp;family=Kanit:wght@400;700&amp;display=swap');
      .thai-text {
        font-family: 'Noto Sans Thai', 'Sarabun', sans-serif;
        font-size: 36px;
        fill: white;
        text-anchor: middle;
        dominant-baseline: central;
        font-weight: 400;
      }
      .thai-bold {
        font-family: 'Noto Sans Thai', 'Sarabun', sans-serif;
        font-size: 42px;
        fill: #FFD700;
        text-anchor: middle;
        dominant-baseline: central;
        font-weight: 700;
      }
    </style>
  </defs>
  <rect width="800" height="600" fill="#1976D2"/>
  
  <!-- ทดสอบสระลอยและวรรณยุกต์ -->
  <text x="400" y="50" class="thai-bold">ทดสอบสระลอยและวรรณยุกต์</text>
  
  <text x="400" y="120" class="thai-text">ปี่ ฟื้น มื่อ ลิง ดิ้น</text>
  <text x="400" y="170" class="thai-text">ตื่น ซื่อ ปืน ชื่อ อื่น</text>
  <text x="400" y="220" class="thai-text">ที่ มี่ ปี๊ ดี๊ ลี่</text>
  <text x="400" y="270" class="thai-text">ปู่ ตู้ หู่ ดู่ คู่</text>
  <text x="400" y="320" class="thai-text">เป่า เล่า เก่า เร่า เท่า</text>
  <text x="400" y="370" class="thai-text">แก้ แม้ แล้ แพ้ แค้</text>
  <text x="400" y="420" class="thai-text">โต๊ะ โล่ โก่ โร่ โท่</text>
  <text x="400" y="470" class="thai-text">ใต้ ใส่ ใช้ ใด้ ให้</text>
  
  <text x="400" y="550" style="font-family: Arial; font-size: 20px; fill: #4CAF50; text-anchor: middle;">✅ SVG with Google Fonts: Perfect Thai rendering!</text>
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
        align = data.get('align', 'left')  # left, center, right
        valign = data.get('valign', 'top')  # top, middle, bottom
        font = data.get('font', 'Noto Sans Thai')  # เพิ่มตัวเลือกฟอนต์
        
        if not img_url:
            return jsonify({"error": "ต้องมี img_url"}), 400
        
        # Escape HTML entities ในข้อความ
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
        
        # รายการฟอนต์ที่รองรับ
        supported_fonts = {
            'Noto Sans Thai': 'Noto+Sans+Thai:wght@400;700',
            'Sarabun': 'Sarabun:wght@400;700',
            'Kanit': 'Kanit:wght@400;700',
            'Prompt': 'Prompt:wght@400;700',
            'Mitr': 'Mitr:wght@400;700'
        }
        
        font_import = supported_fonts.get(font, supported_fonts['Noto Sans Thai'])
        
        # สร้าง SVG ที่มีรูปพื้นหลัง + ข้อความไทย
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family={font_import}&amp;display=swap');
      .thai-text {{
        font-family: '{font}', 'Noto Sans Thai', sans-serif;
        font-size: {font_size}px;
        fill: {color};
        text-anchor: {text_anchor};
        dominant-baseline: {dominant_baseline};
        font-weight: 400;
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

@app.route('/multi-line', methods=['POST'])
def add_multi_line_text():
    """เพิ่มข้อความหลายบรรทัดบนรูป"""
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        lines = data.get('lines', [])  # รับเป็น array ของข้อความ
        x = int(data.get('x', 400))
        y = int(data.get('y', 100))
        font_size = int(data.get('font_size', 48))
        line_height = int(data.get('line_height', font_size * 1.2))
        color = data.get('font_color', '#FFFFFF')
        align = data.get('align', 'center')
        font = data.get('font', 'Noto Sans Thai')
        
        if not img_url:
            return jsonify({"error": "ต้องมี img_url"}), 400
        
        if not lines:
            lines = ["ข้อความบรรทัดที่ 1", "ข้อความบรรทัดที่ 2"]
        
        # จัดการ text alignment
        text_anchor = 'start'
        if align == 'center':
            text_anchor = 'middle'
        elif align == 'right':
            text_anchor = 'end'
        
        # รายการฟอนต์ที่รองรับ
        supported_fonts = {
            'Noto Sans Thai': 'Noto+Sans+Thai:wght@400;700',
            'Sarabun': 'Sarabun:wght@400;700',
            'Kanit': 'Kanit:wght@400;700',
            'Prompt': 'Prompt:wght@400;700',
            'Mitr': 'Mitr:wght@400;700'
        }
        
        font_import = supported_fonts.get(font, supported_fonts['Noto Sans Thai'])
        
        # สร้าง text elements สำหรับแต่ละบรรทัด
        text_elements = ""
        for i, line in enumerate(lines):
            line_y = y + (i * line_height)
            escaped_line = html.escape(line)
            text_elements += f'  <text x="{x}" y="{line_y}" class="thai-text">{escaped_line}</text>\n'
        
        # สร้าง SVG
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family={font_import}&amp;display=swap');
      .thai-text {{
        font-family: '{font}', 'Noto Sans Thai', sans-serif;
        font-size: {font_size}px;
        fill: {color};
        text-anchor: {text_anchor};
        dominant-baseline: hanging;
        font-weight: 400;
      }}
    </style>
  </defs>
  <image href="{img_url}" width="800" height="600" preserveAspectRatio="xMidYMid slice"/>
{text_elements}</svg>'''
        
        return send_file(
            BytesIO(svg_content.encode('utf-8')),
            mimetype='image/svg+xml',
            as_attachment=True,
            download_name='multi_line_result.svg'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pure-svg')
def pure_svg():
    """สร้าง SVG ภาษาไทยอย่างเดียว"""
    text = request.args.get('text', 'สวัสดีครับ')
    font = request.args.get('font', 'Noto Sans Thai')
    
    # Escape HTML entities
    text = html.escape(text)
    
    # รายการฟอนต์ที่รองรับ
    supported_fonts = {
        'Noto Sans Thai': 'Noto+Sans+Thai:wght@400;700',
        'Sarabun': 'Sarabun:wght@400;700',
        'Kanit': 'Kanit:wght@400;700',
        'Prompt': 'Prompt:wght@400;700',
        'Mitr': 'Mitr:wght@400;700'
    }
    
    font_import = supported_fonts.get(font, supported_fonts['Noto Sans Thai'])
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family={font_import}&amp;display=swap');
      .thai-text {{
        font-family: '{font}', 'Noto Sans Thai', sans-serif;
        font-size: 48px;
        fill: white;
        text-anchor: middle;
        dominant-baseline: central;
        font-weight: 400;
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