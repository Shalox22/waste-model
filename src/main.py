from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
from waste_classes import waste_class_indices, predict_kwargs
import cv2
import numpy as np
import os
from pathlib import Path
import json
from datetime import datetime
import shutil
import uuid

app = FastAPI(
    title="Trash Detection API",
    description="YOLO-based trash detection API with camera/CCTV integration",
    version="1.0.0"
)

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT_DIR / "model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_MODEL_NAME = os.getenv("MODEL_PATH", "yolo26n.pt")
ACTIVE_MODEL_PATH = MODEL_DIR / DEFAULT_MODEL_NAME

def load_yolo_model(path: Path):
    return YOLO(str(path), task="detect")

# Load model once
if not ACTIVE_MODEL_PATH.exists():
    raise RuntimeError(f"Model file not found: {ACTIVE_MODEL_PATH}")

model = load_yolo_model(ACTIVE_MODEL_PATH)
_PREDICT_KW = predict_kwargs(waste_class_indices(model.names))

# Create detections directory if it doesn't exist
DETECTIONS_DIR = ROOT_DIR / "detections"
DETECTIONS_DIR.mkdir(exist_ok=True)


@app.get("/")
def home():
    """Health check endpoint"""
    return {
        "message": "Trash Detection API is running 🚀",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict_image": "/predict/",
            "camera_stream": "/camera/stream?camera_url=rtsp://...",
            "camera_snapshot": "/camera/snapshot?camera_url=rtsp://..."
        }
    }


@app.get("/health")
def health():
    """Health check for Docker"""
    return {"status": "healthy", "model_loaded": model is not None, "model_path": str(ACTIVE_MODEL_PATH)}


@app.get("/models/status")
def model_status():
    return {
        "model_loaded": model is not None,
        "model_path": str(ACTIVE_MODEL_PATH),
        "classes": list(model.names) if model is not None else [],
    }


@app.post("/models/upload")
async def upload_model(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    ext = Path(file.filename).suffix.lower()
    if ext not in {".pt", ".onnx"}:
        raise HTTPException(status_code=400, detail="Model file must be .pt or .onnx")

    temp_path = MODEL_DIR / f"upload_{uuid.uuid4().hex}{ext}"
    try:
        contents = await file.read()
        temp_path.write_bytes(contents)

        new_model = load_yolo_model(temp_path)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=400, detail=f"Invalid model file: {str(e)}")

    final_path = MODEL_DIR / file.filename
    if final_path.exists():
        backup_path = MODEL_DIR / f"backup_{uuid.uuid4().hex}{ext}"
        final_path.rename(backup_path)
    try:
        temp_path.replace(final_path)
        global model, _PREDICT_KW, ACTIVE_MODEL_PATH
        model = new_model
        ACTIVE_MODEL_PATH = final_path
        _PREDICT_KW = predict_kwargs(waste_class_indices(model.names))
    except Exception as e:
        if final_path.exists():
            final_path.unlink()
        if 'backup_path' in locals() and backup_path.exists():
            backup_path.replace(final_path)
        raise HTTPException(status_code=500, detail=f"Failed to activate model: {str(e)}")
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        if 'backup_path' in locals() and backup_path.exists():
            backup_path.unlink(missing_ok=True)

    return {
        "success": True,
        "filename": file.filename,
        "model_path": str(ACTIVE_MODEL_PATH),
        "classes": list(model.names)
    }


