# Render Deployment Guide for Resume Parser

## Pre-Deployment Setup

### 1. Ensure Repository is Ready
Your GitHub repository should have:
- `requirements.txt` with all dependencies
- Main server file (e.g., `clean_server.py`)
- Static files in correct directories
- README.md with project description

### 2. Create Render Configuration Files

#### Create `render.yaml` (optional but recommended):
```yaml
services:
  - type: web
    name: resume-parser
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python clean_server.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
      - key: PORT
        fromService:
          type: web
          name: resume-parser
          property: port
```

#### Update your server to use Render's PORT:
```python
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=False)
```

## Deployment Steps

### 1. Repository Settings
- Make repository **PUBLIC** for free Render hosting
- Ensure all files are committed and pushed

### 2. Render Dashboard Setup
1. Go to [render.com](https://render.com)
2. Sign up/Login with GitHub account
3. Click "New +" → "Web Service"
4. Connect your GitHub repository: `Shreyaskrishnareddy/demo-resumeparser`

### 3. Service Configuration
```
Name: resume-parser-demo
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: python clean_server.py
```

### 4. Environment Variables (if needed)
```
PORT: (automatically set by Render)
PYTHON_VERSION: 3.9
```

## Server Code Updates Needed

### Update `clean_server.py` for Render:
```python
import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ... your existing code ...

if __name__ == '__main__':
    # Use Render's PORT environment variable
    port = int(os.environ.get('PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### Update file paths to be relative:
```python
# Instead of absolute paths, use relative paths
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
```

## Render Deployment Configuration

### Service Settings:
- **Runtime**: Python 3.9
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python clean_server.py`
- **Auto-Deploy**: Yes (deploys on git push)

### Resource Allocation:
- **Free Tier**: 512MB RAM, 0.1 CPU
- **Scaling**: Auto-sleep after 15 minutes of inactivity (free tier)

## Post-Deployment

### 1. Test Your Deployment
- Your app will be available at: `https://resume-parser-demo.onrender.com` (or similar)
- Test file upload functionality
- Verify all parsing features work
- Check API endpoints

### 2. Custom Domain (Optional)
- Add custom domain in Render dashboard
- Configure DNS settings
- Enable SSL (automatic with Render)

## Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check `requirements.txt` is complete
   - Ensure Python version compatibility
   - Check for missing system dependencies

2. **Start Command Failures**:
   - Verify your main server file exists
   - Check PORT environment variable usage
   - Ensure app.run() uses host='0.0.0.0'

3. **File Upload Issues**:
   - Render has limited disk space for uploads
   - Consider temporary file cleanup
   - Check file size limits

### Logs and Debugging:
- View logs in Render dashboard
- Use console.log equivalent for Python (print statements)
- Check service health in dashboard

## Performance Optimization for Render

### 1. Keep-Alive Service (Optional)
Create a simple ping service to prevent auto-sleep:
```python
@app.route('/ping')
def ping():
    return {'status': 'alive', 'timestamp': time.time()}
```

### 2. File Cleanup
Add automatic cleanup for uploaded files:
```python
import atexit
import tempfile

def cleanup_uploads():
    # Clean temporary files on shutdown
    pass

atexit.register(cleanup_uploads)
```

## Deployment Checklist

- [ ] Repository is public on GitHub
- [ ] `requirements.txt` is complete and accurate
- [ ] Server code uses `PORT` environment variable
- [ ] Server binds to `0.0.0.0` host
- [ ] Static files are properly configured
- [ ] File upload paths are relative
- [ ] Build and start commands are correct
- [ ] Environment variables are set
- [ ] Repository is connected to Render
- [ ] Service is deployed and running
- [ ] All functionality tested on live URL

## Monitoring and Maintenance

### Health Checks:
```python
@app.route('/health')
def health():
    return {
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': time.time()
    }
```

### Usage Analytics:
- Monitor request patterns in Render dashboard
- Track parsing success/failure rates
- Monitor response times and performance

## Free Tier Limitations

- **Sleep Mode**: App sleeps after 15 minutes of inactivity
- **Build Time**: Limited build minutes per month
- **Storage**: Limited disk space for temporary files
- **Bandwidth**: Limited monthly bandwidth

## Upgrade Considerations

Consider upgrading to paid tier if you need:
- Always-on service (no sleep mode)
- More resources (RAM, CPU)
- Multiple services
- Priority support

## Security Considerations

Even though the repo is public:
- Never commit API keys or secrets
- Use environment variables for sensitive config
- Implement rate limiting for production use
- Monitor for abuse or unusual traffic patterns

## Support and Resources

- [Render Documentation](https://render.com/docs)
- [Python on Render](https://render.com/docs/deploy-flask)
- [Render Community](https://community.render.com/)