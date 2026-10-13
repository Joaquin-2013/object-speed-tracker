"""
speed_tracker.py
================
Click on any moving object in your webcam feed and the program tracks it
and estimates its speed in km/h.

    - CLICK on the object  -> starts tracking it
    - If it gets lost      -> click on it again
    - ESC                  -> quit

IMPORTANT: set PIXELS_PER_METER for your scene, otherwise the km/h are not real.
(see the README: "How to calibrate")
"""

import cv2
import time

# ========================
# SETTINGS
# ========================
CAMERA_INDEX      = 0       # 0 = default webcam
PIXELS_PER_METER  = 50      # ⚠️ Calibrate for your scene (see README)
MOTION_THRESHOLD  = 2.0     # Minimum pixels per frame to count as movement
SMOOTHING_FRAMES  = 20      # Number of frames to average
BBOX_SIZE         = 100     # Size of the box created on click (bigger = more robust)
MAX_LOST_FRAMES   = 15      # After this many frames without tracking, ask for a new click


# ========================
# CREATE TRACKER  (CSRT is more robust than KCF)
# ========================
def create_tracker():
    try:
        return cv2.legacy.TrackerCSRT_create()
    except AttributeError:
        try:
            return cv2.TrackerCSRT_create()
        except AttributeError:
            # Fall back to KCF if CSRT is not available
            try:
                return cv2.legacy.TrackerKCF_create()
            except AttributeError:
                return cv2.TrackerKCF_create()


# ========================
# MOUSE STATE
# ========================
click_pos       = None
object_selected = False


def on_mouse(event, x, y, flags, param):
    global click_pos, object_selected
    if event == cv2.EVENT_LBUTTONDOWN:
        click_pos       = (x, y)
        object_selected = False


# ========================
# START CAMERA
# ========================
cap = cv2.VideoCapture(CAMERA_INDEX)
ret, frame = cap.read()
if not ret:
    print("Error: could not access the camera.")
    cap.release()
    exit()

cv2.namedWindow("Speed")
cv2.setMouseCallback("Speed", on_mouse)

# ========================
# STATE VARIABLES
# ========================
tracker       = None
prev_center   = None
prev_time     = time.time()
speeds        = []
active_bbox   = None
lost_frames   = 0             # Frames in a row without tracking

print("CLICK on the object you want to track.")
print("If it gets lost, click on it again.")
print("Press ESC to quit.")

# ========================
# MAIN LOOP
# ========================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # --- Start / restart the tracker after a click ---
    if click_pos is not None and not object_selected:
        cx, cy = click_pos
        half   = BBOX_SIZE // 2
        x0     = max(0, cx - half)
        y0     = max(0, cy - half)
        w0     = min(BBOX_SIZE, frame.shape[1] - x0)
        h0     = min(BBOX_SIZE, frame.shape[0] - y0)
        active_bbox = (x0, y0, w0, h0)

        tracker = create_tracker()
        tracker.init(frame, active_bbox)

        object_selected = True
        prev_center     = None
        prev_time       = time.time()
        speeds          = []
        lost_frames     = 0
        click_pos       = None

    # --- No object selected yet ---
    if tracker is None or not object_selected:
        cv2.putText(frame, "Click on the object to track",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 200, 255), 2)
        cv2.imshow("Speed", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
        continue

    # --- Update tracker ---
    success, bbox = tracker.update(frame)

    if success:
        lost_frames   = 0
        x, y, w, h    = [int(v) for v in bbox]
        center        = (x + w // 2, y + h // 2)
        current_time  = time.time()

        if prev_center is not None:
            dx             = center[0] - prev_center[0]
            dy             = center[1] - prev_center[1]
            distance_px    = (dx**2 + dy**2) ** 0.5
            elapsed_time   = current_time - prev_time

            if distance_px < MOTION_THRESHOLD or elapsed_time <= 0:
                speed_kmh = 0.0
            else:
                distance_m = distance_px / PIXELS_PER_METER
                speed_mps  = distance_m / elapsed_time
                speed_kmh  = speed_mps * 3.6

            speeds.append(speed_kmh)
            if len(speeds) > SMOOTHING_FRAMES:
                speeds.pop(0)
            smoothed_speed = sum(speeds) / len(speeds)

            cv2.putText(frame, f"{smoothed_speed:.1f} km/h",
                        (x, max(y - 12, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 255, 60), 2)

        prev_center = center
        prev_time   = current_time

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 140, 0), 2)
        cv2.circle(frame, center, 4, (0, 255, 60), -1)

    else:
        lost_frames += 1

        if lost_frames < MAX_LOST_FRAMES:
            bar = int((lost_frames / MAX_LOST_FRAMES) * 200)
            cv2.rectangle(frame, (20, 50), (20 + bar, 68), (0, 140, 255), -1)
            cv2.rectangle(frame, (20, 50), (220, 68), (0, 140, 255), 2)
            cv2.putText(frame, "Searching for object...",
                        (20, 42), cv2.FONT_HERSHEY_SIMPLEX,
                        0.65, (0, 200, 255), 2)
        else:
            object_selected = False
            speeds          = []
            cv2.putText(frame, "Object lost. Click again.",
                        (20, 42), cv2.FONT_HERSHEY_SIMPLEX,
                        0.65, (0, 0, 255), 2)

    cv2.putText(frame, "Click = select  |  ESC = quit",
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

    cv2.imshow("Speed", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
