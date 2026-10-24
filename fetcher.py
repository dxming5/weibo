from urllib import request
import ssl
import json

from config import COOKIE, BLOGGER_MAX_NUM, MAX_RETRY
import util

header = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36 Edg/134.0.0.0',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://m.weibo.cn/',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': COOKIE,
}

context = ssl._create_unverified_context()


def get_all_url(blogger_url):
    """翻页获取某博主所有图片/live/视频 URL。
    返回三个字典：key=微博发布时间，value=该条微博的 url 列表。
    连续异常超过 MAX_RETRY 次时跳过该博主（不再 exit 整个程序）。"""
    all_picture_url_dict = dict()
    all_live_url_dict = dict()
    all_video_url_dict = dict()
    since_id = '0'
    for page in range(1, 1000):
        num = MAX_RETRY
        for i in range(0, num + 1):
            util.time_interval("get_page")
            if i == num:
                print("\n    -->当前博主({})获取异常次数超过{}次，跳过该博主！".format(blogger_url, num))
                return all_picture_url_dict, all_live_url_dict, all_video_url_dict
            if BLOGGER_MAX_NUM != 0 and BLOGGER_MAX_NUM < len(all_picture_url_dict):
                print('\r [已获取图片微博：%d条；live微博：%d条；视频微博：%d条]' % (
                    len(all_picture_url_dict), len(all_live_url_dict), len(all_video_url_dict)))
                print()
                return all_picture_url_dict, all_live_url_dict, all_video_url_dict
            try:
                real_url = blogger_url + "&since_id=" + since_id
                print('\r [已获取图片微博：%d条；live微博：%d条；视频微博：%d条] 开始获取第%d页' % (
                    len(all_picture_url_dict), len(all_live_url_dict), len(all_video_url_dict), page), end='')
                req = request.Request(url=real_url, headers=header)
                resp = request.urlopen(req, context=context).read().decode()
                resp_json = json.loads(resp)

                for key_cards in resp_json['data']['cards']:  # 每条微博开始获取 url
                    # 仅处理 card_type=9 且含 mblog 的微博卡片，其余（分组/广告/置顶等）直接跳过
                    if key_cards.get('card_type') != 9 or 'mblog' not in key_cards:
                        continue
                    create_time_ori = key_cards['mblog']['created_at']
                    # 2023-04-21 00.00.00
                    create_time = create_time_ori[26:31] + '-' + util.month_eng_to_num(create_time_ori[4:7]) + '-' + create_time_ori[8:10] + ' ' \
                                  + create_time_ori[11:13] + '.' + create_time_ori[14:16] + '.' + create_time_ori[17:19]
                    picture_url_mblog = []  # 记录每条微博图片 url
                    live_url_mblog = []     # 记录每条微博 live url
                    video_url_mblog = []    # 记录每条微博视频 url
                    # 每条微博图片 url 获取
                    if 'pics' in key_cards['mblog']:
                        if type(key_cards['mblog']['pics']) == list:
                            for pics_url in key_cards['mblog']['pics']:
                                picture_url_mblog.append(pics_url['large']['url'].replace('\/', '/'))
                        elif type(key_cards['mblog']['pics']) == dict:
                            j = 0
                            while True:
                                if str(j) in key_cards['mblog']['pics']:
                                    picture_url_mblog.append(key_cards['mblog']['pics'][str(j)]['large']['url'].replace('\/', '/'))
                                    j += 1
                                else:
                                    break

                    # 每条微博 live url 获取
                    if 'live_photo' in key_cards['mblog']:
                        for live_photo_url in key_cards['mblog']['live_photo']:
                            live_url_mblog.append(live_photo_url.replace('\/', '/'))

                    # 每条微博视频 url 获取
                    if 'page_info' in key_cards['mblog'] \
                            and 'urls' in key_cards['mblog']['page_info'] \
                            and type(key_cards['mblog']['page_info']['urls']) == dict \
                            and 'mp4_720p_mp4' in key_cards['mblog']['page_info']['urls']:
                        video_url_mblog.append(key_cards['mblog']['page_info']['urls']['mp4_720p_mp4'].replace('\/', '/'))

                    if picture_url_mblog:
                        all_picture_url_dict[create_time] = picture_url_mblog
                    if live_url_mblog:
                        all_live_url_dict[create_time] = live_url_mblog
                    if video_url_mblog:
                        all_video_url_dict[create_time] = video_url_mblog

                # 若当页 json 中无 since_id，表示已无下一页
                if 'cardlistInfo' not in resp_json['data'] or 'since_id' not in resp_json['data']['cardlistInfo']:
                    print('\r [已获取图片微博：%d条；live微博：%d条；视频微博：%d条]' % (
                        len(all_picture_url_dict), len(all_live_url_dict), len(all_video_url_dict)))
                    print()
                    return all_picture_url_dict, all_live_url_dict, all_video_url_dict
                since_id = str(resp_json['data']['cardlistInfo']['since_id'])
                break
            except Exception as error:
                print('\n     error: ', end='')
                print(error)
                print('     -->异常导致重新获取第' + str(page) + '页的URL')
    return all_picture_url_dict, all_live_url_dict, all_video_url_dict
