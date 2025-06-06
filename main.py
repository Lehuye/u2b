import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QLabel
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import yt_dlp


class DownloadWorker(QThread):
    progress = pyqtSignal(str, str)   # percent, speed
    finished = pyqtSignal(str)        # title

    def __init__(self, url, output_dir):
        super().__init__()
        self.url = url
        self.output_dir = output_dir

    def run(self):
        ydl_opts = {
            'outtmpl': f'{self.output_dir}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'progress_hooks': [self.progress_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([self.url])
            except Exception as e:
                self.finished.emit(f"错误：{e}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '').strip()
            self.progress.emit(percent, speed)
        elif d['status'] == 'finished':
            title = d.get('info_dict', {}).get('title', '完成')
            self.finished.emit(title)


class DownloaderUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube 视频下载器")
        self.setMinimumWidth(500)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入 YouTube 视频链接...")

        self.download_btn = QPushButton("确定")
        self.download_btn.clicked.connect(self.start_download)

        self.downloading_list = QListWidget()
        self.completed_list = QListWidget()

        layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.download_btn)

        layout.addLayout(input_layout)
        layout.addWidget(QLabel("下载中："))
        layout.addWidget(self.downloading_list)
        layout.addWidget(QLabel("下载完成："))
        layout.addWidget(self.completed_list)
        self.setLayout(layout)

        self.current_item = None

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            return

        self.current_item = QListWidgetItem(f"开始下载：{url}")
        self.downloading_list.addItem(self.current_item)

        self.worker = DownloadWorker(url, output_dir=os.getcwd())
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.finish_download)
        self.worker.start()

    def update_progress(self, percent, speed):
        if self.current_item:
            self.current_item.setText(f"下载中：{percent} @ {speed}")

    def finish_download(self, title):
        if self.current_item:
            self.downloading_list.takeItem(self.downloading_list.row(self.current_item))
            self.completed_list.addItem(f"完成：{title}")
            self.current_item = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DownloaderUI()
    window.show()
    sys.exit(app.exec_())
