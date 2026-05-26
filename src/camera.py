import cv2
from ultralytics import YOLO
from waste_classes import waste_class_indices, predict_kwargs

model = YOLO("yolo26n.pt", task="detect")
_PREDICT_KW = predict_kwargs(waste_class_indices(model.names))
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    results = model.predict(frame, **_PREDICT_KW)
    frame = results[0].plot()

    cv2.imshow("OceanAI Guard", frame)

    if cv2.waitKey(1) == 27:  # press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()