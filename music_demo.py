import requests
import gequhai
import os
import time
from urllib import parse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

"""
可以搜索歌手，以及批量下载搜索到的所有音乐
1.把上一个文件当成模块导入
2.准备好歌手的名字
3.先创建一个歌手的文件夹，用导入模块的gequhai.mk_dir函数来创建
4. get_main_page方法：
    1.先拼接搜索歌手主页，需要把汉字编码，然后转换成%形式的字符串，然后拼接
    2.看看一共搜索出了多少页
    3.获取每一页的地址
    4.再通过每一页的地址获取所有歌曲的名字和歌曲地址，有歌曲地址就可以用多线程和导入的上一个py文件批量下载了
5.thread_download开始多线程下载，使用gequhai模块下载单曲
6.检查所有歌曲是不是都下载了
后记：
    1.有的歌曲名字里面有不可命名的非法字符，需要用replace('\\', '')替换掉
    2.有个歌曲下了个空文件，下载完后，应该判断文件大小是不是为0，如果是0，再递归下载这首歌曲    
    3.也可以再进一步更改代码，实现可以选择歌曲下载
    4.自己编的模块真是好用，可以随时修改，也避免了一个py文件中代码臃肿的情况
"""


class Application:
    def __init__(self, *args):
        self.url = 'https://www.gequhai.com/'
        self.name = args[0]
        self.dic = {}  # 接受所有的歌曲和链接
        self.lst = []  # 接受下载失败的文件名称
        self.i = 0
        self.j = 0
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'
        }

    def get_main_page(self):
        n = parse.quote(self.name).strip()
        main_url = self.url + 's/' + n
        resp = requests.get(url=main_url, headers=self.headers)
        resp.close()
        # print(resp.text)
        bs = BeautifulSoup(resp.text, 'html.parser')
        # a_lst = bs.find_all('a', class_='music-link d-block')
        a_lst1 = bs.find_all('a', class_='page-link')
        # print(a_lst1)
        for a in a_lst1:
            if a.text != '尾页':
                continue
            else:
                num = int(a.get('href').split('=')[1])
                # print(num + 1, type(num))
        for i in range(1, num + 1):
            params = {'page': str(i)}
            resp = requests.get(url=main_url, params=params, headers=self.headers)
            resp.close()
            # print(resp.text)
            bs = BeautifulSoup(resp.text, 'html.parser')
            a_lst = bs.find_all('a', class_='text-info font-weight-bold')
            # print(a_lst)
            for a in a_lst:
                na = a.text.strip().replace('\\', '').replace('/', '')
                url = self.url + a.get('href')
                self.dic[na] = url
            time.sleep(3)
        print(len(self.dic))
        print(self.dic)

    def thread_download(self):
        self.i += 1
        with ThreadPoolExecutor(10) as t:
            for k, v in self.dic.items():
                t.submit(self.download, url=v)
        print(f'第{self.i}次多线程下载完成！')

    def download(self, url):
        self.j += 1
        print(f'正在下载第{self.j}首歌曲=======')
        app1 = gequhai.Application(url, self.name)
        app1.main()

    def check(self):
        for n in self.dic.keys():
            if not os.path.isfile(f'{self.name}/{n}.mp3'):
                self.lst.append(n)
        if self.lst:
            print(self.lst)
            self.i += 1
            with ThreadPoolExecutor(10) as t:
                for m in self.lst:
                    t.submit(self.download, url=self.dic[m])
            print(f'第{self.i}次多线程下载完成！')
            self.lst = []
            self.check()
        else:
            print('全部下载完成！！！')

    def main(self):
        self.get_main_page()
        self.thread_download()
        # self.check()


if __name__ == '__main__':
    name = input("请输入歌手名字：").strip()
    gequhai.mk_dir(name)
    app = Application(name)
    app.main()

