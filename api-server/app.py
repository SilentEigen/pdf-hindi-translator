from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path
import tempfile
import uuid

# Add parent directory to path to import latex_converter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from latex_converter import LatexConverter

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Initialize converter
converter = LatexConverter()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "PDF Hindi Translator"})

@app.route('/translate', methods=['POST'])
def translate_pdf():
    """
    Translate PDF endpoint
    Expects: PDF file in request
    Returns: Translated PDF
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        pdf_file = request.files['file']
        
        if pdf_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        if not pdf_file.filename.endswith('.pdf'):
            return jsonify({"error": "File must be a PDF"}), 400
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save input PDF
            input_path = os.path.join(temp_dir, 'input.pdf')
            output_path = os.path.join(temp_dir, 'output.pdf')
            
            pdf_file.save(input_path)
            
            # Convert
            print(f"🔄 Starting translation of: {pdf_file.filename}")
            converter.generate_pdf(input_path, output_path)
            
            # Check if output was created
            if not os.path.exists(output_path):
                return jsonify({"error": "Translation failed - output not generated"}), 500
            
            print(f"✅ Translation complete: {pdf_file.filename}")
            
            # Return the translated PDF
            return send_file(
                output_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'translated_{pdf_file.filename}'
            )
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": f"Translation error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print("🚀 Starting PDF Translation API Server...")
    print(f"📍 Endpoint: http://localhost:{port}/translate")
    print(f"💡 Health Check: http://localhost:{port}/health")
    app.run(debug=True, port=port, host='0.0.0.0')
