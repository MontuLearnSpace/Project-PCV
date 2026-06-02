import cv2
import numpy as np
import random
import math
from collections import deque

# ==========================================================
# MANUAL MORPHOLOGY
# ==========================================================
def erosion(img):
    h, w = img.shape
    result = np.zeros_like(img)
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            area = img[y - 1:y + 2, x - 1:x + 2]
            if np.all(area == 255):
                result[y, x] = 255
    return result


def dilation(img):
    h, w = img.shape
    result = np.zeros_like(img)
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            area = img[y - 1:y + 2, x - 1:x + 2]
            if np.any(area == 255):
                result[y, x] = 255
    return result

def opening(img):
    eroded = erosion(img)
    opened = dilation(eroded)
    return opened

def closing(img):
    dilated = dilation(img)
    closed = erosion(dilated)
    return closed

# ==========================================================
# MANUAL ALPHA BLENDING
# ==========================================================
def overlay_png(background, sprite, x, y):
    if sprite is None:
        return background
    h, w = sprite.shape[:2]
    if x < 0:
        return background
    if y < 0:
        return background
    if x + w > background.shape[1]:
        return background
    if y + h > background.shape[0]:
        return background
    roi = background[y:y+h, x:x+w]
    # PNG transparan
    if sprite.shape[2] == 4:
        alpha = sprite[:, :, 3] / 255.0
        for c in range(3):
            roi[:, :, c] = (
                alpha * sprite[:, :, c]
                +
                (1 - alpha) * roi[:, :, c]
            )
    # JPG / RGB biasa
    else:
        roi[:] = sprite
    background[y:y+h, x:x+w] = roi
    return background

# ==========================================================
# LOAD WEAPON
# ==========================================================
sword = cv2.imread(
    "assets/sword.png",
    cv2.IMREAD_UNCHANGED
)
if sword is None:
    raise Exception(
        "ERROR: assets/sword.png tidak ditemukan"
    )
sword = cv2.resize(
    sword,
    (222, 222)
)

# ==========================================================
# LOAD STONES
# ==========================================================
stone1 = cv2.imread(
    "assets/stone1.png",
    cv2.IMREAD_UNCHANGED
)
stone2 = cv2.imread(
    "assets/stone2.png",
    cv2.IMREAD_UNCHANGED
)
stone3 = cv2.imread(
    "assets/stone3.png",
    cv2.IMREAD_UNCHANGED
)
stone4 = cv2.imread(
    "assets/stone4.png",
    cv2.IMREAD_UNCHANGED
)
stone5 = cv2.imread(
    "assets/stone5.png",
    cv2.IMREAD_UNCHANGED
)
stone_imgs = [
    stone1,
    stone2,
    stone3,
    stone4,
    stone5
]

# ==========================================================
# VALIDASI ASSET
# ==========================================================
for i, stone in enumerate(stone_imgs):
    if stone is None:
        raise Exception(
            f"ERROR: assets/stone{i+1}.png tidak ditemukan"
        )

# ==========================================================
# DEBUG INFO
# ==========================================================
print("=" * 40)
print("ASSET LOADED")
print("=" * 40)
print("Sword :", sword.shape)

for i, stone in enumerate(stone_imgs):
    print(
        f"Stone {i+1}:",
        stone.shape
    )
print("=" * 40)

# ==========================================================
# CLASS STONE
# ==========================================================
class Stone:
    def __init__(self):
        self.respawn()
    def respawn(self):
        # Pilih bentuk batu secara acak
        self.img = random.choice(stone_imgs)
        # Ukuran acak
        size = random.randint(50, 90)
        self.img = cv2.resize(
            self.img,
            (size, size)
        )
        self.width = self.img.shape[1]
        self.height = self.img.shape[0]
        # Posisi spawn dari atas layar
        self.x = random.randint(
            20,
            640 - self.width - 20
        )
        self.y = -self.height
        # Kecepatan jatuh
        self.speed = random.randint(
            3,
            7
        )
    def update(self):
        self.y += self.speed
    def draw(self, frame):
        overlay_png(
            frame,
            self.img,
            self.x,
            self.y
        )

