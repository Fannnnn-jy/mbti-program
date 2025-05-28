import sys
import time
import os
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QLineEdit, QLabel, QComboBox, QMessageBox)
from PyQt5.QtGui import QIcon
import vlc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GeQuHaiPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("歌曲海音乐下载器")
        self.setFixedSize(500, 400)
        self.setWindowIcon(QIcon("asset/icons/gequhai.png"))
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

        # self.play_btn = QPushButton("播放选中歌曲")
        # self.play_btn.clicked.connect(self.play_selected)
        # self.layout.addWidget(self.play_btn)

        self.download_btn = QPushButton("下载选中歌曲")
        self.download_btn.clicked.connect(self.download_selected)
        self.layout.addWidget(self.download_btn)

        # self.stop_btn = QPushButton("返回播放页面")
        # self.stop_btn.clicked.connect(self.stop_playing)
        # self.layout.addWidget(self.stop_btn)

        self.status_label = QLabel("准备就绪")
        self.layout.addWidget(self.status_label)

        self.vlc_instance = self.vlc_instance = vlc.Instance('--quiet', '--no-video')
        self.player = self.vlc_instance.media_player_new()

        self.song_map = {}  # display text → (title, song_id, play_url)
        self.driver = None

        self.save_folder = 'asset\\music'
        os.makedirs(self.save_folder, exist_ok=True)

    def init_driver(self):
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def search_music(self):
        keyword = self.search_box.text().strip()
        if not keyword:
            self.status_label.setText("请输入关键词")
            return

        self.status_label.setText("搜索中，请稍候... \n （爬虫搜索可能耗时较长）")
        QApplication.processEvents()
        self.init_driver()

        try:
            search_url = f"https://www.gequhai.net/s/{keyword}"
            self.driver.get(search_url)
            # 等待列表出现
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-8.col-content a.music-link"))
            )

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            # 1) 找到所有歌曲链接
            links = soup.select("div.col-8.col-content a.music-link")

            self.result_combo.clear()
            self.song_map.clear()

            for a in links:
                title = a.get_text(strip=True)
                href  = a["href"]                      # "/music/4190"
                song_id = href.rsplit("/", 1)[-1]      # "4190"

                # 2) 找到同一行里的艺术家
                row = a.find_parent("div", class_="row")
                artist_div = row.select_one("div.col-4.col-content")
                artist = artist_div.get_text(strip=True) if artist_div else ""

                display = f"{title} - {artist}"
                full_url = f"https://www.gequhai.net{href}"

                self.song_map[display] = (title, song_id, full_url)
                self.result_combo.addItem(display)

            if self.song_map:
                self.status_label.setText(f"找到 {len(self.song_map)} 首歌曲")
            else:
                self.status_label.setText("未找到歌曲")
                # self.status_label.setText("未找到歌曲, 开始尝试搜索gequhai.com")    # deprecated
                # search_url = f"https://www.gequhai.com/s/{keyword}"
                # self.driver.get(search_url)
                # # 等待列表出现
                # WebDriverWait(self.driver, 10).until(
                #     EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-8.col-content a.music-link"))
                # )

                # soup = BeautifulSoup(self.driver.page_source, "html.parser")

                # links = soup.select("div.col-8.col-content a.music-link")

                # self.result_combo.clear()
                # self.song_map.clear()

                # for a in links:
                #     title = a.get_text(strip=True)
                #     href  = a["href"]                      # "/music/4190"
                #     song_id = href.rsplit("/", 1)[-1]      # "4190"

                #     row = a.find_parent("div", class_="row")
                #     artist_div = row.select_one("div.col-4.col-content")
                #     artist = artist_div.get_text(strip=True) if artist_div else ""

                #     display = f"{title} - {artist}"
                #     full_url = f"https://www.gequhai.com{href}"

                #     self.song_map[display] = (title, song_id, full_url)
                #     self.result_combo.addItem(display)
                #     if self.song_map:
                #         self.status_label.setText(f"找到 {len(self.song_map)} 首歌曲")
                #     else:
                #         self.status_label.setText("未找到歌曲")

        except Exception as e:
            self.status_label.setText(f"搜索失败: {e}")
            QMessageBox.warning(self, "错误", f"搜索失败：{e}")


    # def play_selected(self):
    #     selected = self.result_combo.currentText()
    #     if not selected or selected not in self.song_map:
    #         self.status_label.setText("请先选择歌曲")
    #         return

    #     _, song_id, _ = self.song_map[selected]
    #     play_url = self.get_mp3_url_via_page(song_id)
    #     if not play_url:
    #         self.status_label.setText("获取播放链接失败")
    #         return

    #     try:
    #         if self.player.is_playing():
    #             self.player.stop()

    #         media = self.vlc_instance.media_new(play_url)
    #         self.player.set_media(media)
    #         self.player.play()
    #         self.status_label.setText(f"正在播放: {selected}")

    #     except Exception as e:
    #         self.status_label.setText(f"播放失败: {e}")
    #         QMessageBox.warning(self, "播放错误", f"无法播放歌曲: {e}")

    def download_selected(self):
        selected = self.result_combo.currentText()
        if not selected or selected not in self.song_map:
            self.status_label.setText("请先选择歌曲")
            return

        title, song_id, _ = self.song_map[selected]
        play_url = self.get_mp3_url_via_page(song_id)
        if not play_url:
            self.status_label.setText("获取下载链接失败")
            return

        # 自动根据 URL 后缀识别扩展名
        parsed = urlparse(play_url)
        path = unquote(parsed.path)
        _, ext = os.path.splitext(path)
        if not ext:
            ext = '.mp3'
        filename = f"{title}{ext}"
        safe_name = "".join(c for c in filename if c not in r'\/:*?"<>|')
        file_path = os.path.join(self.save_folder, safe_name)

        try:
            self.status_label.setText(f"正在下载: {title}{ext}，请稍候...")
            QApplication.processEvents()

            # 下载歌曲
            r = requests.get(play_url, stream=True)
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # 下载专辑封面
            cover_url = self.get_album_cover_url(song_id)
            if cover_url:
                cover_filename = f"{title}.jpg"
                safe_cover_name = "".join(c for c in cover_filename if c not in r'\/:*?"<>|')
                cover_path = os.path.join(self.save_folder, safe_cover_name)

                r_cover = requests.get(cover_url, stream=True)
                r_cover.raise_for_status()
                with open(cover_path, 'wb') as f_cover:
                    for chunk in r_cover.iter_content(chunk_size=8192):
                        if chunk:
                            f_cover.write(chunk)


            self.status_label.setText(f"下载完成: {file_path}")
            QMessageBox.information(self, "下载完成", f"已保存到: {file_path}")

        except Exception as e:
            self.status_label.setText(f"下载失败: {e}")
            QMessageBox.warning(self, "下载错误", f"无法下载歌曲: {e}")

    # def get_cookies_as_string(self, song_id): # deprecated
    #     self.init_driver()
    #     self.driver.get(f'https://www.gequhai.com/play/{song_id}')
    #     time.sleep(2)

    #     cookies = self.driver.get_cookies()
    #     cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])

    #     print(f"提取到 Cookie：{cookie_str}")
    #     return cookie_str
    
    # def get_mp3_url(self, song_id): # 403forbidden
    #     api_url = 'https://www.gequhai.com/api/music'
    #     cookie_str = self.get_cookies_as_string('https://www.gequhai.com/play/{song_id}')
        
    #     headers = {
    #         'Accept': 'application/json, text/javascript, */*; q=0.01',
    #         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    #         'Referer': f'https://www.gequhai.com/play/{song_id}',
    #         'Origin': 'https://www.gequhai.com',
    #         'X-Requested-With': 'XMLHttpRequest',
    #         'Accept-Encoding': 'identity',
    #         'Cookie': cookie_str
    #     }


    #     data = {'id': song_id}

    #     try:
    #         resp = requests.post(api_url, headers=headers, data=data)
    #         resp.raise_for_status()
    #         json_data = resp.json()
    #         if json_data.get('code') == 200 and 'url' in json_data.get('data', {}):
    #             mp3_url = json_data['data']['url'].replace('\\/', '/')
    #             print(f"找到 mp3 链接：{mp3_url}")
    #             return mp3_url
    #         else:
    #             print(f"API 返回异常：{json_data}")
    #     except Exception as e:
    #         print(f"获取 mp3 链接失败: {e}")

    #     return None

    # def get_album_cover_url(self, song_id):
    #     try:
    #         self.init_driver()
    #         page_url = f'https://www.gequhai.com/play/{song_id}'
    #         self.driver.get(page_url)

    #         # 等待 .aplayer-pic 出现
    #         wait = WebDriverWait(self.driver, 10)
    #         pic_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "aplayer-pic")))

    #         # 1) style.background-image 
    #         cover_style = pic_div.value_of_css_property("background-image")
    #         if cover_style and cover_style != "none":
    #             m = re.match(r'url\(["\']?(.*?)["\']?\)', cover_style)
    #             if m:
    #                 cover_url = m.group(1)
    #                 print(f"通过 aplayer-pic style 拿到封面链接：{cover_url}")
    #                 return cover_url

    #         # 2) fallback: <meta property="og:image">
    #         cover_url = self.driver.execute_script("""
    #             let m = document.querySelector('meta[property="og:image"]');
    #             return m ? m.content : null;
    #         """)
    #         if cover_url:
    #             print(f"通过 meta 标签拿到封面链接：{cover_url}")
    #             return cover_url

    #         # 3) fallback: APlayer 全局变量
    #         cover_url = self.driver.execute_script("""
    #             try { return ap.list.audios[0].cover } catch(e) { return null }
    #         """)
    #         if cover_url:
    #             print(f"通过 APlayer 全局变量拿到封面链接：{cover_url}")
    #             return cover_url

    #         print("页面中未找到封面链接")
    #     except Exception as e:
    #         print(f"Selenium 抓取封面链接失败: {e}")

    #     return None

    def get_album_cover_url(self, song_id):
        try:
            self.init_driver()
            page_url = f'https://www.gequhai.net/music/{song_id}'
            self.driver.get(page_url)

            # 等待 .aplayer-pic 出现
            wait = WebDriverWait(self.driver, 10)
            pic_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".aplayer-pic")))

            # 1) 从 style 属性里解析 background-image
            style_attr = pic_div.get_attribute("style") or ""
            m = re.search(r'background-image\s*:\s*url\(\s*["\']?(.*?)["\']?\s*\)', style_attr, re.IGNORECASE)
            if m:
                cover_url = m.group(1)
                print(f"通过 style 属性拿到封面链接：{cover_url}")
                return cover_url

            # 2) fallback: <meta property="og:image">
            cover_url = self.driver.execute_script("""
                const m = document.querySelector('meta[property="og:image"]');
                return m ? m.getAttribute('content') : null;
            """)
            if cover_url:
                print(f"通过 meta 拿到封面链接：{cover_url}")
                return cover_url

            # 3) 再 fallback: APlayer 全局变量
            cover_url = self.driver.execute_script("""
                try { return ap.list.audios[0].cover } catch(e) { return null; }
            """)
            if cover_url:
                print(f"通过 APlayer 全局变量拿到封面链接：{cover_url}")
                return cover_url

            print("页面中未找到封面链接")
        except Exception as e:
            print(f"Selenium 抓取封面链接失败: {e}")

        return None

    def get_mp3_url_via_page(self, song_id):
        try:
            self.init_driver()
            page_url = f'https://www.gequhai.net/music/{song_id}'
            self.driver.get(page_url)
            time.sleep(2)

            # #  <audio> 标签 ### 无效
            # play_url = self.driver.execute_script("""
            #     let audio = document.querySelector('audio');
            #     return audio ? audio.src : null;
            # """)
            # if play_url:
            #     print(f"页面直接找到 <audio> 播放链接：{play_url}")
            #     return play_url
            
            # APlayer 全局变量
            play_url = self.driver.execute_script("""
                try {
                    return ap.list.audios[0].url;
                } catch (e) {
                    return null;
                }
            """)
            if play_url:
                print(f"通过 APlayer 全局变量找到链接：{play_url}")
                return play_url

            print("页面中未找到可用的 mp3 链接")
        except Exception as e:
            print(f"Selenium 抓取 mp3 链接失败: {e}")

        return None

    def stop_playing(self):
        if self.player.is_playing():
            self.player.stop()
            self.status_label.setText("播放已停止")

    def closeEvent(self, event):
        if self.driver:
            self.driver.quit()
        event.accept()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     try:
#         vlc.Instance()
#     except:
#         QMessageBox.critical(None, "错误", "未找到VLC播放器，请先安装VLC")
#         sys.exit(1)

#     window = GeQuHaiPlayer()
#     window.show()
#     sys.exit(app.exec_())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 要测试的歌曲链接
    # test_url = 'https://www.gequhai.com/play/139'
    test_url = 'https://www.gequhai.net/music/4190'
    song_id = test_url.strip('/').split('/')[-1]

    # 初始化下载器实例（不启动 UI）
    player = GeQuHaiPlayer()

    # 获取 mp3 链接
    play_url = player.get_mp3_url_via_page(song_id)
    if play_url:
        print(f"准备下载：{play_url}")

        # 文件保存位置
        file_path = os.path.join(player.save_folder, f"{song_id}.mp3")
        try:
            r = requests.get(play_url, stream=True)
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"下载完成：{file_path}")
        except Exception as e:
            print(f"下载失败: {e}")
    else:
        print("未获取到 mp3 链接，无法下载。")
