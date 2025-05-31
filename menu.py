from PyQt5.QtWidgets import (QApplication, QComboBox, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
                            QHBoxLayout, QLabel, QPushButton, QMessageBox, QFrame, QRadioButton, 
                            QButtonGroup, QScrollArea, QStackedWidget, QTextEdit, QLineEdit, QSlider, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QTimer, QDateTime
from PyQt5.QtGui import QFont, QPixmap, QTransform, QPainter, QBitmap, QImage, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os
from PIL import Image
CURRENT_TYPE = None

from openai import OpenAI
client = OpenAI(api_key="sk-42d27f7d36474c108d648985219ab3c0", base_url="https://api.deepseek.com")

# 从 MBTI_data.py 中导入题库
from MBTI_data import MBTI_Choices, MBTI_Questions, MBTI_Descriptions, WHOLE_SCORING_RULES
from MBTI_data_easy import MBTI_Choices as MBTI_Choices_easy, MBTI_Questions as MBTI_Questions_easy, MBTI_Descriptions as MBTI_Descriptions_easy, EASY_SCORING_RULES


# 从 MBTI_data.py 中导入题库（假设MBTI_Choices是选项列表，MBTI_Questions是问题描述列表）
# 生成带计分规则的问题列表
WHOLE_MBTI_QUESTIONS = []
for j in range(1, len(MBTI_Questions)+1):  # j从1开始对应问题编号
    question = {
        "question": MBTI_Questions[j-1],  # 问题描述（j-1是因为列表索引从0开始）
        "options": MBTI_Choices[j-1],     # 选项列表
        "scoring": {                      # 计分规则
            'A': WHOLE_SCORING_RULES.get((j, 'A'), ('', 0)),  # 默认无维度、0分
            'B': WHOLE_SCORING_RULES.get((j, 'B'), ('', 0))
        }
    }
    WHOLE_MBTI_QUESTIONS.append(question)
    
EASY_MBTI_QUESTIONS = []
for j in range(1, len(MBTI_Questions_easy)+1):  # j从1开始对应问题编号
    question = {
        "question": MBTI_Questions_easy[j-1],  # 问题描述（j-1是因为列表索引从0开始）
        "options": MBTI_Choices_easy[j-1],     # 选项列表
        "scoring": {                      # 计分规则
            'A': EASY_SCORING_RULES.get((j, 'A'), ('', 0)),  # 默认无维度、0分
            'B': EASY_SCORING_RULES.get((j, 'B'), ('', 0))
        }
    }
    EASY_MBTI_QUESTIONS.append(question)
    
    
class MBTITestPage(QWidget):
    test_completed = pyqtSignal(str)  # 测试完成信号，传递MBTI类型

    def __init__(self, questions):
        super().__init__()
        
        self.current_question = 0
        self.answers = []
        self.scores = {
            "E": 0, "I": 0,
            "S": 0, "N": 0,
            "T": 0, "F": 0,
            "J": 0, "P": 0
        }
        self.MBTI_QUESTIONS = questions
        self.init_ui()        

    def init_ui(self):
        self.setLayout(QVBoxLayout())

        # 顶部进度条
        self.progress_label = QLabel(f"问题 1/{len(self.MBTI_QUESTIONS)}")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("font-size: 18px; color: #555;")
        self.layout().addWidget(self.progress_label)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.layout().addWidget(scroll)

        # 问题容器
        container = QWidget()
        scroll.setWidget(container)
        container.setLayout(QVBoxLayout())
        container.layout().setContentsMargins(30, 20, 30, 20)

        # 问题标签
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("font-size: 20px; margin-bottom: 20px;")
        container.layout().addWidget(self.question_label)

        # 选项按钮组
        self.button_group = QButtonGroup()
        self.option_buttons = []

        for i in range(2):  # 每个问题2个选项
            rb = QRadioButton()
            rb.setStyleSheet("font-size: 18px; margin-bottom: 10px;")
            container.layout().addWidget(rb)
            self.option_buttons.append(rb)
            self.button_group.addButton(rb, i)

        # 底部按钮
        btn_container = QWidget()
        btn_container.setLayout(QHBoxLayout())
        self.layout().addWidget(btn_container)

        self.prev_btn = QPushButton("上一题")
        self.prev_btn.setStyleSheet("background-color: #95a5a6; color: white;")
        self.prev_btn.clicked.connect(self.prev_question)
        btn_container.layout().addWidget(self.prev_btn)

        self.next_btn = QPushButton("下一题")
        self.next_btn.setStyleSheet("background-color: #3498db; color: white;")
        self.next_btn.clicked.connect(self.next_question)
        btn_container.layout().addWidget(self.next_btn)
        
        # 新增退出按钮
        self.exit_btn = QPushButton("退出测试")
        self.exit_btn.setStyleSheet("background-color: #e74c3c; color: white; margin-left: 10px;")
        self.exit_btn.clicked.connect(self.exit_test)
        btn_container.layout().addWidget(self.exit_btn)

        # 加载第一个问题
        self.load_question(0)
    def load_question(self, index):
        self.current_question = index
        question_data = self.MBTI_QUESTIONS[index]

        self.question_label.setText(f"问题 {index + 1}: {question_data['question']}")
        
        # 重置选项按钮
        self.button_group.setExclusive(False)
        for btn in self.option_buttons:
            btn.setChecked(False)
        self.button_group.setExclusive(True)

        self.button_group.setExclusive(False)
        for i, option in enumerate(question_data['options']):
            self.option_buttons[i].setText(option)
        self.button_group.setExclusive(True)

        # 自动选中已保存的答案（关键新增）
        if index < len(self.answers):
            saved_answer = self.answers[index]
            if saved_answer == 'A':
                self.option_buttons[0].setChecked(True)
            else:
                self.option_buttons[1].setChecked(True)

        self.progress_label.setText(f"问题 {index + 1}/{len(self.MBTI_QUESTIONS)}")
        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setText("完成测试" if index == len(self.MBTI_QUESTIONS) - 1 else "下一题")

    def prev_question(self):
        if self.current_question > 0:
            self.load_question(self.current_question - 1)

    def next_question(self):
        selected = self.button_group.checkedId()
        if selected == -1:
            QMessageBox.warning(self, "提示", "请选择一个选项")
            return

        answer = 'A' if selected == 0 else 'B'  # 选项转A/B
        # 记录答案（已实现）
        if len(self.answers) > self.current_question:
            self.answers[self.current_question] = answer
        else:
            self.answers.append(answer)

        # 更新计分（关键逻辑）
        dimension, score = self.MBTI_QUESTIONS[self.current_question]["scoring"][answer]
        if dimension:
            self.scores[dimension] += score  # 累加对应维度分数

        # 跳转下一题或完成测试（已实现）
        if self.current_question == len(self.MBTI_QUESTIONS) - 1:
            self.complete_test()
        else:
            self.load_question(self.current_question + 1)

    # 新增: 退出测试方法
    def exit_test(self):
        """处理退出测试逻辑"""
        reply = QMessageBox.question(self, '确认退出', '当前测试进度无法保留\n\n是否要退出当前测试？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 返回主页面
            self.parent().setCurrentWidget(self.parent().widget(0))


    def complete_test(self):
        # 确定MBTI类型
        mbti_type = ""
        if self.scores["E"] > self.scores["I"]:
            mbti_type += "E"
        else:
            mbti_type += "I"

        if self.scores["S"] > self.scores["N"]:
            mbti_type += "S"
        else:
            mbti_type += "N"

        if self.scores["T"] > self.scores["F"]:
            mbti_type += "T"
        else:
            mbti_type += "F"

        if self.scores["J"] > self.scores["P"]:
            mbti_type += "J"
        else:
            mbti_type += "P"

        # 存储当前类型
        global CURRENT_TYPE
        CURRENT_TYPE = mbti_type
        save_path = os.path.join(os.getcwd(), "user_mbti.txt")  # 应用根目录下的user_mbti.txt
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(mbti_type)  # 直接写入类型字符串（如"ENFP"）    
        self.test_completed.emit(mbti_type)

import sys
import os
import glob
import vlc
from downloader import GeQuHaiPlayer
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QHBoxLayout, QSlider
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

class RelaxingPage(QWidget):
    back_to_home = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        # VLC 初始化
        self.vlc_instance = vlc.Instance('--quiet', '--no-video')
        self.player = self.vlc_instance.media_player_new()

        self.playlist = []
        self.current_index = 0

        audio_patterns = ('*.mp3', '*.aac')

        self.music_folder = 'asset/music'
        audio_files = []
        for pat in audio_patterns:
            audio_files.extend(glob.glob(os.path.join(self.music_folder, pat)))
        if audio_files:
            for path in audio_files:
                title = os.path.splitext(os.path.basename(path))[0]
                self.playlist.append({"title": title, "file": path})
        else:
            print("未找到音频文件！")

        # 标题
        title = QLabel("🎵 放松一下")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        self.layout().addWidget(title)


        # 左右分栏演示
        content_row = QHBoxLayout()
        content_row.setSpacing(20)

        content_row.setContentsMargins(150, 0, 0, 0)

        # 左侧：图片演示
        self.pic_size = 300
        self.pic_label = QLabel()
        default_pix = QPixmap("asset/music/demo.png").scaled(self.pic_size, self.pic_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        # 圆形 mask
        mask = QBitmap(self.pic_size, self.pic_size)
        mask.fill(Qt.color0)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.color1)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self.pic_size, self.pic_size)
        painter.end()
        default_pix.setMask(mask)
        
        self.default_pixmap = default_pix
        self.orig_pixmap = default_pix 

        # 把 QLabel 加到布局里
        content_row.addWidget(self.pic_label)
        self.pic_label.setPixmap(self.orig_pixmap)

        # pic = QPixmap("asset/icons/checkmark.png")
        # size = 300
        # pic_label.setPixmap(
        #     pic.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        # )
        # content_row.addWidget(pic_label)

        # 右侧：选曲 + 刷新 + 播放标签
        right_box = QVBoxLayout()
        right_box.setSpacing(0)

        right_box.addSpacing(100)

        # 下拉框+刷新按钮行
        h = QHBoxLayout()
        self.combo = QComboBox()
        self.combo.setFixedWidth(300)
        self.combo.currentIndexChanged.connect(self.select_track)
        h.addWidget(self.combo)

        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedSize(30, 30)
        self.refresh_btn.setStyleSheet(
            "font-size:12px;"
            "background-color:#2ecc71;"
            "color:white;"
            "border-radius:4px;"
        )
        self.refresh_btn.clicked.connect(self.refresh_playlist)
        h.addWidget(self.refresh_btn)

        right_box.addLayout(h)

        # 歌曲名称
        self.track_label = QLabel()
        self.track_label.setAlignment(Qt.AlignCenter)
        self.track_label.setStyleSheet("font-size: 16px;")
        right_box.addWidget(self.track_label)

        content_row.addLayout(right_box)
        self.layout().addLayout(content_row)

        # 进度条
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        # self.layout().addWidget(self.slider)

        # 时间
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 14px; margin-left: 8px;")

        h_slider = QHBoxLayout()
        h_slider.addStretch(1)
        h_slider.addWidget(self.slider, 8)
        h_slider.addWidget(self.time_label, 2)
        self.layout().addLayout(h_slider)



        btn_row = QHBoxLayout()

        self.back_btn = QPushButton("🔙 返回主页")
        self.back_btn.setFixedHeight(40)
        self.back_btn.setStyleSheet("font-size: 14px; background-color: #95a5a6; color: white; border-radius: 6px;")
        btn_row.addWidget(self.back_btn, alignment=Qt.AlignCenter)

        # 播放控制按钮
        self.prev_btn = QPushButton("⏮️")
        self.play_btn = QPushButton("▶️")
        self.next_btn = QPushButton("⏭️")
        for btn in [self.prev_btn, self.play_btn, self.next_btn]:
            btn.setFixedSize(80, 80)
            btn.setStyleSheet("font-size: 18px; background-color: #3498db; color: white; border-radius: 6px;")
            btn_row.addWidget(btn, alignment=Qt.AlignCenter)


        self.search_btn = QPushButton("🔍 搜一搜")
        self.search_btn.setFixedHeight(40)
        self.search_btn.setStyleSheet("font-size: 14px; background-color: #2ecc71; color: white; border-radius: 6px;")
        self.search_btn.clicked.connect(self.open_search_window)
        btn_row.addWidget(self.search_btn, alignment=Qt.AlignCenter)

        self.layout().addLayout(btn_row)

    

        # 连接事件
        self.back_btn.clicked.connect(lambda: self.back_to_home.emit())
        self.prev_btn.clicked.connect(self.play_previous)
        self.play_btn.clicked.connect(self.toggle_play)
        self.next_btn.clicked.connect(self.play_next)
        self.slider.sliderMoved.connect(self.seek_position)

        # 定时器更新进度
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_position)
        self.timer.start()

        self.refresh_playlist()
        # 加载第一首
        if self.playlist:
            self.load_track(0)
        else:
            self.track_label.setText("❌ 没有找到可播放的文件")

    

    
    def open_search_window(self):
        self.search_window = GeQuHaiPlayer()
        self.search_window.setWindowTitle("歌曲海下载器")
        self.search_window.resize(500, 400)
        self.search_window.setWindowIcon(QIcon("asset/icons/gequhai.png"))
        self.search_window.show()

    def refresh_playlist(self):
        """手动扫描目录，更新 self.playlist 和下拉框"""
        audio_patterns = ('*.mp3', '*.aac')
        files = []
        for pat in audio_patterns:
            files += glob.glob(os.path.join(self.music_folder, pat))

        self.player.pause()
        self.play_btn.setText("▶️")

        self.combo.blockSignals(True)
        self.playlist.clear()
        self.combo.clear()

        for path in files:
            title = os.path.splitext(os.path.basename(path))[0]
            self.playlist.append({'title': title, 'file': path})
            self.combo.addItem(title)

        self.combo.blockSignals(False)
        if self.playlist:
            self.current_index = 0
            self.combo.setCurrentIndex(0)
            self.load_track(0)
        else:
            self.track_label.setText("❌ 没有找到可播放的文件")

        
    def format_time(self, ms):
        s = ms // 1000
        return f"{s // 60:02}:{s % 60:02}"

    def load_track(self, index):
        track = self.playlist[index]
        self.track_label.setText(f"当前播放：{track['title']}")
        
        jpg_path = os.path.join(self.music_folder, f"{track['title']}.jpg")
        jpg_path = os.path.normpath(jpg_path)
        abs_path = jpg_path.replace("\\", "/")

        if os.path.exists(jpg_path):
            img = Image.open(abs_path).convert("RGBA")
            w, h = img.size
            data = img.tobytes("raw", "RGBA")

            
            qimg = QImage(data, w, h, QImage.Format_RGBA8888)
            pix  = QPixmap.fromImage(qimg)
            
            mask = QBitmap(self.pic_size, self.pic_size)
            mask.fill(Qt.color0)
            painter = QPainter(mask)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(Qt.color1)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, self.pic_size, self.pic_size)
            painter.end()

            pix = pix.scaled(self.pic_size, self.pic_size,Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            pix.setMask(mask)

            self.orig_pixmap = pix
            
        else:
            self.orig_pixmap = self.default_pixmap
        self.pic_label.setPixmap(self.orig_pixmap)

        path = os.path.abspath(track["file"])
        if os.path.exists(path):
            self.player.stop()
            media = self.vlc_instance.media_new(path, 'file-caching=300')
            self.player.set_media(media)
            # self.player.play()
            # self.play_btn.setText("⏸️")
        else:
            self.track_label.setText(f"❌ 文件不存在: {track['file']}")

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_btn.setText("▶️")
        else:
            self.player.play()
            self.play_btn.setText("⏸️")

    def play_next(self):
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.combo.setCurrentIndex(self.current_index)
        self.player.play()
        self.play_btn.setText("⏸️")

    def play_previous(self):
        self.current_index = (self.current_index - 1 + len(self.playlist)) % len(self.playlist)
        self.combo.setCurrentIndex(self.current_index)
        self.player.play()
        self.play_btn.setText("⏸️")

    def select_track(self, index):
        self.current_index = index
        if 0 <= index < len(self.playlist):
            self.load_track(index)
            self.player.pause()
            self.play_btn.setText("▶️")

    def update_position(self):
        state = self.player.get_state()
        if self.player.is_playing():
            pos = self.player.get_time()
            total = self.player.get_length()
            if total > 0:
                progress = int(pos / total * 1000)
                self.slider.setValue(progress)
                self.time_label.setText(f"{self.format_time(pos)} / {self.format_time(total)}")

                angle = ((pos % 120000) / 120000) * 360
                transform = QTransform()
                transform.translate(self.pic_size/2, self.pic_size/2)
                transform.rotate(angle)
                transform.translate(-self.pic_size/2, -self.pic_size/2)
                rotated_full = self.orig_pixmap.transformed(transform, Qt.SmoothTransformation)

                w, h = rotated_full.width(), rotated_full.height()
                x = (w - self.pic_size) // 2
                y = (h - self.pic_size) // 2
                cropped = rotated_full.copy(x, y, self.pic_size, self.pic_size)

                self.pic_label.setPixmap(cropped)
        if state == vlc.State.Ended:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.combo.setCurrentIndex(self.current_index)
            self.load_track(self.current_index)
            self.slider.setValue(0)
            self.time_label.setText("00:00 / 00:00")
            self.player.play()
            
            self.play_btn.setText("⏸️")

    def seek_position(self, value):
        total = self.player.get_length()    
        if total > 0:
            target = int(total * value / 1000)
            self.player.set_time(target)
        if total == value:
            self.player.stop()
            self.play_btn.setText("▶️")



class DoubaoChatWidget(QWidget):
    back_to_main = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 标题栏
        title_layout = QHBoxLayout()
        title_label = QLabel("智能心理咨询")

        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))

        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 15px;
                background-color: #e74c3c;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_btn.clicked.connect(self.return_to_main)

        title_layout.addStretch()
        title_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)  # 标题居中
        title_layout.addStretch()  # 伸缩空间（让标题真正居中）
        title_layout.addWidget(close_btn)

        layout.addLayout(title_layout)


        # 滚动区域（聊天内容 + 提示按钮）
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        # 聊天内容容器
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        # 初始问候
        self.show_message("小鲸鱼", "你好！我是智能心理咨询助手小鲸鱼，有什么可以帮助你的吗？")
        
        # 初始提示按钮（嵌入聊天区）
        self.add_hint_buttons()
        
        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area)

        # 输入区域
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("输入问题，按回车发送...")
        self.message_input.setMinimumHeight(50)
        self.message_input.setStyleSheet("""
            border: 1px solid #ddd;
            border-radius: 25px;
            padding: 8px 15px;
            font-size: 20px;
        """)
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        self.send_btn = QPushButton("↑")  # 使用更标准的箭头符号
        self.send_btn.setFixedSize(50, 50)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #07c160;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 24px;
                font-weight: 900;
                padding-bottom: 12px;
            }
            QPushButton:hover {
                background-color: #05a14e;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)


        

    def add_hint_buttons(self):
        hints = [
            "我最近情绪低落，该如何调整？→",
            "工作压力大，有什么缓解方法？→",
            "如何改善人际关系？→",
        ]
        for hint in hints:
            btn = QPushButton(hint)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(60)  # 仅固定高度，宽度自适应
            btn.setStyleSheet("""
                QPushButton {
                    margin: 1px 15px;
                    padding: 1px 15px;
                    border: 1px solid #eee;
                    border-radius: 12px;
                    background-color: #f9f9f9;
                    color: #333;
                    font-size: 20px;
                    text-align: left;
                    
                }
                QPushButton:hover {
                    border: 5px solid #eee;
                }
            """)
            btn.clicked.connect(lambda _, q=hint: self.send_hint(q[:-1]))
            self.chat_layout.addWidget(btn)

    def send_hint(self, question):
        self.message_input.setText(question)
        self.send_message()  # 复用发送逻辑

    def show_message(self, sender, message):
        timestamp = QDateTime.currentDateTime().toString("hh:mm")
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                margin: 15px 8px;
                padding: 24px 30px;
                border-radius: 12px;
            }
        """)
        frame.setProperty("sender", sender)
        if sender == "你":
            frame.setObjectName("user_message")
            frame.setStyleSheet("QFrame { background-color: #e3f2fd; }")
        else:
            frame.setObjectName("ai_message")
            frame.setStyleSheet("QFrame { background-color: #f5f5f5; }")

        # 发送者和时间戳
        sender_label = QLabel(f"{sender}")
        sender_label.setStyleSheet("font-size: 18px; color: #333; font-weight: bold;")
        time_label = QLabel(f"{timestamp}")
        time_label.setStyleSheet("font-size: 14px; color: #999;")
        # 消息内容
        content_label = QLabel(message)
        content_label.setStyleSheet("font-size: 20px; color: #333;")
        content_label.setWordWrap(True)
        content_label.setMaximumWidth(900)

        # 只设置一次布局
        frame_layout = QVBoxLayout(frame)
        top_row = QHBoxLayout()
        top_row.addWidget(sender_label)
        top_row.addWidget(time_label)
        top_row.addStretch()
        frame_layout.addLayout(top_row)
        frame_layout.addWidget(content_label)

        # 添加到聊天区
        self.chat_layout.addWidget(frame)

        # 滚动到最新消息
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            self.show_message("你", message)
            self.message_input.clear()
            # 显示"正在思考"
            self.show_message("小鲸鱼", "正在思考...")

            # 模拟AI回复（替换为真实API调用）
            QTimer.singleShot(1000, lambda: self.get_doubao_response(message))

    def return_to_main(self):
        """发送返回主页面信号"""
        self.back_to_main.emit()

    def get_doubao_response(self, message):
        """模拟从豆包API获取回复"""
        message += "。如果我的问题与心理有关，那么请以心理咨询师的身份与口吻解答我的问题，150字以内；如果我的问题与心理无关，则回答后将话题引向心理问题，关注隐含心理问题，150字以内"
        # 这里应该替换为真实的API调用
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": message},
            ],
            stream=False
        )
        reply_content = response.choices[0].message.content
        self.show_message("小鲸鱼", reply_content)  # 只显示内容部分

# 以下是我关于mzr部分的尝试：class QuestionPopup(QWidget):
class QuestionPopup(QWidget):
    """常见问题选择弹窗"""
    back_to_main = pyqtSignal()  # 返回主界面信号
    goto_chat = pyqtSignal(str)   # 跳转对话信号（参数为预填问题）

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("常见问题")
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: white; border-radius: 15px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 顶部关闭栏
        # top_layout = QHBoxLayout()
        # close_btn = QPushButton("返回")
        # close_btn.setFixedSize(80, 35)
        # close_btn.setStyleSheet("""
        #     QPushButton {
        #         border: none;
        #         border-radius: 15px;
        #         background-color: #e74c3c;
        #         color: white;
        #         font-size: 15px;
        #     }
        #     QPushButton:hover { background-color: #c0392b; }
        # """)
        # close_btn.clicked.connect(self.back_to_main.emit)
        # top_layout.addStretch()
        # top_layout.addWidget(close_btn)
        # layout.addLayout(top_layout)

        # 常见问题标题
        title = QLabel("常见问题")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 问题按钮容器（使用流式布局）
        question_layout = QGridLayout()
        question_layout.setSpacing(20)
        # 添加水平拉伸确保有足够空间显示按钮
        question_layout.setContentsMargins(30, 10, 30, 10)  # 增加左右边距
        # 增加容器最大宽度限制（根据窗口大小调整）
        question_container = QWidget()
        question_container.setMaximumWidth(540)  # 600窗口宽度 - 左右边距各30
        question_container.setLayout(question_layout)
        layout.addWidget(question_container, alignment=Qt.AlignCenter)  # 居中显示 
               
        common_questions = [
            "我的MBTI测试结果如何解读？", 
            "最近压力很大该怎么缓解？", 
            "如何改善睡眠质量？", 
            "社交焦虑该怎么办？"
        ]

        # 创建圆形问题按钮
        for idx, question in enumerate(common_questions):
            btn = QPushButton(question)
            btn.setFixedSize(230, 40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid #3498db;  /* 蓝色边框 */
                    background-color: #f0f8ff;  /* 浅蓝背景 */
                    font-size: 14px;
                    color: #2c3e50;  /* 深灰文字（与背景对比明显） */
                }}
                QPushButton:hover {{ 
                    background-color: #e3f2fd;  /* 更浅的悬停背景 */
                    border-color: #2980b9;  /* 深一点的边框 */
                }}
            """)
            if idx == 0:
                with open("user_mbti.txt", "r", encoding="utf-8") as f:
                    mbti_str = f.read().strip()  # 读取并去除首尾空白
                question += f"（我的MBTI类型是：{mbti_str}）"
            btn.clicked.connect(lambda _, q=question: (self.goto_chat.emit(q), self.close()))
            question_layout.addWidget(btn, idx // 2, idx % 2)  # 每行2个

        # 直接对话按钮
        direct_btn = QPushButton("直接开始对话")
        direct_btn.setFixedSize(200, 40)
        direct_btn.setStyleSheet("""
            QPushButton {
                background-color: #07c160;  /* 绿色背景 */
                color: white;  /* 白色文字（高对比度） */
                border: none;
                font-size: 16px;
                font-weight: 500;  /* 文字加粗更清晰 */
            }
            QPushButton:hover { 
                background-color: #05a14e;  /* 深绿悬停 */
            }
        """)
        direct_btn.clicked.connect(lambda: (self.goto_chat.emit(""), self.close()))
        layout.addWidget(direct_btn, alignment=Qt.AlignCenter)

class MentalHealthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("心理健康助手")
        self.setFixedSize(1000, 600)
        self.setWindowIcon(QIcon("asset/icons/main_icon.png"))
        self.current_mbti_type = None  # 初始化MBTI类型存储属性（新增）
        self.load_saved_mbti()  # 加载历史结果（新增）
        # 新增选择题库：
        self.start_test_btn = QPushButton("开始人格测试")
        self.start_test_btn.clicked.connect(self.show_test_selection)  # 连接新的选择弹窗    
        
        
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # 创建豆包对话窗口
        self.doubao_chat = DoubaoChatWidget()
        self.doubao_chat.back_to_main.connect(lambda: self.stack.setCurrentWidget(self.main_page))  
        
        # 主窗口部件
        self.main_page = self.create_main_page()
        self.stack.addWidget(self.main_page)

        # 以下移除：
        '''
        self.mbti_test_page = MBTITestPage()
        self.mbti_test_page.test_completed.connect(self.show_mbti_result)
        self.stack.addWidget(self.mbti_test_page)
        '''
        self.mbti_result_page = None  # 结果页面保持为None，动态创建
        
        
        
        self.relaxing_page = RelaxingPage()
        self.relaxing_page.back_to_home.connect(lambda: self.stack.setCurrentWidget(self.main_page))
        self.stack.addWidget(self.relaxing_page)
        
        # 添加豆包对话窗口
        self.stack.addWidget(self.doubao_chat)

        # mbti结果页面
        self.mbti_result_page = None

    def load_saved_mbti(self):
        """加载本地存储的MBTI类型"""
        save_path = os.path.join(os.getcwd(), "user_mbti.txt")
        if os.path.exists(save_path):
            try:
                with open(save_path, "r", encoding="utf-8") as f:
                    self.current_mbti_type = f.read().strip()  # 读取并去除首尾空格
            except FileNotFoundError:
                self.current_mbti_type = None  # 文件不存在则保持为None

    # 为了实现首页图片的动态更新：
    def update_main_image(self):
        """更新主页面的MBTI人格图片"""
        # 读取本地存储的MBTI类型
        save_path = os.path.join(os.getcwd(), "user_mbti.txt")
        if os.path.exists(save_path):
            with open(save_path, "r", encoding="utf-8") as f:
                self.current_mbti_type = f.read().strip()
        else:
            self.current_mbti_type = None

        # 更新图片显示
        if self.current_mbti_type:
            pixmap_path = f"asset/mbti-icons/demo_{self.current_mbti_type}.png"
        else:
            pixmap_path = "asset/mbti-icons/16-personalities.png"  # 默认图片

        pixmap = QPixmap(pixmap_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(480, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.main_image_label.setPixmap(pixmap)
        else:
            self.main_image_label.setText("图片加载失败")
            self.main_image_label.setStyleSheet("color: red; font-size: 14px;")
            
     # 新增选择弹窗：       
    def show_test_selection(self):
        # 创建自定义弹窗
        msg = QMessageBox()
        msg.setWindowIcon(QIcon("asset/icons/selection.png"))
        msg.setWindowTitle("选择测试类型")
        msg.setText("请选择测试类型：")
        msg.setInformativeText("完整版：93题，约18分钟（更准确）\n精简版：28题，约5分钟（较快速）")
        
        # 添加按钮（QMessageBox.CustomButton保证顺序）
        full_btn = msg.addButton("完整版", QMessageBox.AcceptRole)
        easy_btn = msg.addButton("精简版", QMessageBox.AcceptRole)
        cancel_btn = msg.addButton("取消", QMessageBox.RejectRole)
        
        # 显示弹窗并获取用户选择
        msg.exec_()
        clicked_btn = msg.clickedButton()
        
        if clicked_btn == full_btn:
            # 动态创建完整版测试页面并传递题库
            self.mbti_test_page = MBTITestPage(WHOLE_MBTI_QUESTIONS)
        elif clicked_btn == easy_btn:
            # 动态创建精简版测试页面并传递题库
            self.mbti_test_page = MBTITestPage(EASY_MBTI_QUESTIONS)
        else:
            return  # 取消则不创建

        # 连接信号并显示测试页面
        self.mbti_test_page.test_completed.connect(self.show_mbti_result)
        self.stack.addWidget(self.mbti_test_page)
        self.stack.setCurrentWidget(self.mbti_test_page)
        
    def start_test(self, questions):
        # 实例化测试页面并传递对应题库
        self.test_page = MBTITestPage(questions)  # 需修改MBTITestPage构造函数
        self.setCentralWidget(self.test_page) 
     
     
     
            
    def create_main_page(self):
        page = QWidget()
        layout = QHBoxLayout()
        page.setLayout(layout)
        
        # 左侧图片区域
        left_frame = QFrame()
        left_frame.setFixedWidth(500)
        left_layout = QVBoxLayout()
        left_frame.setLayout(left_layout)
        
        # 初始化 main_image_label 并绑定到实例（关键修复）
        self.main_image_label = QLabel()
        self.main_image_label.setFixedSize(480, 480)
        self.main_image_label.setAlignment(Qt.AlignCenter)
        self.main_image_label.setStyleSheet("border: 1px solid #ddd;")
        
        self.update_main_image()  # 初始加载  
        # 动态加载图片
        self.load_saved_mbti()  # 加载历史结果
        if self.current_mbti_type:
            pixmap_path = f"asset/mbti-icons/demo_{self.current_mbti_type}.png"
        else:
            pixmap_path = "asset/mbti-icons/16-personalities.png"  # 默认图片
        
        pixmap = QPixmap(pixmap_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(480, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.main_image_label.setPixmap(pixmap)
        else:
            self.main_image_label.setText("图片加载失败")
            self.main_image_label.setStyleSheet("color: red; font-size: 14px;")
        
        left_layout.addWidget(self.main_image_label)
        layout.addWidget(left_frame)
        
        # 右侧选项区域
        right_frame = QFrame()
        right_layout = QVBoxLayout()
        right_frame.setLayout(right_layout)
        
        title = QLabel("您的心理健康助手")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #2c3e50; 
            margin-top: 30px;
            margin-bottom: 30px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        """)
        right_layout.addWidget(title)
        
        # 功能按钮子布局（关键调整：按钮添加到子布局而非主布局）
        button_layout = QVBoxLayout()
        button_layout.setSpacing(45)  # 按钮垂直间距（可根据需求调整）
        button_layout.setContentsMargins(20, 10, 20, 15)  # 子布局内边距（左右20，上10，下15）      
        
        # 功能按钮
        buttons = [
            ("MBTI性格自测>>>", self.show_test_selection),
            ("与小鲸鱼聊聊qwq", self.show_doubao_chat),
            ("听音乐放松一下~", self.show_relaxing_page)
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text)
            font = QFont("Microsoft YaHei", 13)
            font.setItalic(True)  # 设置斜体
            btn.setFont(font)
            btn.setFixedSize(280, 55)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    min-width: 250px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn, alignment=Qt.AlignCenter)
        
        right_layout.addLayout(button_layout)  # 底部填充
        right_layout.addStretch()
        layout.addWidget(right_frame)
        
        return page


    '''   
    def show_doubao_chat(self):
        """显示豆包对话窗口"""
        self.stack.setCurrentWidget(self.doubao_chat)
    '''  
    
      
    '''以下是我关于mzr部分的尝试'''
    def show_doubao_chat(self):
        """显示豆包对话前先显示问题弹窗"""
        self.question_popup = QuestionPopup()
        self.question_popup.back_to_main.connect(lambda: self.stack.setCurrentWidget(self.main_page))
        self.question_popup.goto_chat.connect(self.handle_chat_question)
        self.question_popup.show()  # 显示弹窗

    def handle_chat_question(self, question):
        """处理弹窗传递的问题"""
        # 填充问题并跳转对话界面
        self.stack.setCurrentWidget(self.doubao_chat)
        if question:
            self.doubao_chat.message_input.setText(question)
            self.doubao_chat.send_message()  # 自动发送问题    
    '''尝试结束'''
    
    
    
    def show_relaxing_page(self):
        """显示放松音乐页面"""
        self.stack.setCurrentWidget(self.relaxing_page)

    def show_mbti_result(self, mbti_type):
        # 保存当前测试结果到类属性（替代全局变量）
        self.current_mbti_type = mbti_type
        # 立即更新主页面图片（关键修改）
        self.update_main_image()
        
        
        # 暂存修改：
        
        result_page = QWidget()
        # 主布局改为水平分栏（左侧描述+右侧图片）
        main_layout = QHBoxLayout(result_page)
        main_layout.setContentsMargins(50, 30, 50, 30)  # 调整整体边距
        main_layout.setSpacing(40)  # 左右栏间距

        # 左侧描述区域（垂直布局）
        left_container = QVBoxLayout()
        main_layout.addLayout(left_container)

        # 人格类型标题（左侧顶部）
        title = QLabel(f"你的MBTI类型：{mbti_type}")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        # 左侧居中添加控件
        left_container.addWidget(title, alignment=Qt.AlignLeft | Qt.AlignHCenter)

        # 人格描述文本框（左侧下方）
        description = MBTI_Descriptions.get(mbti_type, {})
        desc_text = description.get("description", "未找到该类型的描述")
        description_edit = QTextEdit(desc_text.strip())
        description_edit.setReadOnly(True)
        description_edit.setMinimumWidth(250)  # 左侧描述区宽度
        description_edit.setStyleSheet("""
            QTextEdit {
                font-size: 18px;
                color: #333;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 15px;
                background-color: #f9f9f9;
            }
        """)
        left_container.addWidget(description_edit)

        # 右侧图片区域（垂直布局，用于居中图片）
        right_container = QVBoxLayout()
        main_layout.addLayout(right_container)

        # 结果图片（右侧居中显示）
        result_pic = QLabel()
        pic_path = f"asset/mbti-icons/demo_{mbti_type}.png"
        if os.path.exists(pic_path):
            pixmap = QPixmap(pic_path).scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            # 无对应图片时使用默认图片
            pixmap = QPixmap("asset/mbti-icons/default.png").scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # 应用圆形遮罩（与音乐页面图片样式保持一致）
        mask = QBitmap(300, 300)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.color1)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 300, 300)
        painter.end()
        pixmap.setMask(mask)
        result_pic.setPixmap(pixmap)
        right_container.addWidget(result_pic, alignment=Qt.AlignCenter)  # 图片垂直居中

        # 底部按钮（保持原有并排样式，添加到左侧或右侧均可，这里添加到左侧）
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(20)
        left_container.addWidget(btn_container, alignment=Qt.AlignCenter)  # 按钮在左侧底部居中

        # "问问小鲸鱼"按钮
        ask_btn = QPushButton("问问小鲸鱼")
        ask_btn.setFixedSize(200, 50)
        ask_btn.setStyleSheet("background-color: #07c160; color: white; border-radius: 8px; font-size: 18px;")
        ask_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.doubao_chat))
        btn_layout.addWidget(ask_btn)

        # "返回主页"按钮
        back_btn = QPushButton("返回主页")
        back_btn.setFixedSize(200, 50)
        back_btn.setStyleSheet("background-color: #3498db; color: white; border-radius: 8px; font-size: 18px;")
        back_btn.clicked.connect(lambda: [self.stack.setCurrentWidget(self.main_page), self.update_main_image()])
        btn_layout.addWidget(back_btn)

        self.stack.addWidget(result_page)
        self.stack.setCurrentWidget(result_page)        
        
        


    def analyze_mbti_with_doubao(self, mbti_type):
        """使用豆包API分析MBTI类型"""
        # 切换到豆包对话窗口
        self.stack.setCurrentWidget(self.doubao_chat)
        
        # 发送分析请求
        message = f"请分析一下MBTI类型为{mbti_type}的人的性格特点，以及适合他们的减压方法和职业建议"
        self.doubao_chat.message_input.setText(message)
        self.doubao_chat.send_message()


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    with open("style.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    
    # 尝试加载样式表
    try:
        with open("style.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except:
        pass
    
    window = MentalHealthApp()
    window.show()
    app.exec_()