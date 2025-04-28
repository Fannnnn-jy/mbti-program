from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QFrame, QRadioButton,  QButtonGroup, QScrollArea, QStackedWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
import os

CURRENT_TYPE = None


import random

# 模拟MBTI数据
MBTI_TYPES = ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP",
              "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]

MBTI_QUESTIONS = [
    {"question": "在社交场合中，你通常", "options": ["主动与人交谈", "等待别人来找你"]},
    {"question": "你更倾向于", "options": ["关注现实和具体事物", "关注可能性和整体概念"]},
    {"question": "做决定时，你更注重", "options": ["逻辑和客观因素", "情感和人际关系"]},
    {"question": "你喜欢的生活方式是", "options": ["有计划有组织的", "灵活随性的"]}
] * 10  # 重复10次模拟40个问题

class MBTITestPage(QWidget):
    test_completed = pyqtSignal(str)  # 测试完成信号，传递MBTI类型
    
    def __init__(self):
        super().__init__()
        self.current_question = 0
        self.answers = []
        self.init_ui()
        
    def init_ui(self):
        self.setLayout(QVBoxLayout())
        
        # 顶部进度条
        self.progress_label = QLabel("问题 1/40")
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
        
        # 加载第一个问题
        self.load_question(0)
    
    def load_question(self, index):
        self.current_question = index
        question_data = MBTI_QUESTIONS[index]
        
        self.question_label.setText(f"问题 {index + 1}: {question_data['question']}")
        for i, option in enumerate(question_data['options']):
            self.option_buttons[i].setText(option)
            self.option_buttons[i].setChecked(False)
        
        # 更新进度
        self.progress_label.setText(f"问题 {index + 1}/{len(MBTI_QUESTIONS)}")
        
        # 更新按钮状态
        self.prev_btn.setEnabled(index > 0)
        if index == len(MBTI_QUESTIONS) - 1:
            self.next_btn.setText("完成测试")
        else:
            self.next_btn.setText("下一题")
    
    def prev_question(self):
        if self.current_question > 0:
            self.load_question(self.current_question - 1)
    
    def next_question(self):
        selected = self.button_group.checkedId()
        if selected == -1:
            QMessageBox.warning(self, "提示", "请选择一个选项")
            return
        
        # 记录答案
        if len(self.answers) > self.current_question:
            self.answers[self.current_question] = selected
        else:
            self.answers.append(selected)
        
        # 检查是否完成
        if self.current_question == len(MBTI_QUESTIONS) - 1:
            self.complete_test()
        else:
            self.load_question(self.current_question + 1)
    
    def complete_test(self):
        # 这里简化处理，随机返回一个MBTI类型
        mbti_type = random.choice(MBTI_TYPES)
        self.test_completed.emit(mbti_type)


class MentalHealthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("心理健康助手")
        self.setFixedSize(1000, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # 主窗口部件
        self.main_page = self.create_main_page()
        self.stack.addWidget(self.main_page)

        self.mbti_test_page = MBTITestPage()
        self.mbti_test_page.test_completed.connect(self.show_mbti_result)
        self.stack.addWidget(self.mbti_test_page)
        
        # 结果页面
        self.mbti_result_page = None

    def create_main_page(self):
        page = QWidget()
        layout = QHBoxLayout()
        page.setLayout(layout)
        
        # 左侧图片区域
        left_frame = QFrame()
        left_frame.setFixedWidth(500)
        left_layout = QVBoxLayout()
        left_frame.setLayout(left_layout)
        
        image_label = QLabel()
        image_label.setFixedSize(480, 480)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("border: 1px solid #ddd;")
        
        pixmap = QPixmap("mbti-program/asset/mbti-icons/16-personalities.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(480, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("图片加载失败")
            image_label.setStyleSheet("color: red; font-size: 14px;")
        
        left_layout.addWidget(image_label)
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
        
        # 功能按钮
        buttons = [
            ("MBTI性格自测", self.start_mbti_test),
            ("减压技巧", self.show_relaxation_tips),
            ("专业帮助", self.show_professional_help)
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setFont(QFont("Microsoft YaHei", 14))
            btn.setFixedHeight(50)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    min-width: 250px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn.clicked.connect(callback)
            right_layout.addWidget(btn, alignment=Qt.AlignCenter)
            right_layout.addSpacing(20)
        
        right_layout.addStretch()
        layout.addWidget(right_frame)
        
        return page

    def start_mbti_test(self):
        QMessageBox.information(self, "MBTI人格测试", 
                              "即将开始MBTI性格测试...\n\n"
                              "本测试包含93个问题，约需18分钟完成。")
        self.stack.setCurrentWidget(self.mbti_test_page)
    
    def show_relaxation_tips(self):
        QMessageBox.information(self, "减压技巧", 
                              "常用减压方法:\n\n"
                              "1. 深呼吸练习 - 4-7-8呼吸法\n"
                              "2. 渐进式肌肉放松 - 从头到脚放松\n"
                              "3. 正念冥想 - 关注当下感受\n"
                              "4. 轻度运动 - 散步或瑜伽\n"
                              "5. 艺术创作 - 绘画或音乐")
    
    def show_professional_help(self):
        QMessageBox.information(self, "专业帮助", 
                              "如需专业心理咨询:\n\n"
                              "心理援助热线: 12320 (24小时)\n"
                              "北京心理危机干预中心: 010-82951332\n"
                              "上海心理热线: 021-12320-5\n\n"
                              "工作时间: 9:00-21:00")

    def show_mbti_result(self, mbti_type):
        # 创建结果页面
        result_page = QWidget()
        layout = QVBoxLayout()
        result_page.setLayout(layout)
        
        # 结果标题
        title = QLabel(f"您的MBTI类型是: {mbti_type}")
        title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 30px;")
        layout.addWidget(title)
        
        # 类型描述
        desc = QLabel("这里显示该类型的详细描述...")
        desc.setWordWrap(True)
        desc.setFont(QFont("Microsoft YaHei", 12))
        desc.setStyleSheet("margin: 0 50px;")
        layout.addWidget(desc)
        
        # 返回按钮
        back_btn = QPushButton("返回主页")
        back_btn.setFont(QFont("Microsoft YaHei", 14))
        back_btn.setFixedHeight(50)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                min-width: 200px;
            }
        """)
        back_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.main_page))
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        layout.addStretch()
        
        # 添加到堆叠窗口并切换
        self.stack.addWidget(result_page)
        self.stack.setCurrentWidget(result_page)
        
if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    window = MentalHealthApp()
    window.show()
    app.exec_()