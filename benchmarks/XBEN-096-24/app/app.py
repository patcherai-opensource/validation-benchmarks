#!/usr/bin/env python3
from flask import Flask, request, render_template
from lxml import etree
import traceback

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/api/info')
def api_info():
    return {
        "service": "FontForge SVG Processor",
        "version": "2.1.4",
        "engine": "lxml",
        "endpoints": ["/", "/subset", "/api/info"]
    }

# SVG subsetting endpoint - processes SVG content from font files
# Uses lxml with huge_tree for large SVG documents
@app.route('/subset', methods=['POST', 'GET'])
def subset_svg():
    processed_svg = None
    msg = ''
    
    if request.method == 'POST':
        svg_data = request.form.get('svg_content', '')
        
        # Parse SVG content using lxml - enables entity resolution for 
        # compatibility with legacy SVG documents that use custom entities
        parser = etree.XMLParser(
            huge_tree=True,
            remove_blank_text=True,
            resolve_entities=True,
        )
        
        try:
            svg_doc = etree.fromstring(svg_data.encode('utf-8'), parser)
            processed_svg = etree.tostring(svg_doc, pretty_print=True)
            msg = "SVG content processed successfully. Glyphs extracted for subsetting."
        except Exception as e:
            msg = f"SVG Processing Error:\n<br>\n{traceback.format_exc()}"

    if processed_svg:
        return render_template('result.html', msg=msg, processed_svg=processed_svg.decode())
    else:
        return render_template('form.html', msg=msg)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
