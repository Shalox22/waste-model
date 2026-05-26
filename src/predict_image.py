from ultralytics import YOLO

model = YOLO("yolo26n.pt")
model.predict("test.jpg", save=True)