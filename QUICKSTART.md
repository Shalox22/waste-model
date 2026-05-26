# 🐳 Trash Detection API - Quick Start

## What's New

Your trash detection system is now ready to share! Here's what I've set up:

### ✅ Files Created:
- **Dockerfile** - Container configuration
- **docker-compose.yml** - Easy deployment
- **README_DOCKER.md** - Full Docker documentation
- **INTEGRATION_GUIDE.md** - For your website developer
- **deploy.sh / deploy.bat** - One-command startup scripts
- **.env.example** - Environment configuration template

### 📦 Updated Files:
- **src/main.py** - Enhanced with camera/CCTV support
- **requirements.txt** - Added FastAPI & Uvicorn

---

## 🚀 Quick Start (3 Steps)

### Step 1: Build the Docker Image
```bash
# On Windows
deploy.bat build

# On Mac/Linux
chmod +x deploy.sh
./deploy.sh build
```

### Step 2: Start the API
```bash
# On Windows
deploy.bat start

# On Mac/Linux
./deploy.sh start
```

### Step 3: Test It
```bash
# Check if API is running
curl http://localhost:8080/

# Predict from image
curl -X POST -F "file=@image.jpg" http://localhost:8080/predict/

# View live camera
# Open in browser: http://localhost:8080/camera/stream?camera_id=0
```

---

## 📡 API Endpoints for Your Website Developer

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/health` | GET | Docker health check |
| `/predict/` | POST | Predict trash in single image |
| `/batch-predict/` | POST | Predict in multiple images |
| `/camera/snapshot` | GET | Get camera snapshot with detection |
| `/camera/stream` | GET | Live MJPEG stream |

---

## 📸 Camera Integration

### Local Webcam
```
http://localhost:8080/camera/stream?camera_id=0
http://localhost:8080/camera/snapshot?camera_id=0
```

### CCTV Camera (RTSP)
```
http://localhost:8080/camera/stream?camera_url=rtsp://192.168.1.100:554/stream
http://localhost:8080/camera/snapshot?camera_url=rtsp://192.168.1.100:554/stream
```

---

## 💻 For Website Integration

### Frontend (HTML/JS)
```html
<!-- Display live stream in website -->
<img src="http://localhost:8080/camera/stream?camera_id=0">

<!-- Or with CCTV -->
<img src="http://localhost:8080/camera/stream?camera_url=rtsp://YOUR_CAMERA_IP:554/stream">
```

### Backend (Python)
```python
import requests

# Predict from image
with open('image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8080/predict/', files=files)
    detections = response.json()
```

### Backend (Node.js)
```javascript
const FormData = require('form-data');
const fs = require('fs');

const form = new FormData();
form.append('file', fs.createReadStream('image.jpg'));

const response = await axios.post('http://localhost:8080/predict/', form);
```

---

## 🎛️ Commands Reference

**Windows:**
```bash
deploy.bat start      # Start API
deploy.bat stop       # Stop API
deploy.bat restart    # Restart
deploy.bat logs       # View logs
deploy.bat status     # Check status
deploy.bat build      # Build image
deploy.bat clean      # Clean up
```

**Mac/Linux:**
```bash
./deploy.sh start     # Start API
./deploy.sh stop      # Stop API
./deploy.sh restart   # Restart
./deploy.sh logs      # View logs
./deploy.sh status    # Check status
./deploy.sh build     # Build image
./deploy.sh clean     # Clean up
```

---

## 📝 Configuration

Edit `.env` file to customize:
```env
LOG_LEVEL=info
CONFIDENCE_THRESHOLD=0.5
SKIP_FRAMES=1  # Process every frame (increase for performance)
```

---

## 🔗 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

---

## 🎓 Full Documentation

- **README_DOCKER.md** - Complete Docker setup & API reference
- **INTEGRATION_GUIDE.md** - Detailed integration examples

---

## ❓ Troubleshooting

### API won't start?
```bash
# Check logs
deploy.bat logs

# Or with docker directly
docker-compose logs trash-detector
```

### Camera not working?
- Verify RTSP URL is correct
- Test in VLC first: File > Open Network Stream
- Check firewall allows port 554

### Need GPU support?
- Use NVIDIA Docker: `docker run --gpus all ...`
- Requires nvidia-docker installed

---

## 📦 What to Send to Your Developer

Share these files:
```
├── Dockerfile
├── docker-compose.yml
├── src/
│   ├── main.py
│   ├── yolo26n.pt
│   ├── best.pt
│   └── utils.py
├── requirements.txt
├── README_DOCKER.md
├── INTEGRATION_GUIDE.md
├── deploy.sh (or deploy.bat for Windows)
└── .env.example
```

They can then:
1. Run `docker build -t trash-detector .`
2. Run `docker-compose up`
3. Integrate using API endpoints in README_DOCKER.md

---

## ✨ Key Features

✅ FastAPI with full documentation  
✅ CCTV camera support (RTSP streaming)  
✅ Real-time detection with bounding boxes  
✅ Batch processing  
✅ Automatic result logging  
✅ Docker containerized  
✅ Easy deployment scripts  

---

**Ready to go!** 🚀 Your API is ready for production.

For questions, check:
- API Docs: http://localhost:8080/docs
- README_DOCKER.md
- INTEGRATION_GUIDE.md

