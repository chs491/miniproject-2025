
import sys
import hashlib
import RPi.GPIO as GPIO
import mysql.connector
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import QDateTime

import board
import adafruit_dht

# ========== GPIO 초기화 ==========
GPIO.setmode(GPIO.BCM)
LED_PIN = 18
GPIO.setup(LED_PIN, GPIO.OUT)

# ========== 센서 설정 ==========
dhtDevice = adafruit_dht.DHT11(board.D4)

# ========== DB 설정 ==========
DB_CONFIG = {
    "host": "localhost",
    "user": "raspi",
    "password": "raspi",
    "database": "qt_db"
}

# ========== 암호화 유틸 ==========
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ========== 로그인 창 ==========
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("로그인")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디")
        layout.addWidget(self.id_input)

        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호")
        self.pw_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw_input)

        self.login_button = QPushButton("로그인")
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

        self.correct_id = "admin"
        self.correct_pw_hash = hash_password("1234")

        self.time_label = QLabel("현재 시간: --:--:--")
        layout.addWidget(self.time_label)

        self.log_count_label = QLabel("저장된 로그 수: 0")
        layout.addWidget(self.log_count_label)

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout.addWidget(self.canvas)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000)

        self.temp_data = []
        self.humid_data = []
        self.time_data = []

        # DB 연결
        try:
            self.db = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.db.cursor()
        except:
            self.cursor = None

    def update_time(self):
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.time_label.setText(f"현재 시간: {now}")
        self.update_log_count()

    def update_log_count(self):
        if not self.cursor:
            self.log_count_label.setText("로그 수: 오류")
            return
        try:
            self.cursor.execute("SELECT COUNT(*) FROM sensor_log")
            count = self.cursor.fetchone()[0]
            self.log_count_label.setText(f"저장된 로그 수: {count}")
        except:
            self.log_count_label.setText("로그 수: 오류")

    def update_graph(self):
        self.ax.clear()
        self.ax.plot(self.time_data, self.temp_data, label="온도(°C)", color="red")
        self.ax.plot(self.time_data, self.humid_data, label="습도(%)", color="blue")
        self.ax.set_xlabel("시간")
        self.ax.set_ylabel("측정값")
        self.ax.set_title("실시간 온습도 그래프")
        self.ax.legend()
        self.ax.tick_params(axis='x', rotation=45)
        self.canvas.draw()

    def check_login(self):
        user_id = self.id_input.text()
        password = self.pw_input.text()
        hashed_pw = hash_password(password)

        if user_id == self.correct_id and hashed_pw == self.correct_pw_hash:
            self.control_window = ControlWindow()
            self.control_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "오류", "아이디 또는 비밀번호가 잘못되었습니다.")

# ========== 센서 제어 창 ==========
class ControlWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("센서 제어창")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.led_button = QPushButton("LED ON")
        self.led_button.clicked.connect(self.toggle_led)
        layout.addWidget(self.led_button)

        self.sensor_label = QLabel("온도: --°C  습도: --%")
        layout.addWidget(self.sensor_label)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("센서 ON")
        self.start_button.clicked.connect(self.start_sensor)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("센서 OFF")
        self.stop_button.clicked.connect(self.stop_sensor)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.read_sensor_data)

        self.led_state = False

        self.temp_data = []
        self.humid_data = []
        self.time_data = []

        try:
            self.db = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.db.cursor()
            self.create_table_if_not_exists()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "DB 오류", f"DB 연결 실패:\n{e}")
            sys.exit(1)

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout.addWidget(self.canvas)

    def create_table_if_not_exists(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS sensor_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            temperature FLOAT,
            humidity FLOAT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(create_table_sql)
        self.db.commit()

    def toggle_led(self):
        self.led_state = not self.led_state
        GPIO.output(LED_PIN, self.led_state)
        self.led_button.setText("LED ON" if self.led_state else "LED OFF")

    def start_sensor(self):
        self.timer.start(2000)

    def stop_sensor(self):
        self.timer.stop()
        self.sensor_label.setText("온도: --°C  습도: --%")

    def read_sensor_data(self):
        try:
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            if humidity is not None and temperature is not None:
                self.sensor_label.setText(f"온도: {temperature:.1f}°C  습도: {humidity:.1f}%")
                self.insert_sensor_data(temperature, humidity)

                self.temp_data.append(temperature)
                self.humid_data.append(humidity)
                self.time_data.append(datetime.now().strftime("%H:%M:%S"))

                if len(self.temp_data) > 10:
                    self.temp_data.pop(0)
                    self.humid_data.pop(0)
                    self.time_data.pop(0)

                self.update_graph()
            else:
                self.sensor_label.setText("센서 오류")
        except Exception as e:
            self.sensor_label.setText("센서 오류")
            print("센서 오류:", e)

    def update_graph(self):
        self.ax.clear()
        self.ax.plot(self.time_data, self.temp_data, label="온도(°C)", color="red")
        self.ax.plot(self.time_data, self.humid_data, label="습도(%)", color="blue")
        self.ax.set_xlabel("시간")
        self.ax.set_ylabel("측정값")
        self.ax.set_title("실시간 온습도 그래프")
        self.ax.legend()
        self.ax.tick_params(axis='x', rotation=45)
        self.canvas.draw()

    def insert_sensor_data(self, temperature, humidity):
        try:
            sql = "INSERT INTO sensor_log (temperature, humidity) VALUES (%s, %s)"
            self.cursor.execute(sql, (temperature, humidity))
            self.db.commit()
        except Exception as e:
            print("DB 저장 오류:", e)

    def closeEvent(self, event):
        GPIO.cleanup()
        if self.db.is_connected():
            self.cursor.close()
            self.db.close()
        event.accept()

# ========== 메인 ==========
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
