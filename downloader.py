from urllib import request
import os
import socket

from config import DOWNLOAD_TIMEOUT, MAX_RETRY
import storage
import util
import fetcher


def save_single_url(url, file_name):
    """下载单个文件，超过 MAX_RETRY 次失败则跳过返回 False"""
    i = 0
    while True:
        util.time_interval("download")
        if i > MAX_RETRY:
            print("\n    -->当前url({})下载异常次数超过{}次，跳过！".format(url, MAX_RETRY))
            return False
        try:
            # 下载超时设置，防止线程堵塞
            socket.setdefaulttimeout(DOWNLOAD_TIMEOUT)
            request.urlretrieve(url, file_name)
            return True
        except Exception:
            i += 1


def download_by_type(all_url_dict, blogger_url_txt_dir, blogger_dir, kind):
    """根据类型下载 dict 中的所有 url，已下载的自动跳过（增量更新）"""
    saved_url_list = storage.read_lines(blogger_url_txt_dir)
    all_mblog_num = len(all_url_dict)
    if all_mblog_num:
        download_mblog_num = 0
        for create_time, url_mblog in all_url_dict.items():
            for index in range(0, len(url_mblog)):
                url = url_mblog[index]
                print('\r [{}已下载进度：{}%({}/{})] 开始下载<{}>时刻第{}张(条){}：{}'.format(
                    kind, int(download_mblog_num / all_mblog_num * 100), download_mblog_num,
                    all_mblog_num, create_time, index + 1, kind, url), end='')
                file_name = ''
                if kind == '图片':
                    file_name = os.path.join(blogger_dir, create_time + ' - ' + str(index + 1) + '.jpg')
                elif kind == 'live':
                    file_name = os.path.join(blogger_dir, create_time + ' - ' + str(index + 1) + '.mov')
                elif kind == '视频':
                    file_name = os.path.join(blogger_dir, create_time + ' - ' + str(index + 1) + '.mp4')
                    # 视频 url 是动态的，使用 "https......mp4" 前缀字符串来存储比较
                    mp4_index = url.find('mp4')
                    url = url[0:(mp4_index + 3)]
                if url not in saved_url_list and save_single_url(url_mblog[index], file_name):
                    saved_url_list.append(url)
                    storage.append_line(blogger_url_txt_dir, url)
            download_mblog_num += 1
            print('\r [{}已下载进度：{}%({}/{})]'.format(kind, int(download_mblog_num / all_mblog_num * 100),
                                                          download_mblog_num, all_mblog_num), end='')
        print()


def download(blogger_name, blogger_url):
    """下载某博主的图片 / live / 视频"""
    paths = storage.blogger_paths(blogger_name)
    storage.make_dir(paths['dir'])
    print('*' * 20 + ' <blogger：' + blogger_name + '> ' + '*' * 20)
    all_picture_dict, all_live_dict, all_video_dict = fetcher.get_all_url(blogger_url)

    # 下载图片
    download_by_type(all_picture_dict, paths['picture'], paths['dir'], '图片')
    # 下载 live
    download_by_type(all_live_dict, paths['live'], paths['dir'], 'live')
    # 下载视频
    download_by_type(all_video_dict, paths['video'], paths['dir'], '视频')

    print('*' * 45 + '\n')
