import cv2
import numpy as np
import time
import random
import math

# ==========================================
# FUNGSI PENGOLAHAN CITRA MANUAL (NUMPY)
# ==========================================

def manual_hsv_mask(hsv_frame, lower_hsv, upper_hsv):
    """Masking warna kulit secara manual dengan operasi boolean NumPy."""
    h, s, v = hsv_frame[:, :, 0], hsv_frame[:, :, 1], hsv_frame[:, :, 2]
    mask = (
        (h >= lower_hsv[0]) & (h <= upper_hsv[0]) &
        (s >= lower_hsv[1]) & (s <= upper_hsv[1]) &
        (v >= lower_hsv[2]) & (v <= upper_hsv[2])
    )
    return (mask.astype(np.uint8) * 255)

def manual_dilate(binary_mask):
    """Dilasi manual menggunakan pergeseran matriks (np.roll)."""
    up = np.roll(binary_mask, -1, axis=0)
    down = np.roll(binary_mask, 1, axis=0)
    left = np.roll(binary_mask, -1, axis=1)
    right = np.roll(binary_mask, 1, axis=1)
    return binary_mask | up | down | left | right

def manual_erode(binary_mask):
    """Erosi manual menggunakan pergeseran matriks."""
    up = np.roll(binary_mask, -1, axis=0)
    down = np.roll(binary_mask, 1, axis=0)
    left = np.roll(binary_mask, -1, axis=1)
    right = np.roll(binary_mask, 1, axis=1)
    return binary_mask & up & down & left & right

def manual_alpha_blend(bg_img, fg_img, x_center, y_center):
    """Menempelkan objek foreground (dengan alpha) ke background secara manual."""
    if x_center == 0 and y_center == 0: return bg_img
    
    fh, fw = fg_img.shape[:2]
    bh, bw = bg_img.shape[:2]
    
    x1, y1 = int(x_center - fw/2), int(y_center - fh/2)
    x2, y2 = x1 + fw, y1 + fh
    
    # Crop fg jika keluar batas
    src_x1, src_y1 = 0, 0
    src_x2, src_y2 = fw, fh

    if x1 < 0: src_x1 = abs(x1); x1 = 0
    if y1 < 0: src_y1 = abs(y1); y1 = 0
    if x2 > bw: src_x2 = fw - (x2 - bw); x2 = bw
    if y2 > bh: src_y2 = fh - (y2 - bh); y2 = bh

    if x2 <= x1 or y2 <= y1 or src_x2 <= src_x1 or src_y2 <= src_y1:
        return bg_img
    
    # Ambil ROI dan sub-gambar fg yang valid
    bg_roi = bg_img[y1:y2, x1:x2]
    fg_cropped = fg_img[src_y1:src_y2, src_x1:src_x2]
    
    fg_rgb = fg_cropped[:, :, :3]
    alpha = fg_cropped[:, :, 3] / 255.0
    alpha = np.expand_dims(alpha, axis=2)
    
    blended = (fg_rgb * alpha) + (bg_roi * (1.0 - alpha))
    bg_img[y1:y2, x1:x2] = blended.astype(np.uint8)
    return bg_img

# ==========================================
# INISIALISASI GAME & KAMERA
# ==========================================

# Validasi Aset
sword_img = cv2.imread('assets/sword.png', cv2.IMREAD_UNCHANGED)
rock_img = cv2.imread('assets/rock.png', cv2.IMREAD_UNCHANGED)

if sword_img is None or rock_img is None:
    print("Error: Aset gambar tidak ditemukan di folder assets/")
    exit()

sword_img = cv2.resize(sword_img, (150, 150))
rock_img = cv2.resize(rock_img, (80, 80))

cap = cv2.VideoCapture(0)

# Rentang warna HSV untuk kulit (Sesuaikan dengan pencahayaan Anda!)
# Tip: Jika masih menempel di muka, coba naikkan batas bawah S (LOWER_SKIN[1]) sedikit.
LOWER_SKIN = np.array([0, 30, 60], dtype=np.uint8)
UPPER_SKIN = np.array([25, 255, 255], dtype=np.uint8)

