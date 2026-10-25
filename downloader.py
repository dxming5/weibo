from urllib import request
import os
import socket

from config import DOWNLOAD_TIMEOUT, MAX_RETRY
import storage
import util
import fetcher


def save_single_url(url, file_name):
    """下载单个文件，超过 MAX_RETRY 次失败则跳过返回 False"""
    # 下载超时设置，防止线程堵塞（全局默认超时，设一次即对本次下载全程生效）
    socket.setdefaulttimeout(DOWNLOAD_TIMEOUT)
    i = 0
    while True:
        util.time_interval("download")
        if i > MAX_RETRY:
            util.print_message("    -->当前url({})下载异常次数超过{}次，跳过！".format(url, MAX_RETRY))
            return False
        try:
            request.urlretrieve(url, file_name)
            return True
        except Exception:
            i += 1


# 每累计下载该数量的 url 就落盘一次，兼顾 I/O 次数与崩溃安全性
FLUSH_THRESHOLD = 100


def download_by_type(all_url_dict, blogger_url_txt_dir, blogger_dir, kind):
    """根据类型下载 dict 中的所有 url，已下载的自动跳过（增量更新）。
    进度按"文件总数"计算（每条微博可能含多张图片/多个视频），每处理完一个文件进度 +1。"""
    saved_url_set = set(storage.read_lines(blogger_url_txt_dir))  # set 查重 O(1)，并顺带对历史文件去重
    all_mblog_num = len(all_url_dict)
    # 文件总数 = 所有微博对应 url 列表长度之和，用于精确计算下载进度
    total_files = sum(len(url_mblog) for url_mblog in all_url_dict.values())
    if all_mblog_num:
        classifier = '张' if kind == '图片' else '条'
        downloaded_files = 0  # 已处理的文件数（含跳过的已下载项）
        new_urls = []  # 待落盘的 url 缓冲，满 FLUSH_THRESHOLD 个写一次
        for create_time, url_mblog in all_url_dict.items():
            for index in range(0, len(url_mblog)):
                url = url_mblog[index]
                file_name = ''
                if kind == '图片':
                    file_name = os.path.join(blogger_dir, create_time + ' - ' + str(index + 1) + '.jpg')
                elif kind == 'live':
                    file_name = os.path.join(blogger_dir, create_time + ' - ' + str(index + 1) + '.mov')
                elif kind == '视频':
                    file_name = os.path.join(blogger_dir, create_time + ' - ' + str(index + 1) + '.mp4')
                    # 视频 url 是动态的，使用 "https......mp4" 前缀字符串来存储比较
                    mp4_index = url.find('mp4')
                    if mp4_index != -1:  # 找不到 mp4 时用完整 url 作去重键，避免截断成前两个字符
                        url = url[0:(mp4_index + 3)]
                # 注意：下载用完整 url（url_mblog[index]），去重/落盘用截断后的 url
                if url not in saved_url_set and save_single_url(url_mblog[index], file_name):
                    saved_url_set.add(url)
                    new_urls.append(url)
                    if len(new_urls) >= FLUSH_THRESHOLD:
                        with open(blogger_url_txt_dir, mode='a', encoding='utf-8') as f:
                            f.write('\n'.join(new_urls) + '\n')
                        new_urls = []
                downloaded_files += 1
                percent = int(downloaded_files / total_files * 100) if total_files else 100
                util.print_progress('开始下载<{}>时刻第{}{}{} [{}已下载进度：{}%({}/{})]'.format(
                    create_time, index + 1, classifier, kind, kind,
                    percent, downloaded_files, total_files))
        if new_urls:  # 收尾把不足一批的剩余 url 落盘
            with open(blogger_url_txt_dir, mode='a', encoding='utf-8') as f:
                f.write('\n'.join(new_urls) + '\n')
        util.print_progress('[{}已下载完成]'.format(kind), end='\n')
       


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
