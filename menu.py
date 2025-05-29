from PyQt5.QtWidgets import (QApplication, QComboBox, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QMessageBox, QFrame, QRadioButton, 
                            QButtonGroup, QScrollArea, QStackedWidget, QTextEdit, QLineEdit, QSlider)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QTimer, QDateTime
from PyQt5.QtGui import QFont, QPixmap, QTransform, QPainter, QBitmap, QImage, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os
from PIL import Image
CURRENT_TYPE = None

from openai import OpenAI
client = OpenAI(api_key="sk-42d27f7d36474c108d648985219ab3c0", base_url="https://api.deepseek.com")

# 从 MBTI_data.py 中导入题库
from MBTI_data import MBTI_Choices, MBTI_Questions, MBTI_Descriptions
from MBTI_data_easy import MBTI_Choices as MBTI_Choices_easy, MBTI_Questions as MBTI_Questions_easy, MBTI_Descriptions as MBTI_Descriptions_easy

# 计分规则映射表：(问题编号j, 选项) → (维度, 分数变化)
WHOLE_SCORING_RULES = {
    # 外向与内向（E/I）维度：a1对应E/I
    (4, 'A'): ('I', 1),   # j=4选A → 内向(I)加1分
    (4, 'B'): ('E', 1),   # j=4选B → 外向(E)加1分
    (8, 'A'): ('I', 1), (8, 'B'): ('E', 1),
    (14, 'A'): ('I', 1), (14, 'B'): ('E', 1),
    (19, 'A'): ('I', 1), (19, 'B'): ('E', 1),
    (23, 'A'): ('I', 1), (23, 'B'): ('E', 1),
    (34, 'A'): ('I', 1), (34, 'B'): ('E', 1),
    (62, 'A'): ('I', 1), (62, 'B'): ('E', 1),
    (67, 'A'): ('I', 1), (67, 'B'): ('E', 1),
    (77, 'A'): ('I', 1), (77, 'B'): ('E', 1),
    
    (12, 'B'): ('I', 1),  # j=12选B → 内向(I)加1分
    (12, 'A'): ('E', 1),  # j=12选A → 外向(E)加1分
    (18, 'B'): ('I', 1), (18, 'A'): ('E', 1),
    (22, 'B'): ('I', 1), (22, 'A'): ('E', 1),
    (26, 'B'): ('I', 1), (26, 'A'): ('E', 1),
    (27, 'B'): ('I', 1), (27, 'A'): ('E', 1),
    (35, 'B'): ('I', 1), (35, 'A'): ('E', 1),
    (42, 'B'): ('I', 1), (42, 'A'): ('E', 1),
    (48, 'B'): ('I', 1), (48, 'A'): ('E', 1),
    (54, 'B'): ('I', 1), (54, 'A'): ('E', 1),
    (60, 'B'): ('I', 1), (60, 'A'): ('E', 1),
    (66, 'B'): ('I', 1), (66, 'A'): ('E', 1),
    (72, 'B'): ('I', 1), (72, 'A'): ('E', 1),

    # 实感与直觉（S/N）维度：a2对应S/N
    (3, 'A'): ('S', 1),   # j=3选A → 实感(S)加1分
    (3, 'B'): ('N', 1),   # j=3选B → 直觉(N)加1分
    (13, 'A'): ('S', 1), (13, 'B'): ('N', 1),
    (32, 'A'): ('S', 1), (32, 'B'): ('N', 1),
    (40, 'A'): ('S', 1), (40, 'B'): ('N', 1),
    (47, 'A'): ('S', 1), (47, 'B'): ('N', 1),
    (53, 'A'): ('S', 1), (53, 'B'): ('N', 1),
    (58, 'A'): ('S', 1), (58, 'B'): ('N', 1),
    (61, 'A'): ('S', 1), (61, 'B'): ('N', 1),
    (73, 'A'): ('S', 1), (73, 'B'): ('N', 1),
    (82, 'A'): ('S', 1), (82, 'B'): ('N', 1),
    (86, 'A'): ('S', 1), (86, 'B'): ('N', 1),
    (90, 'A'): ('S', 1), (90, 'B'): ('N', 1),
    (93, 'A'): ('S', 1), (93, 'B'): ('N', 1),

    (5, 'B'): ('S', 1),   # j=5选B → 实感(S)加1分
    (5, 'A'): ('N', 1),   # j=5选A → 直觉(N)加1分
    (15, 'B'): ('S', 1), (15, 'A'): ('N', 1),
    (24, 'B'): ('S', 1), (24, 'A'): ('N', 1),
    (29, 'B'): ('S', 1), (29, 'A'): ('N', 1),
    (37, 'B'): ('S', 1), (37, 'A'): ('N', 1),
    (44, 'B'): ('S', 1), (44, 'A'): ('N', 1),
    (50, 'B'): ('S', 1), (50, 'A'): ('N', 1),
    (55, 'B'): ('S', 1), (55, 'A'): ('N', 1),
    (63, 'B'): ('S', 1), (63, 'A'): ('N', 1),
    (74, 'B'): ('S', 1), (74, 'A'): ('N', 1),
    (79, 'B'): ('S', 1), (79, 'A'): ('N', 1),
    (83, 'B'): ('S', 1), (83, 'A'): ('N', 1),
    (87, 'B'): ('S', 1), (87, 'A'): ('N', 1),

    # 思考与情感（T/F）维度：a3对应T/F
    (31, 'A'): ('T', 1),  # j=31选A → 思考(T)加1分
    (31, 'B'): ('F', 1),  # j=31选B → 情感(F)加1分
    (39, 'A'): ('T', 1), (39, 'B'): ('F', 1),
    (46, 'A'): ('T', 1), (46, 'B'): ('F', 1),
    (52, 'A'): ('T', 1), (52, 'B'): ('F', 1),
    (57, 'A'): ('T', 1), (57, 'B'): ('F', 1),
    (69, 'A'): ('T', 1), (69, 'B'): ('F', 1),
    (78, 'A'): ('T', 1), (78, 'B'): ('F', 1),
    (81, 'A'): ('T', 1), (81, 'B'): ('F', 1),
    (85, 'A'): ('T', 1), (85, 'B'): ('F', 1),
    (89, 'A'): ('T', 1), (89, 'B'): ('F', 1),
    (92, 'A'): ('T', 1), (92, 'B'): ('F', 1),

    (6, 'B'): ('T', 1),   # j=6选B → 思考(T)加1分
    (6, 'A'): ('F', 1),   # j=6选A → 情感(F)加1分
    (16, 'B'): ('T', 1), (16, 'A'): ('F', 1),
    (30, 'B'): ('T', 1), (30, 'A'): ('F', 1),
    (38, 'B'): ('T', 1), (38, 'A'): ('F', 1),
    (45, 'B'): ('T', 1), (45, 'A'): ('F', 1),
    (51, 'B'): ('T', 1), (51, 'A'): ('F', 1),
    (56, 'B'): ('T', 1), (56, 'A'): ('F', 1),
    (64, 'B'): ('T', 1), (64, 'A'): ('F', 1),
    (75, 'B'): ('T', 1), (75, 'A'): ('F', 1),
    (80, 'B'): ('T', 1), (80, 'A'): ('F', 1),
    (84, 'B'): ('T', 1), (84, 'A'): ('F', 1),
    (88, 'B'): ('T', 1), (88, 'A'): ('F', 1),
    (91, 'B'): ('T', 1), (91, 'A'): ('F', 1),

    # 判断与认知（J/P）维度：a4对应J/P
    (1, 'A'): ('J', 1),   # j=1选A → 判断(J)加1分
    (1, 'B'): ('P', 1),   # j=1选B → 认知(P)加1分
    (9, 'A'): ('J', 1), (9, 'B'): ('P', 1),
    (10, 'A'): ('J', 1), (10, 'B'): ('P', 1),
    (20, 'A'): ('J', 1), (20, 'B'): ('P', 1),
    (28, 'A'): ('J', 1), (28, 'B'): ('P', 1),
    (36, 'A'): ('J', 1), (36, 'B'): ('P', 1),
    (43, 'A'): ('J', 1), (43, 'B'): ('P', 1),
    (49, 'A'): ('J', 1), (49, 'B'): ('P', 1),
    (59, 'A'): ('J', 1), (59, 'B'): ('P', 1),
    (68, 'A'): ('J', 1), (68, 'B'): ('P', 1),
    (70, 'A'): ('J', 1), (70, 'B'): ('P', 1),

    (2, 'B'): ('J', 1),   # j=2选B → 判断(J)加1分
    (2, 'A'): ('P', 1),   # j=2选A → 认知(P)加1分
    (7, 'B'): ('J', 1), (7, 'A'): ('P', 1),
    (11, 'B'): ('J', 1), (11, 'A'): ('P', 1),
    (17, 'B'): ('J', 1), (17, 'A'): ('P', 1),
    (21, 'B'): ('J', 1), (21, 'A'): ('P', 1),
    (25, 'B'): ('J', 1), (25, 'A'): ('P', 1),
    (33, 'B'): ('J', 1), (33, 'A'): ('P', 1),
    (41, 'B'): ('J', 1), (41, 'A'): ('P', 1),
    (65, 'B'): ('J', 1), (65, 'A'): ('P', 1),
    (71, 'B'): ('J', 1), (71, 'A'): ('P', 1),
    (76, 'B'): ('J', 1), (76, 'A'): ('P', 1),
}
EASY_SCORING_RULES = {
    # 第1-7题：A→E，B→I
    (1, 'A'): ('E', 1), (1, 'B'): ('I', 1),
    (2, 'A'): ('E', 1), (2, 'B'): ('I', 1),
    (3, 'A'): ('E', 1), (3, 'B'): ('I', 1),
    (4, 'A'): ('E', 1), (4, 'B'): ('I', 1),
    (5, 'A'): ('E', 1), (5, 'B'): ('I', 1),
    (6, 'A'): ('E', 1), (6, 'B'): ('I', 1),
    (7, 'A'): ('E', 1), (7, 'B'): ('I', 1),

    # 第8-14题：A→N，B→S
    (8, 'A'): ('N', 1), (8, 'B'): ('S', 1),
    (9, 'A'): ('N', 1), (9, 'B'): ('S', 1),
    (10, 'A'): ('N', 1), (10, 'B'): ('S', 1),
    (11, 'A'): ('N', 1), (11, 'B'): ('S', 1),
    (12, 'A'): ('N', 1), (12, 'B'): ('S', 1),
    (13, 'A'): ('N', 1), (13, 'B'): ('S', 1),
    (14, 'A'): ('N', 1), (14, 'B'): ('S', 1),

    # 第15-21题：A→F，B→T
    (15, 'A'): ('F', 1), (15, 'B'): ('T', 1),
    (16, 'A'): ('F', 1), (16, 'B'): ('T', 1),
    (17, 'A'): ('F', 1), (17, 'B'): ('T', 1),
    (18, 'A'): ('F', 1), (18, 'B'): ('T', 1),
    (19, 'A'): ('F', 1), (19, 'B'): ('T', 1),
    (20, 'A'): ('F', 1), (20, 'B'): ('T', 1),
    (21, 'A'): ('F', 1), (21, 'B'): ('T', 1),

    # 第22-28题：A→J，B→P
    (22, 'A'): ('J', 1), (22, 'B'): ('P', 1),
    (23, 'A'): ('J', 1), (23, 'B'): ('P', 1),
    (24, 'A'): ('J', 1), (24, 'B'): ('P', 1),
    (25, 'A'): ('J', 1), (25, 'B'): ('P', 1),
    (26, 'A'): ('J', 1), (26, 'B'): ('P', 1),
    (27, 'A'): ('J', 1), (27, 'B'): ('P', 1),
    (28, 'A'): ('J', 1), (28, 'B'): ('P', 1),
}

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
        self.progress_label.setStyleSheet("font-size: 14px; color: #555;")
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
        self.question_label.setStyleSheet("font-size: 16px; margin-bottom: 20px;")
        container.layout().addWidget(self.question_label)

        # 选项按钮组
        self.button_group = QButtonGroup()
        self.option_buttons = []

        for i in range(2):  # 每个问题2个选项
            rb = QRadioButton()
            rb.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
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
        reply = QMessageBox.question(self, '确认退出', '是否要退出当前测试？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 返回主页面
            self.parent().stack.setCurrentWidget(self.parent().main_page)


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
    """豆包API对话窗口"""
    back_to_main = pyqtSignal()  # 添加返回主页面的信号

    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        
        # 标题栏
        title_layout = QHBoxLayout()
        title_label = QLabel("智能心理咨询")

        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30,30)
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
        
        # 对话显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            background-color: #f0f0f0;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
        """)
        layout.addWidget(self.chat_display)
        
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
        
        # 初始问候
        self.show_message("豆包助手", "你好！我是智能心理咨询助手，有什么可以帮助你的吗？")
    # 气泡可以显示的版本
    # def show_message(self, sender, message):
    #     """在对话窗口中显示消息，使用微信风格的气泡"""
    #     timestamp = QDateTime.currentDateTime().toString("hh:mm")
        
    #     if sender == "你":
    #         # 用户消息（右对齐）
    #         self.chat_display.append(f"""
    #             <div style="text-align: right; margin: 12px 0;">
    #                 <div style="display: inline-block; text-align: right; margin-right: 12px;">
    #                     <span style="font-size: 13px; color: #666;">{timestamp}</span>
    #                     <div style="display: inline-block; background-color: #07c160; color: white; 
    #                                 border-radius: 20px; padding: 14px 20px; min-height: 42px; margin-top: 6px;
    #                                 width: fit-content; max-width: 75%; word-wrap: break-word; position: relative;
    #                                 font-size: 20px; line-height: 1.4;">  <!-- 字体大小调整为20px -->
    #                         {message}
    #                         <div style="position: absolute; right: -8px; top: 14px; 
    #                                     width: 0; height: 0; border-top: 8px solid transparent; 
    #                                     border-left: 16px solid #07c160; border-bottom: 8px solid transparent;"></div>
    #                     </div>
    #                 </div>
    #                 <img src="path/to/user/avatar.png" style="width: 48px; height: 48px; 
    #                         border-radius: 50%; vertical-align: top;" />
    #             </div>
    #         """)
    #     else:
    #         # AI消息（左对齐）
    #         self.chat_display.append(f"""
    #             <div style="text-align: left; margin: 12px 0;">
    #                 <img src="path/to/ai/avatar.png" style="width: 48px; height: 48px; 
    #                         border-radius: 50%; vertical-align: top;" />
    #                 <div style="display: inline-block; text-align: left; margin-left: 12px;">
    #                     <div style="font-size: 18px; font-weight: bold; color: #333;">{sender}</div>
    #                     <span style="font-size: 13px; color: #666;">{timestamp}</span>
    #                     <div style="display: inline-block; background-color: white; color: #333; 
    #                                 border-radius: 20px; padding: 14px 20px; min-height: 42px; margin-top: 6px;
    #                                 width: fit-content;max-width: 75%; word-wrap: break-word; position: relative;
    #                                 box-shadow: 0 1px 3px rgba(0,0,0,0.15);
    #                                 font-size: 20px; line-height: 1.4;">  <!-- 字体大小调整为20px -->
    #                         {message}
    #                         <div style="position: absolute; left: -8px; top: 14px; 
    #                                     width: 0; height: 0; border-top: 8px solid transparent; 
    #                                     border-right: 16px solid white; border-bottom: 8px solid transparent;"></div>
    #                     </div>
    #                 </div>
    #             </div>
    #         """)

    def show_message(self, sender, message):
        """在对话窗口中显示消息，使用微信风格的气泡"""
        timestamp = QDateTime.currentDateTime().toString("hh:mm")
        
        if sender == "你":
            # 用户消息（右对齐）
            self.chat_display.append(f"""
                <div style="text-align: right; margin: 12px 0; overflow: hidden;">  <!-- 添加overflow:hidden -->
                    <div style="display: inline-block; text-align: right; margin-right: 12px;">
                        <span style="font-size: 13px; color: #666;">{timestamp}</span>
                        <div style="display: inline-block; background-color: #07c160; color: white; 
                                    border-radius: 20px; padding: 14px 20px; margin-top: 6px;
                                    min-width: 40px;  <!-- 最小宽度 -->
                                    max-width: 75%;  <!-- 最大宽度 -->
                                    word-wrap: break-word; position: relative;
                                    font-size: 20px; line-height: 1.4;
                                    box-sizing: border-box;  <!-- 确保内边距包含在尺寸内 -->
                                    vertical-align: top;">  <!-- 垂直对齐顶部 -->
                            {message}
                            <div style="position: absolute; right: -8px; top: 16px;  <!-- 微调位置 -->
                                        width: 0; height: 0; border-top: 8px solid transparent; 
                                        border-left: 16px solid #07c160; border-bottom: 8px solid transparent;"></div>
                        </div>
                    </div>
                    <img src="path/to/user/avatar.png" style="width: 48px; height: 48px; 
                            border-radius: 50%; vertical-align: top; display: inline-block;" />  <!-- 确保图片是内联块 -->
                </div>
            """)
        else:
            # AI消息（左对齐）
            self.chat_display.append(f"""
                <div style="text-align: left; margin: 12px 0; overflow: hidden;">  <!-- 添加overflow:hidden -->
                    <img src="path/to/ai/avatar.png" style="width: 48px; height: 48px; 
                            border-radius: 50%; vertical-align: top; display: inline-block;" />  <!-- 确保图片是内联块 -->
                    <div style="display: inline-block; text-align: left; margin-left: 12px;">
                        <div style="font-size: 18px; font-weight: bold; color: #333;">{sender}</div>
                        <span style="font-size: 13px; color: #666;">{timestamp}</span>
                        <div style="display: inline-block; background-color: white; color: #333; 
                                    border-radius: 20px; padding: 14px 20px; margin-top: 6px;
                                    min-width: 40px;  <!-- 最小宽度 -->
                                    max-width: 75%;  <!-- 最大宽度 -->
                                    word-wrap: break-word; position: relative;
                                    box-shadow: 0 1px 3px rgba(0,0,0,0.15);
                                    font-size: 20px; line-height: 1.4;
                                    box-sizing: border-box;  <!-- 确保内边距包含在尺寸内 -->
                                    vertical-align: top;">  <!-- 垂直对齐顶部 -->
                            {message}
                            <div style="position: absolute; left: -8px; top: 16px;  <!-- 微调位置 -->
                                        width: 0; height: 0; border-top: 8px solid transparent; 
                                        border-right: 16px solid white; border-bottom: 8px solid transparent;"></div>
                        </div>
                    </div>
                </div>
            """)

    def return_to_main(self):
        """发送返回主页面信号"""
        self.back_to_main.emit()
    
    def send_message(self):
        """发送消息到豆包API并获取回复"""
        message = self.message_input.text().strip()
        if not message:
            return
            
        # 显示用户消息
        self.show_message("你", message)
        self.message_input.clear()
        
        # 显示"正在思考"
        self.show_message("豆包助手", "正在思考...")
        
        # 模拟调用豆包API（实际使用时需要替换为真实API调用）
        QTimer.singleShot(1000, lambda: self.get_doubao_response(message))
    
    def get_doubao_response(self, message):
        """模拟从豆包API获取回复"""
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
        self.show_message("豆包助手", reply_content)  # 只显示内容部分


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
            margin-bottom: 30px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        """)
        right_layout.addWidget(title)
        
        # 功能按钮子布局（关键调整：按钮添加到子布局而非主布局）
        button_layout = QVBoxLayout()
        button_layout.setSpacing(45)  # 按钮垂直间距（可根据需求调整）
        button_layout.setContentsMargins(20, 15, 20, 15)  # 子布局内边距（左右20，上下15）      
        
        # 功能按钮
        buttons = [
            ("MBTI性格自测>>>", self.show_test_selection),
            ("与豆包聊聊qwq", self.show_doubao_chat),
            ("听音乐放松一下~", self.show_relaxing_page)
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setFont(QFont("Microsoft YaHei", 14))
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


    
    def show_doubao_chat(self):
        """显示豆包对话窗口"""
        self.stack.setCurrentWidget(self.doubao_chat)
    
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