# Integration Guide for Website Developers

## Architecture Overview

```
┌─────────────────┐
│   Website/Web   │
│   Application   │
└────────┬────────┘
         │ HTTP API calls
         ↓
┌─────────────────────────────────────┐
│    Trash Detection API (Docker)     │
│   - FastAPI Server                  │
│   - YOLO Model                      │
│   - Camera/CCTV Support             │
└─────────────────────────────────────┘
         │          │
         ↓          ↓
    ┌────────────────────┐
    │  USB Camera   │  RTSP CCTV  │
    └────────────────────┘
```

## Setup Steps

### 1. **Prepare the Docker Image**

On the machine where you want to deploy:

```bash
# Clone/copy the project
cd /path/to/JSS

# Build Docker image
docker build -t trash-detector:1.0 .

# Test it locally
docker-compose up -d

# Check if it's running
curl http://localhost:8080/health
```

### 2. **For Website Backend Integration**

#### Node.js / Express
```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const API_URL = 'http://localhost:8080';

// Predict from uploaded image
async function predictImage(imagePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(imagePath));
  
  try {
    const response = await axios.post(`${API_URL}/predict/`, form, {
      headers: form.getHeaders()
    });
    return response.data;
  } catch (error) {
    console.error('Prediction failed:', error);
  }
}

// Get current snapshot from camera
async function getCameraSnapshot(cameraUrl) {
  try {
    const response = await axios.get(`${API_URL}/camera/snapshot`, {
      params: { camera_url: cameraUrl },
      responseType: 'arraybuffer'
    });
    return Buffer.from(response.data);
  } catch (error) {
    console.error('Failed to get snapshot:', error);
  }
}

module.exports = { predictImage, getCameraSnapshot };
```

#### Python / Django
```python
import requests
from django.core.files.storage import default_storage

API_URL = 'http://localhost:8080'

def predict_image(image_file):
    """Send image to detection API"""
    files = {'file': image_file.read()}
    response = requests.post(f'{API_URL}/predict/', files=files)
    return response.json()

def get_camera_snapshot(camera_url):
    """Get snapshot from CCTV camera"""
    response = requests.get(f'{API_URL}/camera/snapshot', 
                          params={'camera_url': camera_url})
    return response.content  # JPEG bytes

# In your Django view
from django.http import JsonResponse

def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        result = predict_image(request.FILES['image'])
        return JsonResponse(result)
```

#### PHP / Laravel
```php
<?php
$apiUrl = 'http://localhost:8080';

// Single image prediction
function predictImage($imagePath) {
    global $apiUrl;
    
    $cfile = new CURLFile($imagePath);
    $post = array('file' => $cfile);
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "$apiUrl/predict/");
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $result = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($result, true);
}

// Get camera snapshot
function getCameraSnapshot($cameraUrl) {
    global $apiUrl;
    
    $url = $apiUrl . '/camera/snapshot?camera_url=' . urlencode($cameraUrl);
    return file_get_contents($url);
}

// Usage
if ($_FILES['image']) {
    $result = predictImage($_FILES['image']['tmp_name']);
    echo json_encode($result);
}
?>
```

### 3. **Frontend Display**

