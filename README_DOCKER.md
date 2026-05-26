# Trash Detection API - Docker Setup Guide

## Quick Start

### Prerequisites
- Docker installed on your system
- Docker Compose installed
- The model files (yolo26n.pt, best.pt) included in the src/ folder

### Build and Run with Docker

#### Option 1: Using Docker Compose (Recommended)
```bash
# Build and start the API
docker-compose up -d

# View logs
docker-compose logs -f trash-detector

# Stop the service
docker-compose down
```

#### Option 2: Using Docker directly
```bash
# Build the image
docker build -t trash-detector:latest .

# Run the container
docker run -d \
  --name trash-detector \
  -p 8080:8080 \
  --device /dev/video0:/dev/video0 \
  -v $(pwd)/detections:/app/detections \
  trash-detector:latest

# View logs
docker logs -f trash-detector

# Stop the container
docker stop trash-detector
docker rm trash-detector
```

## API Endpoints

### 1. Health Check
```
GET http://localhost:8080/
GET http://localhost:8080/health
```

**Response:**
```json
{
  "message": "Trash Detection API is running 🚀",
  "version": "1.0.0"
}
```

### 2. Single Image Prediction
```
POST http://localhost:8080/predict/
```

**Request:**
- Form-data with image file (JPG, PNG, etc.)

**Response:**
```json
{
  "success": true,
  "filename": "image.jpg",
  "detections_count": 2,
  "timestamp": "2024-05-01T10:30:45.123456",
  "detections": [
    {
      "class": 0,
      "class_name": "trash",
      "confidence": 0.95,
      "bbox": {
        "x1": 100.5,
        "y1": 150.2,
        "x2": 250.8,
        "y2": 300.4
      }
    }
  ]
}
```

### 3. Batch Image Prediction
```
POST http://localhost:8080/batch-predict/
```

**Request:**
- Form-data with multiple image files

**Response:**
```json
{
  "total_images": 3,
  "results": [
    {
      "filename": "image1.jpg",
      "detections_count": 2,
      "detections": [...]
    }
  ]
}
```

### 4. Camera Snapshot with Detection
```
GET http://localhost:8080/camera/snapshot?camera_url=rtsp://192.168.1.100:554/stream
GET http://localhost:8080/camera/snapshot?camera_id=0
```

**Parameters:**
- `camera_url`: RTSP URL for CCTV camera (optional)
- `camera_id`: Local camera ID, default is 0 for webcam (optional)

**Response:**
- JPEG image with detection boxes drawn

### 5. Live Camera Stream (MJPEG)
```
GET http://localhost:8080/camera/stream?camera_url=rtsp://192.168.1.100:554/stream
GET http://localhost:8080/camera/stream?camera_id=0
```

**Parameters:**
- `camera_url`: RTSP URL for CCTV camera (optional)
- `camera_id`: Local camera ID, default is 0 for webcam (optional)

**Response:**
- Motion JPEG stream with real-time detection boxes

## CCTV Camera Integration

### RTSP URL Formats

Different CCTV cameras have different RTSP URL formats. Common examples:

```
# Hikvision
rtsp://username:password@192.168.1.100:554/Streaming/Channels/101

# Dahua
rtsp://username:password@192.168.1.100:554/stream/unicast/trackID=1

# Generic
rtsp://192.168.1.100:554/stream
```

### Example: Test with cURL

```bash
# Get a snapshot from CCTV camera
curl -o snapshot.jpg "http://localhost:8080/camera/snapshot?camera_url=rtsp://192.168.1.100:554/stream"

# Stream to a video file (10 seconds)
ffmpeg -i "http://localhost:8080/camera/stream?camera_url=rtsp://192.168.1.100:554/stream" \
  -t 10 -c:v libx264 output.mp4

# View stream in a browser or video player
# Open: http://localhost:8080/camera/stream?camera_url=rtsp://192.168.1.100:554/stream
```

## Website Integration Examples

### Python (requests)
```python
import requests

# Single image prediction
with open('image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8080/predict/', files=files)
    detections = response.json()
    print(detections)

# Get camera snapshot
response = requests.get('http://localhost:8080/camera/snapshot?camera_id=0')
with open('snapshot.jpg', 'wb') as f:
    f.write(response.content)
```

### JavaScript (Fetch API)
```javascript
// Single image prediction
async function predictImage(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch('http://localhost:8080/predict/', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  console.log(result);
}

// Display live stream
const img = document.getElementById('camera-feed');
img.src = 'http://localhost:8080/camera/stream?camera_id=0';

// Get snapshot
async function getSnapshot() {
  const response = await fetch('http://localhost:8080/camera/snapshot?camera_id=0');
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  document.getElementById('snapshot').src = url;
}
```

### cURL Examples
```bash
# Predict from image
curl -X POST -F "file=@image.jpg" http://localhost:8080/predict/

# Get camera snapshot
curl -o snapshot.jpg http://localhost:8080/camera/snapshot?camera_id=0

# Get health status
curl http://localhost:8080/health
```

## Performance Optimization

### Reduce Detection Frequency
Edit `src/main.py` in the `camera_stream` function:

```python
# Change this line to process every Nth frame
if frame_count % 5 == 0:  # Process every 5th frame instead of every frame
    results = model(frame)
    frame = results[0].plot()
```

### GPU Support
To enable GPU (CUDA) support in Docker:

```dockerfile
# In Dockerfile, use CUDA base image
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04
# ... rest of Dockerfile
```

Then run with:
```bash
docker run --gpus all -p 8080:8080 trash-detector:latest
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs trash-detector

# Or for direct docker run
docker logs <container_name>
```

### Camera connection issues
- Verify RTSP URL is correct
- Check firewall allows port 554
- Test RTSP URL with VLC: File > Open Network Stream

### High memory usage
- Reduce frame processing frequency
- Use GPU acceleration
- Resize frames before processing

### Slow performance
- Process every Nth frame instead of every frame
- Resize input frames
- Use a lighter YOLO model (yolo8n instead of yolo26n)

## Environment Variables

You can customize the API using environment variables:

```bash
# In docker-compose.yml
environment:
  - MODEL_PATH=/app/src/yolo26n.pt
  - LOG_LEVEL=info
```

## Detection Results Storage

Detection results are automatically saved as JSON in the `detections/` directory with timestamps. You can access them from your website backend.

## Next Steps

1. Deploy this Docker container to your server
2. Integrate the API endpoints into your website
3. Connect CCTV cameras via their RTSP URLs
4. Customize detection thresholds and model as needed
