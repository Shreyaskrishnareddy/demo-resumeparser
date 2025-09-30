#!/usr/bin/env python3
"""
Improved Resume Parser Server - Using Comprehensive Parser
Addresses all critical missing field issues
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import time
import uuid
import logging
from fixed_comprehensive_parser import FixedComprehensiveParser
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("Warning: PyMuPDF not available, using fallback PDF processing")

import docx
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
parser = FixedComprehensiveParser()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_transaction_id():
    return str(uuid.uuid4())[:8]

def extract_text_from_file(file_path, filename):
    """Extract text from uploaded file"""
    try:
        file_ext = Path(filename).suffix.lower()

        if file_ext == '.pdf':
            return extract_text_from_pdf(file_path)
        elif file_ext in ['.doc', '.docx']:
            return extract_text_from_docx(file_path)
        elif file_ext == '.txt':
            return extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {str(e)}")
        raise

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    if not PYMUPDF_AVAILABLE:
        raise ValueError("PyMuPDF not available for PDF processing")

    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    except Exception as e:
        raise ValueError(f"Error reading DOCX: {str(e)}")

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Error reading TXT file: {str(e)}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'parser': 'comprehensive',
        'uptime': time.time()
    })

@app.route('/api/parse', methods=['POST'])
def parse_resume():
    """Parse uploaded resume file"""
    start_time = time.time()
    transaction_id = generate_transaction_id()

    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded',
                'transaction_id': transaction_id
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'transaction_id': transaction_id
            }), 400

        # Validate file
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Supported types: {", ".join(ALLOWED_EXTENSIONS)}',
                'transaction_id': transaction_id
            }), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB',
                'transaction_id': transaction_id
            }), 400

        # Save file
        filename = secure_filename(file.filename)
        temp_filename = f"{transaction_id}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(file_path)

        try:
            # Extract text
            text_extraction_start = time.time()
            text = extract_text_from_file(file_path, filename)
            text_extraction_time = time.time() - text_extraction_start

            # Parse resume
            parsing_start = time.time()
            result = parser.parse_resume(text, filename)
            parsing_time = time.time() - parsing_start

            # Add processing metadata
            result['processing_metadata'] = {
                'transaction_id': transaction_id,
                'filename': filename,
                'file_size': file_size,
                'text_extraction_time': text_extraction_time,
                'parsing_time': parsing_time,
                'total_processing_time': time.time() - start_time,
                'parser_version': '2.0.0',
                'parser_type': 'comprehensive'
            }

            result['success'] = True

            logger.info(f"Successfully parsed {filename} (ID: {transaction_id}) in {time.time() - start_time:.3f}s")

            return jsonify(result)

        finally:
            # Clean up temporary file
            try:
                os.remove(file_path)
            except:
                pass

    except Exception as e:
        logger.error(f"Error parsing resume (ID: {transaction_id}): {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'transaction_id': transaction_id,
            'processing_time': time.time() - start_time
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Main page with upload interface"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Resume Parser</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 800px;
            width: 90%;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .title {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }

        .subtitle {
            color: #666;
            font-size: 1.1em;
        }

        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .feature {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }

        .feature-icon {
            font-size: 2em;
            margin-bottom: 10px;
        }

        .upload-area {
            border: 3px dashed #ddd;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .upload-area:hover {
            border-color: #667eea;
            background: #f8f9ff;
        }

        .upload-area.dragover {
            border-color: #667eea;
            background: #f0f4ff;
        }

        .file-input {
            display: none;
        }

        .upload-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            transition: transform 0.2s ease;
        }

        .upload-btn:hover {
            transform: translateY(-2px);
        }

        .parse-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
            display: none;
        }

        .progress {
            margin-top: 20px;
            display: none;
        }

        .progress-bar {
            width: 100%;
            height: 10px;
            background: #f0f0f0;
            border-radius: 5px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            animation: progress 2s ease-in-out;
        }

        @keyframes progress {
            0% { width: 0%; }
            100% { width: 100%; }
        }

        .results {
            margin-top: 30px;
            display: none;
        }

        .result-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .result-section h3 {
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 5px;
        }

        .json-output {
            background: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
        }

        .copy-btn {
            background: #17a2b8;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }

        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #f5c6cb;
            margin-top: 20px;
            display: none;
        }

        .success-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .stat {
            text-align: center;
            background: white;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }

        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">Enhanced Resume Parser</h1>
            <p class="subtitle">Comprehensive extraction with missing field fixes</p>
        </div>

        <div class="features">
            <div class="feature">
                <div class="feature-icon">👤</div>
                <h4>Complete Contact Info</h4>
                <p>Names, phones, emails, social media</p>
            </div>
            <div class="feature">
                <div class="feature-icon">💼</div>
                <h4>Detailed Experience</h4>
                <p>Job titles, companies, dates, descriptions</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🎓</div>
                <h4>Full Education</h4>
                <p>Degrees, schools, majors, dates</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🔧</div>
                <h4>Comprehensive Skills</h4>
                <p>Categorized technical and soft skills</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🚀</div>
                <h4>Projects & More</h4>
                <p>Projects, achievements, certifications</p>
            </div>
            <div class="feature">
                <div class="feature-icon">📊</div>
                <h4>Professional Summary</h4>
                <p>Career overview and key titles</p>
            </div>
        </div>

        <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
            <div style="font-size: 3em; margin-bottom: 20px;">📄</div>
            <h3>Drop your resume here or click to upload</h3>
            <p style="margin-top: 10px; color: #666;">Supports PDF, DOC, DOCX, TXT (Max 10MB)</p>
            <input type="file" id="fileInput" class="file-input" accept=".pdf,.doc,.docx,.txt">
            <button class="upload-btn" style="margin-top: 20px;">Choose File</button>
        </div>

        <button class="parse-btn" id="parseBtn" onclick="parseResume()">Parse Resume</button>

        <div class="progress" id="progress">
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <p style="text-align: center; margin-top: 10px;">Processing resume...</p>
        </div>

        <div class="error" id="error"></div>

        <div class="results" id="results">
            <div class="success-stats" id="stats"></div>

            <div class="result-section">
                <h3>📋 Parsed Data (JSON)</h3>
                <div class="json-output" id="jsonOutput"></div>
                <button class="copy-btn" onclick="copyToClipboard()">Copy JSON</button>
            </div>
        </div>
    </div>

    <script>
        let selectedFile = null;
        let parsedData = null;

        // File input handling
        document.getElementById('fileInput').addEventListener('change', function(e) {
            handleFileSelect(e.target.files[0]);
        });

        // Drag and drop handling
        const uploadArea = document.getElementById('uploadArea');

        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            handleFileSelect(e.dataTransfer.files[0]);
        });

        function handleFileSelect(file) {
            if (!file) return;

            // Validate file type
            const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
            if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|doc|docx|txt)$/i)) {
                showError('Please select a PDF, DOC, DOCX, or TXT file.');
                return;
            }

            // Validate file size (10MB)
            if (file.size > 10 * 1024 * 1024) {
                showError('File size must be less than 10MB.');
                return;
            }

            selectedFile = file;
            document.getElementById('uploadArea').innerHTML = `
                <div style="font-size: 2em; margin-bottom: 10px;">✅</div>
                <h3>File Selected: ${file.name}</h3>
                <p style="color: #666;">Size: ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
            `;
            document.getElementById('parseBtn').style.display = 'block';
            hideError();
        }

        async function parseResume() {
            if (!selectedFile) {
                showError('Please select a file first.');
                return;
            }

            // Show progress
            document.getElementById('progress').style.display = 'block';
            document.getElementById('parseBtn').style.display = 'none';
            document.getElementById('results').style.display = 'none';
            hideError();

            // Create form data
            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const response = await fetch('/api/parse', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                // Hide progress
                document.getElementById('progress').style.display = 'none';

                if (data.success) {
                    parsedData = data;
                    displayResults(data);
                } else {
                    showError(data.error || 'Failed to parse resume.');
                    document.getElementById('parseBtn').style.display = 'block';
                }
            } catch (error) {
                document.getElementById('progress').style.display = 'none';
                document.getElementById('parseBtn').style.display = 'block';
                showError('Network error. Please try again.');
                console.error('Error:', error);
            }
        }

        function displayResults(data) {
            // Show results
            document.getElementById('results').style.display = 'block';

            // Display stats
            const contact = data.ContactInformation || {};
            const experience = (data.EmploymentHistory || {}).Positions || [];
            const education = (data.Education || {}).EducationDetails || [];
            const skills = (data.Skills || {}).Raw || [];

            document.getElementById('stats').innerHTML = `
                <div class="stat">
                    <div class="stat-value">${contact.CandidateName?.FormattedName ? '✅' : '❌'}</div>
                    <div class="stat-label">Name Extracted</div>
                </div>
                <div class="stat">
                    <div class="stat-value">${(contact.EmailAddresses || []).length}</div>
                    <div class="stat-label">Email(s)</div>
                </div>
                <div class="stat">
                    <div class="stat-value">${(contact.Telephones || []).length}</div>
                    <div class="stat-label">Phone(s)</div>
                </div>
                <div class="stat">
                    <div class="stat-value">${(contact.SocialMedia || []).length}</div>
                    <div class="stat-label">Social Media</div>
                </div>
                <div class="stat">
                    <div class="stat-value">${experience.length}</div>
                    <div class="stat-label">Work Positions</div>
                </div>
                <div class="stat">
                    <div class="stat-value">${education.length}</div>
                    <div class="stat-label">Education</div>
                </div>
                <div class="stat">
                    <div class="stat-value">${skills.length}</div>
                    <div class="stat-label">Skills</div>
                </div>
                <div class="stat">
                    <div class="stat-value">${data.QualityScore || 0}%</div>
                    <div class="stat-label">Quality Score</div>
                </div>
            `;

            // Display JSON
            document.getElementById('jsonOutput').textContent = JSON.stringify(data, null, 2);
        }

        function copyToClipboard() {
            const jsonText = document.getElementById('jsonOutput').textContent;
            navigator.clipboard.writeText(jsonText).then(() => {
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                setTimeout(() => {
                    btn.textContent = originalText;
                }, 2000);
            });
        }

        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }

        function hideError() {
            document.getElementById('error').style.display = 'none';
        }
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    print("\n🚀 Enhanced Resume Parser Server Starting...")
    print("📊 Features:")
    print("   ✅ Complete contact information extraction")
    print("   ✅ Job titles, companies, and employment details")
    print("   ✅ Education with degrees and schools")
    print("   ✅ Comprehensive skills categorization")
    print("   ✅ Projects, achievements, and certifications")
    print("   ✅ Professional summary and career overview")
    print("   ✅ Social media links extraction")
    print("   ✅ Middle name support")
    print("\n🌐 Access the parser at: http://localhost:8001")
    print("📋 API endpoint: http://localhost:8001/api/parse")
    print("❤️ Health check: http://localhost:8001/api/health")

    app.run(host='0.0.0.0', port=8001, debug=True)