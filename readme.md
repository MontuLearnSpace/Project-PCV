# Stone Slicer - Hand Weapon Mini Game

## Deskripsi Project
Stone Slicer adalah mini game berbasis pengolahan citra video yang dikembangkan menggunakan Python, OpenCV, dan NumPy tanpa menggunakan game engine maupun framework game lainnya.Pada permainan ini, pemain menggunakan tangan yang dideteksi oleh webcam untuk mengendalikan sebuah pedang virtual. Pedang mengikuti posisi tangan secara real-time dan dapat digunakan untuk menghancurkan batu yang jatuh dari bagian atas layar menuju bawah. Permainan menerapkan konsep Gesture Detection, Object Detection, Collision Detection, dan Score System sesuai dengan ketentuan tugas Pengolahan Citra Video.
---

# Teknologi yang Digunakan
## Bahasa Pemrograman
* Python 3.11.0
## Library
* OpenCV (cv2)
* NumPy
* Math
* Random
* Collections
---

# Cara Kerja Sistem
## 1. Akuisisi Video
Sistem mengambil frame video secara real-time menggunakan webcam laptop.
cap = cv2.VideoCapture(0)
Frame kemudian dibalik secara horizontal agar pergerakan tangan terasa lebih natural bagi pengguna.
---

## 2. Segmentasi Warna Kulit
Frame yang diperoleh dikonversi dari ruang warna BGR ke HSV.
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
Kemudian dilakukan proses thresholding menggunakan rentang warna kulit:
lower_skin = [0,20,70]
upper_skin = [20,255,255]
Hasil proses ini berupa citra biner (mask) yang memisahkan area kulit dari background.
---

## 3. Operasi Morfologi
Program menyediakan implementasi operasi morfologi secara manual menggunakan NumPy, yaitu:
### Erosion
Menghilangkan noise kecil pada citra biner.
### Dilation
Memperbesar area objek yang terdeteksi.
Seluruh operasi dilakukan tanpa menggunakan fungsi morphology OpenCV.
---

## 4. Deteksi Tangan
Program mencari contour terbesar dari hasil segmentasi warna kulit.
largest = max(contours, key=cv2.contourArea)
Jika area contour lebih besar dari batas minimum, maka contour dianggap sebagai tangan pengguna.
---

## 5. Penentuan Posisi Tangan
Posisi tangan ditentukan menggunakan centroid dari contour.
M = cv2.moments(largest)
Posisi centroid dihitung menggunakan:
cx = M["m10"] / M["m00"]
cy = M["m01"] / M["m00"]
Koordinat centroid digunakan sebagai titik kendali pedang.
---

## 6. Gesture Recognition
Gesture yang digunakan pada project ini adalah Swipe Gesture.
Program menyimpan beberapa posisi tangan terakhir menggunakan deque.
hand_positions = deque(maxlen=10)
Kecepatan gerakan tangan dihitung menggunakan jarak Euclidean.
speed = sqrt(dx² + dy²)
Jika nilai kecepatan melebihi threshold tertentu, maka sistem menganggap pemain melakukan serangan.
if swipe_speed > SWIPE_THRESHOLD:
    attack = True
---

## 7. Weapon Overlay
Pedang ditampilkan menggunakan teknik Alpha Blending manual.
Asset pedang berupa file PNG transparan yang ditempelkan pada frame video sesuai posisi tangan.
overlay_png()
Pedang akan mengikuti pergerakan tangan secara real-time.
---

## 8. Sistem Batu
Terdapat lima jenis batu yang digunakan sebagai obstacle yang ditaruh pada assets:
* Stone 1
* Stone 2
* Stone 3
* Stone 4
* Stone 5
Batu dipilih secara acak setiap kali muncul.
random.choice(stone_imgs)
Batu muncul dari bagian atas layar dan bergerak ke bawah dengan kecepatan tertentu.
---

## 9. Collision Detection
Program melakukan pengecekan tabrakan antara area pedang dan area batu menggunakan Bounding Box Collision Detection.
Jika:
* Pedang mengenai batu
* Gesture attack aktif
maka batu dianggap hancur.
if collision and attack:
---

## 10. Sistem Skor
Setiap batu yang berhasil dihancurkan akan menambah skor pemain.
score += 1
Nilai skor ditampilkan secara real-time pada layar permainan.
---

## 11. Combo System
Combo akan bertambah apabila pemain berhasil menghancurkan batu secara beruntun.
combo += 1
Combo akan kembali ke nol apabila batu berhasil lolos.
---

## 12. HP System
Pemain memiliki 3 HP.
hp = 3
Setiap batu yang berhasil mencapai bagian bawah layar akan mengurangi HP pemain.
hp -= 1
---

## 13. Level System
Level meningkat berdasarkan skor yang diperoleh.
level = (score // LEVEL_UP_SCORE) + 1
Semakin tinggi level:
* Batu bergerak lebih cepat
* Tingkat kesulitan meningkat
---

## 14. Game Over
Permainan berakhir ketika HP mencapai nol.
if hp <= 0:
    game_over = True
Layar Game Over akan ditampilkan beserta skor akhir pemain.
---

# Fitur Utama
* Real-Time Hand Tracking
* HSV Skin Color Segmentation
* Manual Morphological Operations
* Swipe Gesture Recognition
* Weapon Sprite Overlay
* Alpha Blending Manual
* Random Stone Generation
* Collision Detection
* Score System
* Combo System
* Level System
* HP System
* Game Over Screen

# Struktur Folder
```text
StoneSlicer/
│
├── main.py
│
├── assets/
│   ├── sword.png
│   ├── stone1.png
│   ├── stone2.png
│   ├── stone3.png
│   ├── stone4.png
│   └── stone5.png
```
# Cara Menjalankan
1. Install dependency:pip install opencv-python numpy
2. Jalankan program:  python main.py
3. Pastikan webcam aktif.
4. Gerakkan tangan di depan kamera.
5. Lakukan gerakan swipe untuk menghancurkan batu.