#### HTML + JavaScript
```html
<!DOCTYPE html>
<html>
<head>
    <title>Trash Detection System</title>
</head>
<body>
    <!-- Upload Image -->
    <h2>Upload Image for Detection</h2>
    <input type="file" id="imageInput" accept="image/*">
    <button onclick="uploadImage()">Predict</button>
    
    <div id="results"></div>
    
    <!-- Live Camera Stream -->
    <h2>Live Camera Feed</h2>
    <img id="cameraStream" src="http://localhost:8080/camera/stream?camera_id=0" 
         style="max-width: 100%; border: 2px solid black;">
    
    <!-- CCTV Stream -->
    <h2>CCTV Camera Stream</h2>
    <input type="text" id="rtspUrl" placeholder="Enter RTSP URL" 
           value="rtsp://192.168.1.100:554/stream">
    <button onclick="changeCCTV()">Connect</button>
    <img id="cctvStream" style="max-width: 100%; border: 2px solid black;">

    <script>
    async function uploadImage() {
        const fileInput = document.getElementById('imageInput');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Please select an image');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            displayResults(result);
        } catch (error) {
            console.error('Error:', error);
        }
    }
    
    function displayResults(result) {
        let html = `<h3>Found ${result.detections_count} objects:</h3>`;
        html += '<ul>';
        
        result.detections.forEach(det => {
            html += `<li>
                Class: ${det.class_name} | 
                Confidence: ${(det.confidence * 100).toFixed(2)}%
            </li>`;
        });
        
        html += '</ul>';
        document.getElementById('results').innerHTML = html;
    }
    
    function changeCCTV() {
        const rtspUrl = document.getElementById('rtspUrl').value;
        const streamUrl = `http://localhost:8080/camera/snapshot?camera_url=${encodeURIComponent(rtspUrl)}`;
        document.getElementById('cctvStream').src = streamUrl;
    }
    </script>
</body>
</html>
```

### 4. **CCTV Camera Setup**

#### Finding Your CCTV Camera RTSP URL

Different manufacturers have different formats:

**Hikvision (DS-series)**
```
rtsp://username:password@192.168.1.100:554/Streaming/Channels/101
rtsp://username:password@192.168.1.100:554/Streaming/Channels/102
```

**Dahua (IPC-series)**
```
rtsp://username:password@192.168.1.100:554/stream/unicast/trackID=1
```

**AXIS (Network cameras)**
```
rtsp://username:password@192.168.1.100:554/axis-media/media.amp
```

**TP-Link / Generic**
```
rtsp://username:password@192.168.1.100:554/stream
```

#### How to Find Your Camera's RTSP URL

1. Check the camera's manual or documentation
2. Login to camera's web interface (usually http://camera-ip)
3. Look in Settings > Network > Stream Settings
4. Default credentials are often admin/admin

### 5. **Database Storage of Results**

Store detection results for later analysis:

```python
# Django Model Example
from django.db import models

class DetectionResult(models.Model):
    image = models.ImageField(upload_to='detections/')
    timestamp = models.DateTimeField(auto_now_add=True)
    detections = models.JSONField()  # Store JSON data
    detection_count = models.IntegerField()
    
    class Meta:
        ordering = ['-timestamp']

# Save detection
result = predictImage(uploaded_file)
DetectionResult.objects.create(
    image=uploaded_file,
    detections=result['detections'],
    detection_count=result['detections_count']
)
```

### 6. **Deployment Checklist**

- [ ] Docker is installed on server
- [ ] Port 8080 is open for API
- [ ] CCTV cameras are accessible from server
- [ ] Model files (yolo26n.pt, best.pt) are included
- [ ] Website backend can reach `http://localhost:8080`
- [ ] CORS is configured if frontend is on different domain
- [ ] Storage directory for detections has write permissions
- [ ] API is tested with curl before integrating

### 7. **CORS Setup (if frontend on different domain)**

Update `src/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://yourwebsite.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing Your Integration

```bash
# 1. Test API health
curl http://localhost:8080/health

# 2. Test image prediction
curl -X POST -F "file=@test_image.jpg" http://localhost:8080/predict/

# 3. Test camera snapshot
curl -o snapshot.jpg http://localhost:8080/camera/snapshot?camera_id=0

# 4. Test CCTV stream (requires valid RTSP URL)
curl -o cctv.jpg "http://localhost:8080/camera/snapshot?camera_url=rtsp://192.168.1.100:554/stream"
```

## Support

For issues or questions, check:
- Container logs: `docker-compose logs -f`
- API docs: `http://localhost:8080/docs` (Swagger UI)
- Camera connectivity: Test RTSP URL with VLC media player first

## Performance Tips

- **For high volume**: Use batch endpoint `/batch-predict/`
- **For real-time**: Stream every Nth frame (reduce frequency)
- **For GPU**: Use GPU-enabled Docker image
- **For multiple cameras**: Deploy multiple containers or load balance

