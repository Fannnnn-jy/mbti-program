import sys, requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl


import os
VLC_PATH = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\VideoLAN"
os.environ['PATH'] = VLC_PATH + os.pathsep + os.environ['PATH']
import vlc


class NeteaseMusicDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("网易云音乐学习爬虫播放器")
        self.setFixedSize(500, 300)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("输入歌曲关键词")
        self.layout.addWidget(self.search_box)

        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.search_music)
        self.layout.addWidget(self.search_btn)

        self.result_combo = QComboBox()
        self.layout.addWidget(self.result_combo)

        self.play_btn = QPushButton("播放选中歌曲")
        self.play_btn.clicked.connect(self.play_selected)
        self.layout.addWidget(self.play_btn)

        self.status_label = QLabel("准备就绪")
        self.layout.addWidget(self.status_label)

        self.player = QMediaPlayer()
        self.song_map = {}  # {显示文本: 歌曲id}

    def search_music(self):
        keyword = self.search_box.text().strip()
        if not keyword:
            self.status_label.setText("请输入关键词")
            return

        self.status_label.setText("搜索中...")
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://music.163.com/"
        }
        url = "https://music.163.com/api/search/get"
        params = {
            "s": keyword,
            "type": 1,
            "limit": 10
        }

        resp = requests.get(url, params=params, headers=headers)
        data = resp.json()

        self.result_combo.clear()
        self.song_map.clear()

        try:
            songs = data["result"]["songs"]
            for song in songs:
                name = f'{song["name"]} - {song["artists"][0]["name"]}'
                song_id = song["id"]
                self.song_map[name] = song_id
                self.result_combo.addItem(name)
            self.status_label.setText("搜索完成")
        except:
            self.status_label.setText("搜索失败")

    def play_selected(self):
        selected = self.result_combo.currentText()
        song_id = self.song_map.get(selected)
        if not song_id:
            self.status_label.setText("请选择歌曲")
            return

        # 拼接网易云的中转播放链接（非官方，可能过期）
        song_url = f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"
        self.vlc_player = vlc.MediaPlayer()
        self.vlc_player.set_media(vlc.Media(song_url))
        self.vlc_player.play()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NeteaseMusicDemo()
    window.show()
    sys.exit(app.exec_())
