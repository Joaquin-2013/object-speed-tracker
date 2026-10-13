# 🎯💨 Object Speed Tracker

> Click on any moving object in your webcam and the program **tracks it and shows its speed in km/h**. 😎

I made a small Python program with OpenCV that:
- opens your webcam 📷
- lets you **click on an object** (a ball, a toy car, a person walking...)
- follows it with a box and shows its **estimated speed** right above it
- if the object gets lost, you just **click on it again**

Everything lives in **one single file**: `speed_tracker.py`. 🎉

---

## 🧠 How does it work?

```
 click on object ──▶ CSRT tracker follows it frame by frame
                              │
              distance moved (pixels) ÷ PIXELS_PER_METER = meters
                              │
                 meters ÷ time between frames = m/s  ──▶  × 3.6 = km/h
                              │
              average of the last 20 frames (so it doesn't jump around)
```

1. When you click, the program draws a 100×100 px box around that point and starts tracking it.
2. For every frame it measures how many pixels the center of the box moved.
3. It converts pixels to meters (using your calibration) and divides by the real time between frames.
4. It averages the last few values so the number is smooth and readable.

---

## 🛠️ What you need

- Python 3.8 or newer
- A webcam
- OpenCV **with the contrib modules** (the CSRT tracker lives there)

---

## 🚀 Installation (step by step)

### 1. Get the project
```bash
git clone https://github.com/YOUR_USERNAME/object-speed-tracker.git
cd object-speed-tracker
```

### 2. (Recommended) Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac / Linux
```

### 3. Install OpenCV
```bash
pip install -r requirements.txt
```
> ⚠️ Install **`opencv-contrib-python`** and **not** `opencv-python` at the same time. Having both causes weird errors. If you already have `opencv-python`, run `pip uninstall opencv-python` first.

### 4. Run it!
```bash
python speed_tracker.py
```

---

## 🎮 How to use it

| Action | What happens |
|--------|--------------|
| **Left click** on an object | Starts tracking it |
| Object goes out of view | Shows *"Searching for object..."* and then *"Object lost. Click again."* |
| **Click** again | Tracks a new object (or the same one) |
| `ESC` | Quit |

---

## 📏 How to calibrate (IMPORTANT!)

The speed is only correct if the program knows **how many pixels equal one meter** in your scene. The default (`PIXELS_PER_METER = 50`) is just a placeholder.

1. Put an object of **known length** in your scene, at the **same distance** from the camera as the thing you want to measure (a ruler, a meter stick, a sheet of paper...).
2. Find out how many **pixels** it takes up on screen (take a screenshot and measure it in any image editor, or hover over its ends in Paint).
3. Do this:
   ```
   PIXELS_PER_METER = length_in_pixels / real_length_in_meters
   ```
   Example: a 0.30 m ruler that is 150 px long → `150 / 0.30 = 500`
4. Change the number at the top of `speed_tracker.py`:
   ```python
   PIXELS_PER_METER = 500
   ```

---

## ⚙️ Things you can tweak (top of the file)

| Variable | What it does |
|----------|--------------|
| `CAMERA_INDEX` | Which camera to use (0 = default, 1 = second camera...) |
| `PIXELS_PER_METER` | **The calibration** (see above) |
| `MOTION_THRESHOLD` | Minimum pixels moved per frame to count as movement. Raise it if the number jitters when the object is still |
| `SMOOTHING_FRAMES` | How many frames to average. Higher = smoother but slower to react |
| `BBOX_SIZE` | Size of the box made on click. Use a bigger one for bigger objects |
| `MAX_LOST_FRAMES` | How long to keep searching before giving up |

---

## ⚠️ Limitations (please read)

This is an **estimate**, not a speed gun. 🚨

- It only measures movement **across the image**. If the object moves **toward or away** from the camera, the speed will be wrong.
- The calibration is only valid for objects at **the same distance** as your reference. Closer objects look faster, farther ones look slower.
- Wide-angle lenses (like many phone and laptop cameras) distort the image, which adds error near the edges.
- Fast objects can blur or leave the frame, and the tracker may lose them.
- Don't use it for anything safety-critical or to measure the speed of real vehicles.

---

## 🐛 Common problems

- **`AttributeError: ... TrackerCSRT_create`:** you don't have the contrib modules. Run `pip uninstall opencv-python` and then `pip install opencv-contrib-python`.
- **"Error: could not access the camera":** close other apps using the webcam, or change `CAMERA_INDEX` to `1`.
- **The box drifts or jumps to something else:** click again, using a bigger `BBOX_SIZE` and an object that stands out from the background.
- **Shows speed when the object is still:** raise `MOTION_THRESHOLD` (try 3 or 4).
- **The km/h look way off:** calibrate `PIXELS_PER_METER` (see above).

---

## 📁 Project layout

```
object-speed-tracker/
├── speed_tracker.py   # the whole program
├── requirements.txt   # libraries
├── .gitignore
├── LICENSE
└── README.md          # this file
```

---

## 💡 Ideas for later

- [ ] Select the object by drawing a box instead of a single click
- [ ] Show the speed in m/s or mph with a key press
- [ ] Draw the trail of the object's path
- [ ] Save the speed readings to a CSV file
- [ ] Use a video file instead of the webcam

---

Made with ❤️, lots of coffee and plenty of bugs by **Joaquín**.
If you liked it, drop a ⭐ on the repo!