@app.post("/predict/")
async def predict_image(file: UploadFile = File(...)):
    """
    Predict trash in uploaded image
    
    Args:
        file: Image file (JPG, PNG, etc.)
    
    Returns:
        Detections with bounding boxes and confidence scores
    """
    try:
        # Read image
        contents = await file.read()
        np_img = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")

        # Run detection
        results = model(img, **_PREDICT_KW)

        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    "class": int(box.cls),
                    "class_name": model.names[int(box.cls)],
                    "confidence": float(box.conf),
                    "bbox": {
                        "x1": float(box.xyxy[0][0]),
                        "y1": float(box.xyxy[0][1]),
                        "x2": float(box.xyxy[0][2]),
                        "y2": float(box.xyxy[0][3])
                    }
                })

        # Save detection result
        timestamp = datetime.now().isoformat()
        result_file = DETECTIONS_DIR / f"detection_{timestamp.replace(':', '-')}.json"
        with open(result_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "filename": file.filename,
                "detections_count": len(detections),
                "detections": detections
            }, f, indent=2)

        return {
            "success": True,
            "filename": file.filename,
            "detections_count": len(detections),
            "detections": detections,
            "timestamp": timestamp
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/camera/snapshot")
async def camera_snapshot(camera_url: str = None, camera_id: int = 0):
    """
    Get a snapshot from camera with detections
    
    Args:
        camera_url: RTSP URL for CCTV (e.g., rtsp://192.168.1.100:554/stream)
        camera_id: Local camera ID (default 0 for webcam)
    
    Returns:
        Image with bounding boxes drawn
    """
    try:
        if camera_url:
            cap = cv2.VideoCapture(camera_url)
        else:
            cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Cannot open camera")
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise HTTPException(status_code=400, detail="Failed to read frame")
        
        # Run detection
        results = model(frame, **_PREDICT_KW)
        
        # Draw results on frame
        annotated_frame = results[0].plot()
        
        # Encode as JPG
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        
        return StreamingResponse(
            iter([buffer.tobytes()]),
            media_type="image/jpeg"
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Camera error: {str(e)}")


@app.get("/camera/stream")
async def camera_stream(camera_url: str = None, camera_id: int = 0):
    """
    Stream camera with real-time detections (Motion JPEG)
    
    Args:
        camera_url: RTSP URL for CCTV (e.g., rtsp://192.168.1.100:554/stream)
        camera_id: Local camera ID (default 0 for webcam)
    
    Returns:
        MJPEG stream with detection boxes
    """
    async def generate():
        try:
            if camera_url:
                cap = cv2.VideoCapture(camera_url)
            else:
                cap = cv2.VideoCapture(camera_id)
            
            if not cap.isOpened():
                raise ValueError("Cannot open camera")
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Run detection every frame (or every N frames for performance)
                if frame_count % 1 == 0:  # Change to frame_count % 5 to process every 5th frame
                    results = model(frame, **_PREDICT_KW)
                    frame = results[0].plot()
                
                # Encode frame to JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + f'{len(frame_bytes)}'.encode() + b'\r\n\r\n'
                       + frame_bytes + b'\r\n')
                
                frame_count += 1
            
            cap.release()
        
        except Exception as e:
            print(f"Stream error: {e}")
    
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.post("/batch-predict/")
async def batch_predict(files: list[UploadFile] = File(...)):
    """
    Predict trash in multiple images
    
    Args:
        files: Multiple image files
    
    Returns:
        List of detections for each image
    """
    results_list = []
    
    for file in files:
        try:
            contents = await file.read()
            np_img = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            
            if img is None:
                results_list.append({
                    "filename": file.filename,
                    "error": "Invalid image format"
                })
                continue
            
            results = model(img, **_PREDICT_KW)
            detections = []
            
            for r in results:
                for box in r.boxes:
                    detections.append({
                        "class": int(box.cls),
                        "class_name": model.names[int(box.cls)],
                        "confidence": float(box.conf),
                        "bbox": {
                            "x1": float(box.xyxy[0][0]),
                            "y1": float(box.xyxy[0][1]),
                            "x2": float(box.xyxy[0][2]),
                            "y2": float(box.xyxy[0][3])
                        }
                    })
            
            results_list.append({
                "filename": file.filename,
                "detections_count": len(detections),
                "detections": detections
            })
        
        except Exception as e:
            results_list.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "total_images": len(files),
        "results": results_list
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("APP_PORT", "8080")),
    )