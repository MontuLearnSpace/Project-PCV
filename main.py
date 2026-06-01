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
    """Dilasi manual menggunakan pergeseran matriks (np.roll) agar lebih cepat dari iterasi for loop."""
    up = np.roll(binary_mask, -1, axis=0)
    down = np.roll(binary_mask, 1, axis=0)
    left = np.roll(binary_mask, -1, axis=1)
    right = np.roll(binary_mask, 1, axis=1)
    # Logika OR
    return binary_mask | up | down | left | right

def manual_erode(binary_mask):
    """Erosi manual menggunakan pergeseran matriks."""
    up = np.roll(binary_mask, -1, axis=0)
    down = np.roll(binary_mask, 1, axis=0)
    left = np.roll(binary_mask, -1, axis=1)
    right = np.roll(binary_mask, 1, axis=1)
    # Logika AND
    return binary_mask & up & down & left & right

def manual_alpha_blend(bg_img, fg_img, x_center, y_center):
    """Menempelkan objek foreground (dengan alpha) ke background secara manual."""
    fh, fw = fg_img.shape[:2]
    bh, bw = bg_img.shape[:2]
    
    # Hitung batas koordinat (Bounding Box)
    x1, y1 = int(x_center - fw/2), int(y_center - fh/2)
    x2, y2 = x1 + fw, y1 + fh
    
    # Mencegah error jika gambar keluar dari frame layar
    if x1 < 0 or y1 < 0 or x2 >= bw or y2 >= bh:
        return bg_img
    
    # Ekstrak Region of Interest (ROI) dari background
    bg_roi = bg_img[y1:y2, x1:x2]
    
    # Pisahkan channel warna dan alpha dari foreground
    fg_rgb = fg_img[:, :, :3]
    alpha = fg_img[:, :, 3] / 255.0 # Normalisasi alpha 0.0 - 1.0
    alpha = np.expand_dims(alpha, axis=2) # Bentuk (H, W, 1) agar bisa dikalikan dengan RGB
    
    # Rumus Alpha Blending Manual: C_out = (C_fg * alpha) + (C_bg * (1 - alpha))
    blended = (fg_rgb * alpha) + (bg_roi * (1.0 - alpha))
    
    # Masukkan kembali ke background asli
    bg_img[y1:y2, x1:x2] = blended.astype(np.uint8)
    return bg_img

# ==========================================
# INISIALISASI GAME & KAMERA
# ==========================================

# Ganti 'assets/sword.png' dan 'assets/rock.png' dengan path Anda
# Wajib menggunakan cv2.IMREAD_UNCHANGED untuk membaca channel alpha (transparansi)
sword_img = cv2.imread('assets/sword.png', cv2.IMREAD_UNCHANGED)
rock_img = cv2.imread('assets/rock.png', cv2.IMREAD_UNCHANGED)

# Resize aset agar tidak terlalu besar
sword_img = cv2.resize(sword_img, (120, 120))
rock_img = cv2.resize(rock_img, (80, 80))

cap = cv2.VideoCapture(0)

# Rentang warna HSV untuk kulit (Sesuaikan dengan pencahayaan ruangan Anda)
LOWER_SKIN = np.array([0, 40, 60], dtype=np.uint8)
UPPER_SKIN = np.array([20, 255, 255], dtype=np.uint8)

# Variabel Game
score = 0
rocks = [] # List untuk menyimpan data batu
prev_hand_x, prev_hand_y = 0, 0
slash_threshold = 40 # Kecepatan piksel minimum untuk dianggap "menebas"

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    frame = cv2.flip(frame, 1) # Mirror effect
    h, w = frame.shape[:2]
    
    # 1. Konversi ke HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 2. Manual Skin Masking
    mask = manual_hsv_mask(hsv_frame, LOWER_SKIN, UPPER_SKIN)
    
    # 3. Manual Morphology (Opening: Erode lalu Dilate) untuk membersihkan noise
    mask_clean = manual_erode(mask)
    mask_clean = manual_dilate(mask_clean)
    
    # 4. Cari Posisi Tangan (Centroid)
    # Menggunakan numpy where untuk mencari koordinat piksel putih (nilai 255)
    y_coords, x_coords = np.where(mask_clean == 255)
    
    hand_x, hand_y = 0, 0
    is_slashing = False
    
    if len(x_coords) > 500: # Jika area tangan cukup besar
        hand_x = int(np.mean(x_coords))
        hand_y = int(np.mean(y_coords))
        
        # 5. Gesture Recognition (Menghitung kecepatan / jarak dari frame sebelumnya)
        distance = math.sqrt((hand_x - prev_hand_x)**2 + (hand_y - prev_hand_y)**2)
        if distance > slash_threshold:
            is_slashing = True # Gerakan terdeteksi sebagai tebasan
            
        prev_hand_x, prev_hand_y = hand_x, hand_y
        
        # 6. Menempelkan Pedang (Manual Alpha Blending)
        frame = manual_alpha_blend(frame, sword_img, hand_x, hand_y)

    # 7. Game Logic: Munculkan dan gerakkan batu
    # 2% peluang muncul batu baru di setiap frame
    if random.random() < 0.02: 
        rocks.append({'x': random.randint(100, w-100), 'y': -50, 'speed': random.randint(5, 12)})
        
    for rock in rocks[:]:
        rock['y'] += rock['speed'] # Batu jatuh
        
        # Menempelkan batu ke layar
        frame = manual_alpha_blend(frame, rock_img, rock['x'], rock['y'])
        
        # Collision Detection: Jika pedang mengenai batu DAN sedang melakukan tebasan
        if hand_x != 0 and hand_y != 0:
            dist_to_rock = math.sqrt((hand_x - rock['x'])**2 + (hand_y - rock['y'])**2)
            if dist_to_rock < 60: # Radius benturan
                if is_slashing:
                    score += 10
                    rocks.remove(rock) # Batu hancur
                    # Opsional: tambahkan efek visual skor di sini
                    continue
                
        # Hapus batu jika sudah melewati batas bawah layar
        if rock['y'] > h + 50:
            rocks.remove(rock)

    # 8. Tampilkan UI / Skor
    cv2.putText(frame, f'SCORE: {score}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
    if is_slashing:
        cv2.putText(frame, 'SLASH!', (w - 150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Tampilkan hasil
    cv2.imshow('Stone Slicer - Mask View', mask_clean) # Untuk debugging mask
    cv2.imshow('Stone Slicer', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()