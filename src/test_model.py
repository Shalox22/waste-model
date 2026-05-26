from ultralytics import YOLO
from ultralytics import YOLO

model = YOLO("yolo26n.pt")

results = model.predict("C:/Users/sammb/Desktop/JSS/src/test.jpg", save=True)

print("✅ Done")