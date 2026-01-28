#!/usr/bin/env python3
from flask import Flask, request, render_template, jsonify, send_file
from lxml import etree
import traceback
import os
import io
import hashlib
import json
from datetime import datetime
import base64

app = Flask(__name__)

# In-memory storage for fonts
font_storage = {}

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/api/status')
def api_status():
    """API health check endpoint"""
    return jsonify({
        "status": "operational",
        "service": "FontForge Pro",
        "version": "2.4.1",
        "endpoints": ["/api/status", "/api/fonts", "/docs"]
    })

@app.route('/docs')
def docs():
    """API documentation page"""
    return render_template('docs.html')

@app.route('/api/fonts', methods=['GET'])
def list_fonts():
    """List all uploaded fonts"""
    fonts = []
    for font_id, data in font_storage.items():
        fonts.append({
            "id": font_id,
            "name": data.get("name", "Unknown"),
            "uploaded": data.get("uploaded", ""),
            "format": data.get("format", "Unknown")
        })
    return jsonify({"fonts": fonts, "total": len(fonts)})

@app.route('/convert', methods=['GET', 'POST'])
def convert_font():
    """Font conversion page - decoy endpoint"""
    if request.method == 'GET':
        return render_template('convert.html')
    # Conversion not implemented - return error
    return jsonify({"error": "Conversion service temporarily unavailable", "code": 503}), 503

@app.route('/subset', methods=['GET', 'POST'])
def subset_font():
    """Font subsetting service page"""
    return render_template('subset.html')

@app.route('/api/subset', methods=['POST'])
def api_subset():
    """
    Font subsetting API endpoint
    Accepts SVG font data for glyph subsetting operations
    """
    result_data = None
    error_msg = None
    
    try:
        content_type = request.content_type or ''
        
        if 'application/json' in content_type:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON payload"}), 400
            svg_data = data.get('svg_data', '')
            options = data.get('options', {})
        elif 'multipart/form-data' in content_type:
            if 'svg_file' in request.files:
                svg_file = request.files['svg_file']
                svg_data = svg_file.read().decode('utf-8')
            else:
                svg_data = request.form.get('svg_data', '')
            options = json.loads(request.form.get('options', '{}'))
        else:
            svg_data = request.form.get('svg_data', request.data.decode('utf-8'))
            options = {}
        
        if not svg_data:
            return jsonify({"error": "No SVG data provided"}), 400
        
        # Parse the SVG font data for glyph subsetting
        # Using XMLParser with huge_tree for large font files
        # Note: resolve_entities enabled for compatibility with older SVG fonts
        parser = etree.XMLParser(
            huge_tree=True,
            remove_blank_text=True,
            no_network=False,
            resolve_entities=True
        )
        
        svg_tree = etree.fromstring(svg_data.encode('utf-8'), parser)
        
        # Extract glyph information
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}
        glyphs = svg_tree.xpath('//svg:glyph | //glyph', namespaces=namespaces)
        
        glyph_info = []
        for glyph in glyphs:
            glyph_info.append({
                'name': glyph.get('glyph-name', glyph.get('unicode', 'unnamed')),
                'unicode': glyph.get('unicode', ''),
                'd': glyph.get('d', '')[:50] + '...' if glyph.get('d') else ''
            })
        
        # Build result
        result_xml = etree.tostring(svg_tree, pretty_print=True).decode('utf-8')
        
        return jsonify({
            "status": "success",
            "message": "SVG font data processed successfully",
            "glyphs_found": len(glyph_info),
            "glyphs": glyph_info[:10],  # Return first 10 glyphs
            "processed_svg": result_xml
        })
        
    except etree.XMLSyntaxError as e:
        return jsonify({
            "error": "XML parsing error",
            "details": str(e),
            "hint": "Ensure your SVG data is well-formed XML"
        }), 400
    except Exception as e:
        return jsonify({
            "error": "Processing error",
            "details": str(e)
        }), 500

@app.route('/validate', methods=['GET', 'POST'])
def validate_svg():
    """SVG validation endpoint"""
    if request.method == 'GET':
        return render_template('validate.html')
    
    svg_data = request.form.get('svg_data', '')
    if not svg_data:
        return render_template('validate.html', error="No SVG data provided")
    
    try:
        # Validate SVG structure
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(svg_data.encode('utf-8'), parser)
        
        return render_template('validate.html', 
            success=True,
            message="SVG is valid",
            root_tag=tree.tag,
            child_count=len(tree))
    except etree.XMLSyntaxError as e:
        return render_template('validate.html', error=f"Invalid SVG: {str(e)}")

@app.route('/upload', methods=['GET', 'POST'])
def upload_font():
    """Font upload page - stores fonts for later processing"""
    if request.method == 'GET':
        return render_template('upload.html')
    
    if 'font_file' not in request.files:
        return render_template('upload.html', error="No file uploaded")
    
    font_file = request.files['font_file']
    if font_file.filename == '':
        return render_template('upload.html', error="No file selected")
    
    # Generate font ID
    font_data = font_file.read()
    font_id = hashlib.md5(font_data).hexdigest()[:12]
    
    # Store font metadata
    font_storage[font_id] = {
        "name": font_file.filename,
        "uploaded": datetime.now().isoformat(),
        "format": os.path.splitext(font_file.filename)[1].upper().strip('.'),
        "size": len(font_data)
    }
    
    return render_template('upload.html', 
        success=True,
        font_id=font_id,
        font_name=font_file.filename)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
