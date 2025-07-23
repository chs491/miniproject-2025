import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, QTime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import rc

# 한글 폰트 설정
rc('font', family='NanumGothic')
plt.rcParams['axes.unicode_minus'] = False

class TimePlotApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("시간 플로팅 앱")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 시간 표시 라벨
        self.time_label = QLabel("현재 시각: --:--:--")
        self.layout.addWidget(self.time_label)

        # matplotlib 그래프 추가
        self.figure = plt.figure(figsize=(6, 3))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # 그래프 데이터 초기화
        self.times = []
        self.values = []

        # 시작 버튼
        self.start_button = QPushButton("시작")
        self.start_button.clicked.connect(self.start_plotting)
        self.layout.addWidget(self.start_button)

        # 타이머 설정
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

    def start_plotting(self):
        self.timer.start(1000)  # 1초 간격으로 갱신

    def update_plot(self):
        # 현재 시간 가져오기
        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.time_label.setText(f"현재 시각: {current_time}")

        # 더미 데이터 추가
        self.times.append(len(self.times))
        self.values.append(len(self.values) % 10)

        # 그래프 그리기
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(self.times, self.values, marker='o')
        ax.set_title("시간에 따른 값 변화")
        ax.set_xlabel("시간(초)")
        ax.set_ylabel("값")

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimePlotApp()
    window.show()
    sys.exit(app.exec_())