# ==========================================================
# GAME INITIALIZATION
# ==========================================================
score = 0
hp = 3
level = 1
combo = 0
max_combo = 0
game_over = False

# ==========================================================
# CREATE STONES
# ==========================================================
stones = []
STONE_COUNT = 5
for _ in range(STONE_COUNT):
    stones.append(
        Stone()
    )

# ==========================================================
# WEBCAM INITIALIZATION
# ==========================================================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception(
        "ERROR: Webcam tidak dapat dibuka"
    )
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    FRAME_WIDTH
)
cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    FRAME_HEIGHT
)

# ==========================================================
# SWIPE GESTURE VARIABLES
# ==========================================================
hand_positions = deque(maxlen=10)
hand_detected = False
hand_x = 0
hand_y = 0

# Gesture Status
attack = False
attack_timer = 0
ATTACK_DURATION = 10
SWIPE_THRESHOLD = 40

# ==========================================================
# FPS VARIABLES
# ==========================================================
fps = 0
prev_tick = cv2.getTickCount()

# ==========================================================
# LEVEL SYSTEM
# ==========================================================
LEVEL_UP_SCORE = 10

# ==========================================================
# COLOR CONSTANTS
# ==========================================================
GREEN = (0, 255, 0)
RED = (0, 0, 255)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
WHITE = (255, 255, 255)

# ==========================================================
# DEBUG
# ==========================================================
print("=" * 40)
print("GAME INITIALIZED")
print("=" * 40)

print(f"Jumlah Batu : {STONE_COUNT}")
print(f"HP Awal     : {hp}")
print(f"Score Awal  : {score}")

print("=" * 40)

