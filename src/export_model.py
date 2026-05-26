from ultralytics import YOLO

# load your model
model = YOLO("yolo26n.pt")

# export to ONNX
model.export(format="onnx")

print("✅ Export completed!")