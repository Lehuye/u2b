import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QLabel
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import yt_dlp
import shutil


# ✅ 新增：创建 temp 和 downloads 文件夹
temp_dir = os.path.join(os.getcwd(), "temp")
downloads_dir = os.path.join(os.getcwd(), "downloads")
os.makedirs(temp_dir, exist_ok=True)
os.makedirs(downloads_dir, exist_ok=True)


class DownloadWorker(QThread):
    progress = pyqtSignal(str, str)   # percent, speed
    finished = pyqtSignal(str)        # title

    def __init__(self, url, output_dir):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.temp_output_path = temp_dir  # ✅ 使用 temp 文件夹

    def run(self):
        ydl_opts = {
            'outtmpl': f'{self.temp_output_path}/%(title)s.%(ext)s',  # ✅ 保存到 temp
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
            info = d.get('info_dict', {})
            title = info.get('title', '完成')
            ext = info.get('ext', 'mp4')
            
            # ✅ 解决路径匹配问题 —— 实际文件路径来自 d['filename']
            src = d.get('filename')  # yt_dlp >= 2021 支持
            dst = os.path.join(downloads_dir, os.path.basename(src))

            try:
                if os.path.exists(src):
                    import shutil
                    shutil.move(src, dst)
            except Exception as e:
                title = f"{title}（移动失败：{e}）"

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
