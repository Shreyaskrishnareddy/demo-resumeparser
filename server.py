#!/usr/bin/env python3
"""
Resume Parser Deployment Server
Lightweight Flask server for production deployment
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import time
import uuid
import logging
from pathlib import Path
from fixed_comprehensive_parser import FixedComprehensiveParser
import fitz  # PyMuPDF
from docx import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize parser
parser = FixedComprehensiveParser()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_transaction_id():
    return str(uuid.uuid4())[:8]

def extract_text_from_file(file_path):
    """Extract text from PDF or DOCX file"""
    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    try:
        if extension == '.pdf':
            doc = fitz.open(str(file_path))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        elif extension in ['.docx', '.doc']:
            doc = Document(str(file_path))
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return text
        elif extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return None
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Parser</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f7; min-height: 100vh; color: #1d1d1f;
        }
        .container {
            max-width: 520px; margin: 80px auto; padding: 0 24px;
        }
        h1 {
            font-size: 2.5rem; font-weight: 700; text-align: center;
            margin-bottom: 8px; letter-spacing: -0.03em;
        }
        .subtitle {
            text-align: center; color: #86868b; margin-bottom: 48px;
            font-size: 1.1rem; font-weight: 400;
        }
        .upload-area {
            background: white; border: 2px dashed #d1d1d6;
            border-radius: 12px; padding: 48px 32px; text-align: center;
            transition: all 0.2s ease; cursor: pointer; margin-bottom: 32px;
        }
        .upload-area:hover { border-color: #007aff; }
        .upload-area.dragover { border-color: #007aff; background: #f0f8ff; }
        .upload-icon {
            width: 48px; height: 48px; margin: 0 auto 16px;
            background: #f0f8ff; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
        }
        #fileInput { display: none; }
        .upload-text {
            font-size: 1.1rem; font-weight: 500; margin-bottom: 4px;
        }
        .upload-subtext { color: #86868b; font-size: 0.95rem; }
        .upload-btn {
            background: #007aff; color: white; border: none;
            padding: 12px 24px; border-radius: 8px; font-size: 1rem;
            font-weight: 500; cursor: pointer; margin-top: 16px;
            transition: background 0.2s ease;
        }
        .upload-btn:hover { background: #0056cc; }
        .loading {
            display: none; text-align: center; margin: 32px 0;
        }
        .spinner {
            border: 2px solid #f0f0f0; border-top: 2px solid #007aff;
            border-radius: 50%; width: 24px; height: 24px;
            animation: spin 1s linear infinite; margin: 0 auto 12px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .results { margin-top: 32px; display: none; }
        .result-section {
            background: white; border-radius: 8px; padding: 20px;
            margin-bottom: 16px; border: 1px solid #e5e5e7;
        }
        .result-title {
            font-weight: 600; margin-bottom: 12px; color: #1d1d1f;
            font-size: 1.1rem;
        }
        .result-item { margin-bottom: 8px; color: #424245; }
        .result-item strong { color: #1d1d1f; }
        .json-output {
            background: #1d1d1f; color: #ffffff; padding: 16px;
            border-radius: 8px; font-family: 'SF Mono', monospace;
            font-size: 0.85rem; max-height: 300px; overflow-y: auto;
            white-space: pre-wrap; margin-top: 16px;
        }
        .error {
            background: #ffeaea; border: 1px solid #ff6b6b;
            color: #d63031; padding: 12px; border-radius: 8px;
            margin: 16px 0; display: none;
        }
        .stats {
            display: grid; grid-template-columns: repeat(3, 1fr);
            gap: 12px; margin: 24px 0;
        }
        .stat {
            background: white; padding: 16px; border-radius: 8px;
            text-align: center; border: 1px solid #e5e5e7;
        }
        .stat-number {
            font-size: 1.4rem; font-weight: 700; color: #007aff;
        }
        .stat-label {
            color: #86868b; font-size: 0.8rem; margin-top: 4px;
        }
        .download-btn {
            background: #007aff; color: white; border: none;
            padding: 12px 24px; border-radius: 8px; font-size: 1rem;
            font-weight: 500; cursor: pointer; margin: 16px 0;
            transition: background 0.2s ease; display: block; width: 100%;
        }
        .download-btn:hover { background: #0056cc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Resume Parser</h1>
        <p class="subtitle">Professional resume parsing solution</p>

        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <div class="upload-icon">
                <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                </svg>
            </div>
            <div class="upload-text">Drop resume here or click to browse</div>
            <div class="upload-subtext">PDF, DOC, DOCX, TXT (Max 10MB)</div>
            <button class="upload-btn" type="button">Choose File</button>
            <input type="file" id="fileInput" accept=".pdf,.doc,.docx,.txt">
        </div>

        <div class="error" id="errorDiv"></div>

        <div class="loading" id="loadingDiv">
            <div class="spinner"></div>
            <p>Processing resume...</p>
        </div>

        <div class="results" id="resultsDiv">
            <div class="stats" id="statsDiv"></div>
            <div id="resultCards"></div>
            <button class="download-btn" id="downloadBtn" onclick="downloadJSON()">Download JSON</button>
            <div class="json-output" id="jsonOutput"></div>
        </div>
    </div>

    <script>
        const uploadArea = document.querySelector('.upload-area');
        const fileInput = document.getElementById('fileInput');
        const loadingDiv = document.getElementById('loadingDiv');
        const resultsDiv = document.getElementById('resultsDiv');
        const errorDiv = document.getElementById('errorDiv');

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                processFile(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                processFile(e.target.files[0]);
            }
        });

        function showError(message) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            loadingDiv.style.display = 'none';
            resultsDiv.style.display = 'none';
        }

        function processFile(file) {
            errorDiv.style.display = 'none';
            resultsDiv.style.display = 'none';
            loadingDiv.style.display = 'block';

            const formData = new FormData();
            formData.append('file', file);

            fetch('/api/parse', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                loadingDiv.style.display = 'none';
                if (data.success) {
                    displayResults(data);
                } else {
                    showError(data.error || 'Failed to parse resume');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Network error occurred');
            });
        }

        let currentData = null;

        function displayResults(data) {
            currentData = data;
            const statsDiv = document.getElementById('statsDiv');
            const resultCards = document.getElementById('resultCards');
            const jsonOutput = document.getElementById('jsonOutput');

            const personalDetails = data.data?.PersonalDetails || {};
            const experiences = data.data?.ListOfExperiences || [];
            const skills = data.data?.ListOfSkills || [];

            statsDiv.innerHTML = `
                <div class="stat">
                    <div class="stat-number">${skills.length}</div>
                    <div class="stat-label">Skills</div>
                </div>
                <div class="stat">
                    <div class="stat-number">${experiences.length}</div>
                    <div class="stat-label">Positions</div>
                </div>
                <div class="stat">
                    <div class="stat-number">${Math.round((data.processing_time_ms || 0))}ms</div>
                    <div class="stat-label">Processing</div>
                </div>
            `;

            resultCards.innerHTML = `
                <div class="result-section">
                    <div class="result-title">Contact Information</div>
                    <div class="result-item"><strong>Name:</strong> ${personalDetails.FullName || 'Not found'}</div>
                    <div class="result-item"><strong>Email:</strong> ${personalDetails.EmailID || 'Not found'}</div>
                    <div class="result-item"><strong>Phone:</strong> ${personalDetails.PhoneNumber || 'Not found'}</div>
                </div>
                <div class="result-section">
                    <div class="result-title">Experience</div>
                    <div class="result-item"><strong>Positions:</strong> ${experiences.length}</div>
                    <div class="result-item"><strong>Skills:</strong> ${skills.length}</div>
                </div>
            `;

            jsonOutput.textContent = JSON.stringify(data, null, 2);
            resultsDiv.style.display = 'block';
        }

        function downloadJSON() {
            if (!currentData) {
                alert('No data to download');
                return;
            }

            const now = new Date();
            const timestamp = now.toISOString().slice(0, 19).replace(/[:.]/g, '-');
            const filename = `resume-parsed-${timestamp}.json`;

            const jsonString = JSON.stringify(currentData, null, 2);
            const blob = new Blob([jsonString], { type: 'application/json' });
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Homepage with clean UI"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'resume-parser',
        'version': '2.0',
        'timestamp': time.time()
    })

@app.route('/api/parse', methods=['POST'])
def parse_resume():
    """Parse resume endpoint"""
    start_time = time.time()
    transaction_id = generate_transaction_id()

    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'transaction_id': transaction_id
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'transaction_id': transaction_id
            }), 400

        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not allowed. Supported: PDF, DOCX, TXT',
                'transaction_id': transaction_id
            }), 400

        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"{transaction_id}_{filename}")
        file.save(filepath)

        # Extract text
        text = extract_text_from_file(filepath)

        if not text:
            return jsonify({
                'success': False,
                'error': 'Could not extract text from file',
                'transaction_id': transaction_id
            }), 400

        # Parse resume
        result = parser.parse_resume(text, filename)

        # Clean up file
        try:
            os.remove(filepath)
        except:
            pass

        processing_time = time.time() - start_time

        return jsonify({
            'success': True,
            'transaction_id': transaction_id,
            'processing_time_ms': round(processing_time * 1000, 2),
            'data': result
        })

    except Exception as e:
        logger.error(f"Error parsing resume: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'transaction_id': transaction_id
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)