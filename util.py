import time
import random

from config import IS_TIME_INTERVAL, MAX_RETRY


def time_interval(kind):
    """反爬时间间隔：get_page 1~2s / download 0~0.5s / update_all 3s"""
    if not IS_TIME_INTERVAL:
        return
    gap = 0
    if kind == "get_page":       # 获取页面间隔 1~2s
        gap = 1 + random.random()
    elif kind == "download":     # 下载间隔 0~0.5s
        gap = 0.5 * random.random()
    elif kind == "update_all":   # 更新所有博主间隔 3s
        gap = 3
    if gap:
        time.sleep(gap)


# 英文月份 -> 两位数字
_MONTHS = {
    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12',
}


def month_eng_to_num(month_eng):
    return _MONTHS.get(month_eng, '00')


def print_progress(msg, end=''):
    """进度打印：\r 回到行首，\033[K 清除到行尾的残留字符。
    相比用空格补齐，不会在行尾留下可见空白，也不会出现短行覆盖长行时残留尾巴的问题。"""
    print('\r' + msg + '\033[K', end=end)


def print_message(msg):
    """打印一条独立消息（错误/提示）：先换行离开当前进度行，再打印消息并换行，
    使后续 print_progress 从全新的一行开始，避免与 \r 进度行互相覆盖残留。"""
    print()
    print(msg)