# Variabel Game
score = 0
rocks = []
prev_hand_x, prev_hand_y = 0, 0
slash_threshold = 35 

# --- PARAMETER UNTUK MENGHINDARI WAJAH ---
# Kita asumsikan wajah berada di area atas tengah frame.
# Kita buat "Zona Terlarang" di bagian atas agar pedang tidak muncul di sana.
forbidden_zone_height_ratio = 0.4 # 40% area atas dianggap zona wajah/gangguan

while True:
    ret, frame = cap.read()
    if not ret: break
        
    frame = cv2.flip(frame, 1) # Mirror
    h, w = frame.shape[:2]
    
    # 1. Konversi ke HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 2. Manual Skin Masking
    mask = manual_hsv_mask(hsv_frame, LOWER_SKIN, UPPER_SKIN)
    
    # 3. Manual Morphology (Membersihkan noise)
    # Erosi lebih kuat untuk memisahkan koneksi tipis antara tangan dan lengan
    mask_clean = manual_erode(mask)
    mask_clean = manual_erode(mask_clean) # Erosi x2
    mask_clean = manual_dilate(mask_clean)
    mask_clean = manual_dilate(mask_clean) # Dilasi x2
    
    # 4. Cari Posisi Tangan dengan Heuristik (Mengabaikan Muka)
    
    # A. Terapkan Zona Terlarang (Forbidden Zone) di mask
    # Ubah 40% area atas mask menjadi hitam (abaikan wajah)
    forbidden_h = int(h * forbidden_zone_height_ratio)
    mask_clean[0:forbidden_h, :] = 0 
    
    # Untuk debug: gambar garis batas zona terlarang
    # cv2.line(frame, (0, forbidden_h), (w, forbidden_h), (0, 0, 255), 2)

    # B. Temukan Contours menggunakan OpenCV (untuk mencari blob terbesar di area valid)
    # Ini diperbolehkan untuk 'pengenalan objek', sedangkan masking/morfologi tetap manual numpy.
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    hand_x, hand_y = 0, 0
    is_slashing = False
    
    if contours:
        # Cari kontur dengan area terbesar di area valid (asumsi ini adalah tangan/lengan bawah)
        largest_contour = max(contours, key=cv2.contourArea)
        
        if cv2.contourArea(largest_contour) > 1000: # Batas minimum area tangan
            # Hitung Moments untuk mencari centroid
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                hand_x = int(M["m10"] / M["m00"])
                hand_y = int(M["m01"] / M["m00"])
                
                # 5. Gesture Recognition (Kecepatan)
                distance = math.sqrt((hand_x - prev_hand_x)**2 + (hand_y - prev_hand_y)**2)
                if distance > slash_threshold and prev_hand_x != 0:
                    is_slashing = True
                    
                prev_hand_x, prev_hand_y = hand_x, hand_y
                
                # 6. Menempelkan Pedang (Manual Alpha Blending)
                frame = manual_alpha_blend(frame, sword_img, hand_x, hand_y)
    else:
        prev_hand_x, prev_hand_y = 0, 0 # Reset jika tangan hilang

    # 7. Game Logic: Batu
    if random.random() < 0.025: 
        rocks.append({'x': random.randint(50, w-50), 'y': -50, 'speed': random.randint(6, 14)})
        
    for rock in rocks[:]:
        rock['y'] += rock['speed']
        
        # Menempelkan batu
        frame = manual_alpha_blend(frame, rock_img, rock['x'], rock['y'])
        
        # Collision Detection
        if hand_x != 0 and hand_y != 0:
            dist_to_rock = math.sqrt((hand_x - rock['x'])**2 + (hand_y - rock['y'])**2)
            if dist_to_rock < 70: # Radius benturan
                if is_slashing:
                    score += 10
                    rocks.remove(rock)
                    continue
                
        if rock['y'] > h + 50:
            rocks.remove(rock)

    # 8. Tampilkan UI
    cv2.putText(frame, f'SCORE: {score}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 255), 3)
    if is_slashing:
        cv2.putText(frame, 'SLASH!', (w - 180, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    # Debug windows
    cv2.imshow('Mask Clean (Hands Only)', mask_clean)
    cv2.imshow('Stone Slicer', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()