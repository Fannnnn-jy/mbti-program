from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import os

class MentalHealthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("心理健康助手")
        self.setFixedSize(1000, 600)
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 使用水平布局分左右两栏
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)  # 设置边距
        central_widget.setLayout(main_layout)

        # 左侧图片区域 (40%宽度)
        left_frame = QFrame()
        left_frame.setFixedWidth(400)  # 固定宽度
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 20, 0)  # 右侧留出间距
        left_frame.setLayout(left_layout)
        
        # 加载图片 - 使用正斜杠或原始字符串
        image_label = QLabel()
        image_path = os.path.normpath("mbti-program/asset/mbti-icons/16-personalities.png")
        pixmap = QPixmap(image_path)
        
        if not pixmap.isNull():
            pixmap = pixmap.scaled(380, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
        else:
            image_label.setText("图片加载失败\n请检查图片路径")
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("color: red; font-size: 14px;")

        left_layout.addWidget(image_label)
        left_layout.addStretch()
        main_layout.addWidget(left_frame)
        
        # 右侧功能区域 (60%宽度)
        right_frame = QFrame()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(20, 0, 0, 0)  # 左侧留出间距
        right_frame.setLayout(right_layout)
        
        # 标题
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
        
        # 功能按钮区域
        button_frame = QFrame()
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)  # 按钮间距
        button_frame.setLayout(button_layout)
        
        # 三个功能按钮
        options = [
            ("MBTI性格自测", self.show_mbti_test),
            ("减压技巧", self.show_relaxation_tips),
            ("专业帮助", self.show_professional_help)
        ]
        
        for text, callback in options:
            btn = QPushButton(text)
            btn.setFont(QFont("Microsoft YaHei", 14))
            btn.setFixedHeight(50)  # 固定按钮高度
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
                QPushButton:pressed {
                    background-color: #1d6fa5;
                }
            """)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn, alignment=Qt.AlignCenter)
        
        right_layout.addWidget(button_frame)
        right_layout.addStretch()
        main_layout.addWidget(right_frame)
    
    def show_mbti_test(self):
        # 这里可以跳转到MBTI测试页面
        QMessageBox.information(self, "MBTI人格测试", 
                              "即将开始MBTI性格测试...\n\n"
                              "本测试包含93个问题，约需18分钟完成。")
    
    def show_relaxation_tips(self):
        # 可以扩展为包含更多减压方法的页面
        QMessageBox.information(self, "减压技巧", 
                              "常用减压方法:\n\n"
                              "1. 深呼吸练习 - 4-7-8呼吸法\n"
                              "2. 渐进式肌肉放松 - 从头到脚放松\n"
                              "3. 正念冥想 - 关注当下感受\n"
                              "4. 轻度运动 - 散步或瑜伽\n"
                              "5. 艺术创作 - 绘画或音乐")
    
    def show_professional_help(self):
        # 可以添加更多专业资源
        QMessageBox.information(self, "专业帮助", 
                              "如需专业心理咨询:\n\n"
                              "心理援助热线: 12320 (24小时)\n"
                              "北京心理危机干预中心: 010-82951332\n"
                              "上海心理热线: 021-12320-5\n\n"
                              "工作时间: 9:00-21:00")

if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    window = MentalHealthApp()
    window.show()
    app.exec_()