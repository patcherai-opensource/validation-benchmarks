#!/usr/bin/env python3
import os
import io
import re
import tempfile
from flask import Flask, request, render_template, send_file, jsonify
from lxml import etree
from fontTools import ttLib
from fontTools.ttLib.tables.S_V_G_ import SVGDocument
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'ttf', 'otf', 'woff', 'woff2'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def subset_svg_table(font, glyph_subset):
    """
    Process SVG table in font, keeping only glyphs in the subset.
    This mimics fonttools subset functionality for SVG tables.
    """
    if 'SVG ' not in font:
        return None, "Font does not contain an SVG table"
    
    svg_table = font['SVG ']
    new_docs = []
    processed_svg_data = []
    
    for doc in svg_table.docList:
        glyphs_in_doc = set(range(doc.startGlyphID, doc.endGlyphID + 1))
        overlapping = glyphs_in_doc.intersection(glyph_subset)
        
        if not overlapping:
            continue
        
        svg = etree.fromstring(
            doc.data.encode("utf-8"),
            parser=etree.XMLParser(
                huge_tree=True,
                remove_blank_text=True,
            ),
        )
        
        elements_kept = []
        for el in svg.iter():
            el_id = el.get('id', '')
            match = re.match(r'^glyph(\d+)$', el_id)
            if match:
                gid = int(match.group(1))
                if gid in glyph_subset:
                    elements_kept.append(el_id)
        
        svg_str = etree.tostring(svg, encoding='unicode', pretty_print=True)
        processed_svg_data.append({
            'startGlyph': doc.startGlyphID,
            'endGlyph': doc.endGlyphID,
            'keptElements': elements_kept,
            'svgPreview': svg_str[:500] + ('...' if len(svg_str) > 500 else '')
        })
        
        new_doc = SVGDocument(
            data=svg_str,
            startGlyphID=min(overlapping),
            endGlyphID=max(overlapping)
        )
        new_docs.append(new_doc)
    
    if new_docs:
        svg_table.docList = new_docs
        return processed_svg_data, None
    else:
        del font['SVG ']
        return None, "No matching glyphs found in SVG table"


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/subset', methods=['GET', 'POST'])
def subset_font():
    if request.method == 'GET':
        return render_template('subset.html')
    
    if 'font' not in request.files:
        return render_template('subset.html', error="No font file provided")
    
    file = request.files['font']
    if file.filename == '':
        return render_template('subset.html', error="No file selected")
    
    if not allowed_file(file.filename):
        return render_template('subset.html', error="Invalid file type. Allowed: TTF, OTF, WOFF, WOFF2")
    
    glyphs_str = request.form.get('glyphs', '').strip()
    if not glyphs_str:
        return render_template('subset.html', error="No glyphs specified")
    
    try:
        glyph_ids = set()
        for part in glyphs_str.replace(',', ' ').split():
            if '-' in part:
                start, end = part.split('-', 1)
                glyph_ids.update(range(int(start), int(end) + 1))
            else:
                glyph_ids.add(int(part))
    except ValueError:
        return render_template('subset.html', error="Invalid glyph specification")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ttf') as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        font = ttLib.TTFont(tmp_path)
        
        font_info = {
            'numGlyphs': font['maxp'].numGlyphs,
            'tables': list(font.keys()),
            'hasSVG': 'SVG ' in font
        }
        
        svg_result = None
        svg_error = None
        
        if 'SVG ' in font:
            svg_result, svg_error = subset_svg_table(font, glyph_ids)
        
        output = io.BytesIO()
        font.save(output)
        output.seek(0)
        
        font.close()
        os.unlink(tmp_path)
        
        return render_template('result.html',
                             font_info=font_info,
                             svg_result=svg_result,
                             svg_error=svg_error,
                             glyphs=sorted(glyph_ids))
        
    except Exception as e:
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        return render_template('subset.html', error=f"Error processing font: {str(e)}")


@app.route('/api/subset', methods=['POST'])
def api_subset():
    if 'font' not in request.files:
        return jsonify({'error': 'No font file provided'}), 400
    
    file = request.files['font']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    glyphs_str = request.form.get('glyphs', '')
    
    try:
        glyph_ids = set()
        for part in glyphs_str.replace(',', ' ').split():
            if '-' in part:
                start, end = part.split('-', 1)
                glyph_ids.update(range(int(start), int(end) + 1))
            else:
                glyph_ids.add(int(part))
    except ValueError:
        return jsonify({'error': 'Invalid glyph specification'}), 400
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ttf') as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        font = ttLib.TTFont(tmp_path)
        
        result = {
            'numGlyphs': font['maxp'].numGlyphs,
            'tables': list(font.keys()),
            'hasSVG': 'SVG ' in font,
            'svgData': None
        }
        
        if 'SVG ' in font:
            svg_result, svg_error = subset_svg_table(font, glyph_ids)
            if svg_result:
                result['svgData'] = svg_result
            if svg_error:
                result['svgError'] = svg_error
        
        font.close()
        os.unlink(tmp_path)
        
        return jsonify(result)
        
    except Exception as e:
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        return jsonify({'error': str(e)}), 500


@app.route('/docs')
def docs():
    return render_template('docs.html')


@app.route('/sample-font')
def sample_font():
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    if os.path.exists(font_path):
        return send_file(font_path, as_attachment=True, download_name='sample.ttf')
    return jsonify({'error': 'Sample font not available'}), 404


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Internal server error"), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
