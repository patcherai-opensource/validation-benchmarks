import os
import io
import zlib
import struct
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Secret flag - only accessible through the vulnerability
FLAG = os.environ.get('FLAG', '@FLAG@')

# Configuration for "secure" image processing
MAX_METADATA_SIZE = 1024  # We "limit" metadata to 1KB... but there's a bug

def parse_png_chunks(data):
    """
    Parse PNG file and extract chunk information.
    This parser has a vulnerability in handling compressed text chunks (zTXt).
    """
    if len(data) < 8:
        raise ValueError("File too small to be a valid PNG")
    
    # Check PNG signature
    signature = data[:8]
    if signature != b'\x89PNG\r\n\x1a\n':
        raise ValueError("Invalid PNG signature")
    
    chunks = []
    offset = 8
    total_decompressed_size = 0
    
    while offset < len(data):
        if offset + 8 > len(data):
            break
            
        # Read chunk length and type
        length = struct.unpack('>I', data[offset:offset+4])[0]
        chunk_type = data[offset+4:offset+8].decode('ascii', errors='replace')
        
        if offset + 12 + length > len(data):
            break
            
        chunk_data = data[offset+8:offset+8+length]
        
        chunk_info = {
            'type': chunk_type,
            'length': length,
            'offset': offset
        }
        
        # Handle different chunk types
        if chunk_type == 'zTXt':
            # Compressed text chunk - THIS IS WHERE THE VULNERABILITY IS
            # CVE-2014-9601: No limit on decompressed size
            try:
                null_pos = chunk_data.find(b'\x00')
                if null_pos > 0:
                    keyword = chunk_data[:null_pos].decode('latin-1')
                    compression_method = chunk_data[null_pos+1]
                    compressed_text = chunk_data[null_pos+2:]
                    
                    if compression_method == 0:  # zlib deflate
                        # VULNERABILITY: No size limit on decompression
                        # In real CVE-2014-9601, this could exhaust memory
                        # Here, we check if the decompressed size is "too large"
                        # and in that case, expose debug info including the flag
                        try:
                            decompressed = zlib.decompress(compressed_text)
                            total_decompressed_size += len(decompressed)
                            
                            # "Security check" that ironically creates the vulnerability
                            # When decompression exceeds the limit, dump debug info
                            if len(decompressed) > MAX_METADATA_SIZE:
                                chunk_info['warning'] = 'Decompression exceeded limit'
                                chunk_info['decompressed_size'] = len(decompressed)
                                chunk_info['debug_context'] = {
                                    'keyword': keyword,
                                    'text_preview': decompressed[:200].decode('latin-1', errors='replace'),
                                    'server_state': get_debug_state()
                                }
                            else:
                                chunk_info['keyword'] = keyword
                                chunk_info['text'] = decompressed.decode('latin-1', errors='replace')
                        except zlib.error as e:
                            chunk_info['error'] = f'Decompression failed: {str(e)}'
            except Exception as e:
                chunk_info['error'] = str(e)
                
        elif chunk_type == 'iTXt':
            # International text chunk - also vulnerable
            try:
                null_pos = chunk_data.find(b'\x00')
                if null_pos > 0:
                    keyword = chunk_data[:null_pos].decode('utf-8', errors='replace')
                    rest = chunk_data[null_pos+1:]
                    if len(rest) >= 2:
                        compression_flag = rest[0]
                        compression_method = rest[1]
                        
                        # Find the actual text (after language tag and translated keyword)
                        remaining = rest[2:]
                        null1 = remaining.find(b'\x00')
                        if null1 >= 0:
                            remaining = remaining[null1+1:]
                            null2 = remaining.find(b'\x00')
                            if null2 >= 0:
                                text_data = remaining[null2+1:]
                                
                                if compression_flag == 1 and compression_method == 0:
                                    # Compressed - vulnerable path
                                    try:
                                        decompressed = zlib.decompress(text_data)
                                        total_decompressed_size += len(decompressed)
                                        
                                        if len(decompressed) > MAX_METADATA_SIZE:
                                            chunk_info['warning'] = 'iTXt decompression exceeded limit'
                                            chunk_info['decompressed_size'] = len(decompressed)
                                            chunk_info['debug_context'] = {
                                                'keyword': keyword,
                                                'server_state': get_debug_state()
                                            }
                                    except zlib.error:
                                        pass
            except Exception as e:
                chunk_info['error'] = str(e)
                
        elif chunk_type == 'iCCP':
            # ICC Profile chunk - also vulnerable to decompression
            try:
                null_pos = chunk_data.find(b'\x00')
                if null_pos > 0:
                    profile_name = chunk_data[:null_pos].decode('latin-1')
                    compression_method = chunk_data[null_pos+1]
                    compressed_profile = chunk_data[null_pos+2:]
                    
                    if compression_method == 0:
                        try:
                            decompressed = zlib.decompress(compressed_profile)
                            total_decompressed_size += len(decompressed)
                            
                            if len(decompressed) > MAX_METADATA_SIZE:
                                chunk_info['warning'] = 'iCCP decompression exceeded limit'
                                chunk_info['profile_name'] = profile_name
                                chunk_info['decompressed_size'] = len(decompressed)
                                chunk_info['debug_context'] = get_debug_state()
                        except zlib.error:
                            pass
            except Exception as e:
                chunk_info['error'] = str(e)
        
        chunks.append(chunk_info)
        offset += 12 + length
    
    return chunks, total_decompressed_size

def get_debug_state():
    """
    Returns debug state information - this is where the flag leaks
    when the decompression vulnerability is triggered.
    """
    return {
        'memory_warning': 'Excessive decompression detected',
        'app_version': '1.0.0-debug',
        'internal_secret': FLAG,  # VULNERABILITY: Flag exposed in debug output
        'recommendation': 'Consider upgrading image processing library'
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """
    Upload and analyze a PNG image.
    The analyzer extracts metadata and reports any issues found.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.png'):
        return jsonify({'error': 'Only PNG files are supported'}), 400
    
    try:
        data = file.read()
        chunks, total_decompressed = parse_png_chunks(data)
        
        result = {
            'filename': file.filename,
            'file_size': len(data),
            'total_decompressed_metadata': total_decompressed,
            'chunks': chunks
        }
        
        # Add warning if total decompression was high
        if total_decompressed > MAX_METADATA_SIZE * 10:
            result['security_warning'] = {
                'message': 'Total decompressed metadata exceeded safe limits',
                'total_size': total_decompressed,
                'limit': MAX_METADATA_SIZE * 10,
                'debug_dump': get_debug_state()
            }
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Alternative API endpoint for image analysis.
    Accepts raw PNG data in the request body.
    """
    if request.content_type and 'image/png' in request.content_type:
        data = request.get_data()
    else:
        return jsonify({'error': 'Content-Type must be image/png'}), 400
    
    if len(data) < 8:
        return jsonify({'error': 'Data too small'}), 400
    
    try:
        chunks, total_decompressed = parse_png_chunks(data)
        
        result = {
            'file_size': len(data),
            'total_decompressed_metadata': total_decompressed,
            'chunks': chunks
        }
        
        if total_decompressed > MAX_METADATA_SIZE * 10:
            result['security_warning'] = {
                'message': 'Decompression bomb detected',
                'debug_dump': get_debug_state()
            }
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'ImageMetadataAnalyzer'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
