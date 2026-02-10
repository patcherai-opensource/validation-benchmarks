#!/usr/bin/env python3
"""
Font Subsetting Service - SVG Table Processor

This service processes OpenType SVG fonts and subsets their SVG tables.
Mimics the behavior of fonttools pyftsubset SVG processing functionality.

CVE-2023-45139 simulation: fonttools XXE vulnerability in SVG table parsing.
The vulnerability exists in the svg.py subsetting module which uses lxml
without resolve_entities=False, allowing XXE attacks via malicious SVG content.
"""
from flask import Flask, request, render_template
from lxml import etree
import traceback
import base64
import io

app = Flask(__name__)

# Supported glyph IDs for subsetting simulation
GLYPH_REGISTRY = ['glyph1', 'glyph2', 'glyph3', 'glyph4', 'glyph5']


@app.route('/')
def index():
    """Font processing service homepage"""
    return render_template('home.html')


def subset_glyphs(svg_data, glyph_ids=None):
    """
    Subset SVG glyphs from SVG table data.
    
    This function mimics fonttools Lib/fontTools/subset/svg.py subset_glyphs() 
    which parses SVG data from OT-SVG font tables.
    
    VULNERABLE: Uses XMLParser without resolve_entities=False
    Ref: CVE-2023-45139 fonttools XXE in svg.py
    """
    if glyph_ids is None:
        glyph_ids = GLYPH_REGISTRY
    
    # This is the vulnerable code pattern from fonttools svg.py
    # The parser does NOT set resolve_entities=False, allowing XXE
    svg = etree.fromstring(
        svg_data.encode("utf-8") if isinstance(svg_data, str) else svg_data,
        parser=etree.XMLParser(
            huge_tree=True,
            remove_blank_text=True,
        ),
    )
    
    # Find and extract requested glyph elements
    result_elements = []
    for elem in svg.iter():
        elem_id = elem.get('id', '')
        if elem_id in glyph_ids or elem.tag.endswith('}g') or elem.tag == 'g':
            result_elements.append(etree.tostring(elem, encoding='unicode'))
    
    return etree.tostring(svg, encoding='unicode')


@app.route('/subset', methods=['POST', 'GET'])
def subset_font():
    """
    Font SVG table subsetting endpoint.
    
    Accepts SVG table data from OT-SVG fonts and performs glyph subsetting.
    This simulates the fonttools pyftsubset SVG processing functionality.
    """
    result_svg = None
    msg = ''
    
    if request.method == 'POST':
        svg_data = request.form.get('svg_table', '')
        glyph_ids = request.form.get('glyphs', '').split(',')
        glyph_ids = [g.strip() for g in glyph_ids if g.strip()]
        
        if not glyph_ids:
            glyph_ids = GLYPH_REGISTRY
        
        try:
            # Process SVG table data through vulnerable parser
            result_svg = subset_glyphs(svg_data, glyph_ids)
            msg += "SVG table processed successfully. Glyphs subsetted."
        except Exception as e:
            msg += "Error processing SVG table:\n<br>\n" + traceback.format_exc()
    
    if result_svg:
        return render_template('result.html', msg=msg, parsed_xml=result_svg)
    else:
        return render_template('form.html', msg=msg, endpoint='/subset')


@app.route('/process_font', methods=['POST', 'GET'])
def process_font():
    """
    Alternative endpoint for font SVG processing.
    Accepts base64-encoded SVG table data.
    """
    result_svg = None
    msg = ''
    
    if request.method == 'POST':
        encoded_svg = request.form.get('svg_b64', '')
        
        try:
            # Decode base64 SVG data
            svg_data = base64.b64decode(encoded_svg).decode('utf-8')
            result_svg = subset_glyphs(svg_data)
            msg += "Font SVG table decoded and processed."
        except Exception as e:
            msg += "Error:\n<br>\n" + traceback.format_exc()
    
    if result_svg:
        return render_template('result.html', msg=msg, parsed_xml=result_svg)
    else:
        return render_template('form_b64.html', msg=msg)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