# ==========================================================
# MAIN GAME LOOP
# ==========================================================
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    hand_detected = False

    # ======================================================
    # HSV SKIN DETECTION
    # ======================================================
    hsv = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2HSV
    )
    lower_skin = np.array(
        [0, 20, 70],
        dtype=np.uint8
    )
    upper_skin = np.array(
        [20, 255, 255],
        dtype=np.uint8
    )
    mask = cv2.inRange(
        hsv,
        lower_skin,
        upper_skin
    )

    # ======================================================
    # MANUAL MORPHOLOGY
    # ======================================================

    small_mask = cv2.resize(
        mask,
        (320, 240)
    )
 #   small_mask = opening(
 #       small_mask
  #  )
  #  small_mask = closing(
 #       small_mask
  #  )  
    mask = cv2.resize(
        small_mask,
        (640, 480)
    )

    # ======================================================
    # FIND CONTOUR
    # ======================================================
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # ======================================================
    # HAND DETECTION
    # ======================================================
    if contours:
        largest = max(
            contours,
            key=cv2.contourArea
        )
        area = cv2.contourArea(
            largest
        )
        if area > 3000:
            hand_detected = True
            hull = cv2.convexHull(
                largest
            )
            cv2.drawContours(
                frame,
                [largest],
                -1,
                GREEN,
                2
            )
            cv2.drawContours(
                frame,
                [hull],
                -1,
                BLUE,
                2
            )
            M = cv2.moments(
                largest
            )
            if M["m00"] != 0:
                hand_x = int(
                    M["m10"] /
                    M["m00"]
                )
                hand_y = int(
                    M["m01"] /
                    M["m00"]
                )
                cv2.circle(
                    frame,
                    (hand_x, hand_y),
                    8,
                    RED,
                    -1
                )
                hand_positions.append(
                    (
                        hand_x,
                        hand_y
                    )
                )

    # ======================================================
    # SWIPE DETECTION
    # ======================================================
    swipe_speed = 0
    if len(hand_positions) >= 5:
        x1, y1 = hand_positions[0]
        x2, y2 = hand_positions[-1]
        dx = x2 - x1
        dy = y2 - y1
        swipe_speed = math.sqrt(
            dx * dx +
            dy * dy
        )
        if swipe_speed > SWIPE_THRESHOLD:
            attack = True
            attack_timer = ATTACK_DURATION

    # ======================================================
    # ATTACK TIMER
    # ======================================================
    if attack_timer > 0:
        attack_timer -= 1
    else:
        attack = False

    # ======================================================
    # DRAW SWORD
    # ======================================================
    sword_w = sword.shape[1]
    sword_h = sword.shape[0]
    sword_x = hand_x - sword_w // 2
    sword_y = hand_y - sword_h // 2
    if hand_detected:
        frame = overlay_png(
            frame,
            sword,
            sword_x,
            sword_y
        )

    # ======================================================
    # LEVEL SYSTEM
    # ======================================================
    level = (
        score // LEVEL_UP_SCORE
    ) + 1

    # ======================================================
    # UPDATE STONES
    # ======================================================
    if not game_over:
        for stone in stones:
            stone.speed = min(
                5 + level,
                15
            )
            stone.update()
            stone.draw(frame)
            stone_w = stone.width
            stone_h = stone.height
            collision = (
                sword_x <
                stone.x + stone_w
                and
                sword_x + sword_w >
                stone.x
                and
                sword_y <
                stone.y + stone_h
                and
                sword_y + sword_h >
                stone.y
            )

            # ==========================================
            # HIT STONE
            # ==========================================
            if (
                collision
                and attack
                and hand_detected
            ):
                score += 1
                combo += 1
                max_combo = max(
                    max_combo,
                    combo
                )
                stone.respawn()

            # ==========================================
            # STONE ESCAPE
            # ==========================================
            if stone.y > FRAME_HEIGHT:
                hp -= 1
                combo = 0
                stone.respawn()

    # ======================================================
    # GAME OVER
    # =====================================================
    if hp <= 0:
        game_over = True

    # ======================================================
    # FPS CALCULATION
    # ======================================================
    current_tick = cv2.getTickCount()
    time_elapsed = (
        current_tick -
        prev_tick
    ) / cv2.getTickFrequency()
    prev_tick = current_tick
    if time_elapsed > 0:
        fps = int(
            1 / time_elapsed
        )

    # ======================================================
    # UI
    # ======================================================
    cv2.putText(
        frame,
        f"Score : {score}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        GREEN,
        2
    )
    cv2.putText(
        frame,
        f"HP : {hp}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        RED,
        2
    )
    cv2.putText(
        frame,
        f"Level : {level}",
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        YELLOW,
        2
    )
    cv2.putText(
        frame,
        f"Combo : {combo}",
        (20, 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        WHITE,
        2
    )
    cv2.putText(
        frame,
        f"FPS : {fps}",
        (20, 180),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        GREEN,
        2
    )
    cv2.putText(
        frame,
        f"Swipe : {int(swipe_speed)}",
        (20, 215),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        BLUE,
        2
    )
    status = (
        "ATTACK"
        if attack
        else "IDLE"
    )
    cv2.putText(
        frame,
        status,
        (20, 250),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        YELLOW,
        2
    )

    # ======================================================
    # GAME OVER SCREEN
    #=======================================================
    if game_over:
        cv2.putText(
            frame,
            "GAME OVER",
            (150, 220),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            RED,
            4
        )
        cv2.putText(
            frame,
            f"FINAL SCORE : {score}",
            (150, 280),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            WHITE,
            3
        )

    # ======================================================
    # SHOW WINDOWS
    # ======================================================
    cv2.imshow(
        "Stone Slicer",
        frame
    )
#    cv2.imshow(
#        "Hand Mask",
    #    mask
 #   )
    key = cv2.waitKey(1)
    if key == 27:
        break

# ==========================================================
# CLEANUP
# ==========================================================
cap.release()
cv2.destroyAllWindows()