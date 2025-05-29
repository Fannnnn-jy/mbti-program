import subprocess
import sys

def install_packages():
    packages = [
        'pyqt5',          # PyQt5 GUI库
        'openai',         # OpenAI API
        'pillow',         # PIL图像处理库
        'requests',       # HTTP请求库
        'python-vlc',     # VLC媒体播放器接口
        'selenium',       # 浏览器自动化测试库
        'webdriver-manager',  # 浏览器驱动管理
        'beautifulsoup4'  # HTML/XML解析库
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"成功安装: {package}")
        except subprocess.CalledProcessError as e:
            print(f"安装{package}失败: {e}")

if __name__ == "__main__":
    install_packages()
    print("所有依赖包安装完成！")