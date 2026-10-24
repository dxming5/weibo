import os
import shutil

from config import DOWNLOAD_DIR

BLOGGER_LIST_TXT = os.path.join(DOWNLOAD_DIR, 'bloggerlist.txt')


def ensure_root():
    """创建下载根目录与博主列表文件"""
    make_dir(DOWNLOAD_DIR)
    make_txt(BLOGGER_LIST_TXT)


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def make_txt(path):
    # 以追加模式打开并立即关闭：文件不存在则创建空文件，存在则不动
    open(path, mode='a', encoding='utf-8').close()


def rm_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def read_lines(path):
    """按行读取，返回去除换行符的非空行列表"""
    lines = []
    with open(path, mode='r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n').rstrip('\r')
            if line:
                lines.append(line)
    return lines


def append_line(path, text):
    with open(path, mode='a', encoding='utf-8') as f:
        f.write(text + '\n')


def write_lines(path, lines):
    """覆盖写入列表（用于删除博主后回写 bloggerlist.txt）"""
    with open(path, mode='w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')


def blogger_paths(blogger_name):
    """返回某博主相关的所有路径字典"""
    base = os.path.join(DOWNLOAD_DIR, blogger_name)
    return {
        'dir': base,
        'picture': os.path.join(base, 'picture_url.txt'),
        'live': os.path.join(base, 'live_url.txt'),
        'video': os.path.join(base, 'video_url.txt'),
    }
