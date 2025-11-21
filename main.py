"""
Monkey Pose Mimic - Ana uygulama
PyQt5 arayüz + MediaPipe pose detection
"""

import sys
import cv2
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont

try:
    from pose_detector import PoseDetector
    print("MediaPipe ile pose detection aktif!")
except ImportError:
    print("=" * 60)
    print("HATA: MediaPipe bulunamadi!")
    print("=" * 60)
    print(f"Python versiyonu: {sys.version}")
    print()
    print("MediaPipe sadece Python 3.12 ve altinda calisir.")
    print("Python 3.13 kullaniyorsaniz:")
    print()
    print("1. Python 3.12 yukleyin:")
    print("   https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe")
    print()
    print("2. Su komutla calistirin:")
    print("   py -3.12 main.py")
    print()
    print("VEYA:")
    print("   calistir.bat dosyasina cift tiklayin")
    print()
    print("=" * 60)
    sys.exit(1)


class MonkeyPoseApp(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Monkey Pose Mimic (MediaPipe)")
        self.setGeometry(100, 100, 1200, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                border: 2px solid #444;
                border-radius: 10px;
                background-color: #1e1e1e;
            }
        """)
        
        # Kamera başlat
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Pose detector
        self.pose_detector = PoseDetector()
        
        # Maymun resimleri
        self.monkey_images = self._load_monkey_images()
        self.current_pose = "default"
        
        # UI oluştur
        self._setup_ui()
        
        # Timer (40 FPS - daha akıcı)
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.timer.start(25)
    
    def _setup_ui(self):
        """Arayüz oluştur"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Sol - Kamera
        left_layout = QVBoxLayout()
        
        camera_title = QLabel("📷 Canlı Kamera")
        camera_title.setFont(QFont("Arial", 14, QFont.Bold))
        camera_title.setAlignment(Qt.AlignCenter)
        camera_title.setStyleSheet("QLabel { color: #fff; border: none; background: transparent; padding: 5px; }")
        camera_title.setMaximumHeight(40)
        
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setScaledContents(True)
        
        left_layout.addWidget(camera_title, 0)
        left_layout.addWidget(self.camera_label, 1)
        left_layout.setSpacing(5)
        
        # Sağ - Maymun
        right_layout = QVBoxLayout()
        
        monkey_title = QLabel("🐵 Maymun Pozu")
        monkey_title.setFont(QFont("Arial", 14, QFont.Bold))
        monkey_title.setAlignment(Qt.AlignCenter)
        monkey_title.setStyleSheet("QLabel { color: #fff; border: none; background: transparent; padding: 5px; }")
        monkey_title.setMaximumHeight(40)
        
        self.monkey_label = QLabel()
        self.monkey_label.setMinimumSize(480, 480)
        self.monkey_label.setAlignment(Qt.AlignCenter)
        self.monkey_label.setScaledContents(True)
        
        self.pose_name_label = QLabel("Normal Duruş")
        self.pose_name_label.setFont(QFont("Arial", 12))
        self.pose_name_label.setAlignment(Qt.AlignCenter)
        self.pose_name_label.setStyleSheet("QLabel { color: #4CAF50; border: none; background: transparent; padding: 5px; }")
        self.pose_name_label.setMaximumHeight(35)
        
        right_layout.addWidget(monkey_title, 0)
        right_layout.addWidget(self.monkey_label, 1)
        right_layout.addWidget(self.pose_name_label, 0)
        right_layout.setSpacing(5)
        
        main_layout.addLayout(left_layout, 60)
        main_layout.addLayout(right_layout, 40)
        
        self._update_monkey_image("default")
    
    def _load_monkey_images(self):
        """Maymun resimlerini yükle"""
        assets_dir = Path("assets")
        images = {}
        pose_files = {
            "raising_hand": "raising_hand_pose.jpg",
            "shocking": "shocking_pose.jpg",
            "thinking": "thinking_pose.jpg",
            "default": "default_pose.jpg"
        }
        
        for pose, filename in pose_files.items():
            image_path = assets_dir / filename
            if image_path.exists():
                images[pose] = str(image_path)
            else:
                print(f"Uyarı: {image_path} bulunamadı!")
                images[pose] = None
        
        return images
    
    def _update_frame(self):
        """Kamera frame güncelle"""
        ret, frame = self.camera.read()
        if not ret:
            return
        
        # Ayna efekti kaldır
        frame = cv2.flip(frame, 1)
        
        # Pose detection
        processed_frame, pose_name = self.pose_detector.detect_pose(frame)
        
        # Kamera göster - direkt pixmap, Qt otomatik ölçeklendirir
        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qt_image)
        self.camera_label.setPixmap(pixmap)
        
        # Poz değişti mi
        if pose_name != self.current_pose:
            self.current_pose = pose_name
            self._update_monkey_image(pose_name)
    
    def _update_monkey_image(self, pose_name):
        """Maymun resmini güncelle"""
        image_path = self.monkey_images.get(pose_name)
        
        if image_path:
            pixmap = QPixmap(image_path)
            self.monkey_label.setPixmap(pixmap)  # Qt otomatik ölçeklendirir
        else:
            self.monkey_label.setText(f"{pose_name}\n\n(Resim bulunamadı)")
            self.monkey_label.setStyleSheet("QLabel { color: #ff9800; font-size: 16px; border: 2px dashed #444; }")
        
        pose_names = {
            "raising_hand": "☝️ İşaret Parmağı Yukarıda",
            "shocking": "😲 Ağız Açık (Şaşkınlık)",
            "thinking": "🤔 El Yüzde (Düşünme)",
            "default": "😊 Normal Duruş"
        }
        self.pose_name_label.setText(pose_names.get(pose_name, pose_name))
    
    def closeEvent(self, event):
        """Kaynakları temizle"""
        self.timer.stop()
        self.camera.release()
        self.pose_detector.release()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MonkeyPoseApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
