Project Game Mata Kuliah Pengolahan CItra Video

Rizki Farhan Nabil
5024221046

Tema Project: Handweapon Mini Game (misalnya: Game Fruit Ninja menggunakan deteksi tangan sebagai pedang/katana dengan interaksi gerakan cepat/slash).

Di dalam mini game yang dikembangkan harus terdapat unsur: Gesture Detection, Second Object, Scoring.

Mini game dikembangkan hanya menggunakan python dan library opencv saja, dilarang menggunakan framework atau engine game yang sudah ada.

Konfigurasikan perangkat keras fisik (kamera/webcam laptop) agar terhubung dan frame videonya dapat dibaca menggunakan library OpenCV (Gunakan fungsi I/O dasar seperti cv2.VideoCapture, cv2.imshow, dan cv2.imread).

Terapkan teknik segmentasi berbasis warna (skin color masking) menggunakan ruang warna HSV untuk mendeteksi area tangan secara real-time, di mana seluruh manipulasi piksel wajib diimplementasikan dari awal menggunakan fungsi array pada library NumPy.

Terapkan operasi morfologi citra (seperti Opening dan Closing secara manual dengan NumPy) ke dalam pipeline untuk memproses, menganalisis, dan membersihkan noise atau lubang dari data mentah mask citra biner hasil deteksi tangan.

Integrasikan visual senjata (weapon sprite overlay) ke dalam pipeline real-time dengan menempelkannya tepat di posisi tangan yang terdeteksi menggunakan metode alpha blending manual.

Kembangkan fitur game interaktif yang responsif dengan menambahkan pengenalan gerakan (gesture recognition) minimal 1 jenis, dilengkapi dengan kalkulasi sistem skor (score system).

Publikasikan seluruh dokumentasi teknis dan kode sumber proyek ke dalam repositori GitHub.

Lengkapi repositori dengan file README.md (sebagai laporan dan pedoman teknis), direktori kode sumber game utama, tangkapan layar game, serta tautan video demonstrasi.

Demokan progres pada pertemuan ke-7 (M7) dan Final demo pada pertemuan ke-15 (M15)
