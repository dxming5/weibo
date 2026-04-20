from urllib import request
import re
import ssl
import os
import shutil
import time
import random
import socket
import json
# 爬取微博图片
# weibo_v1 获取多页图片
# weibo_v2 添加当页图片url获取函数，缩短代码
# weibo_v3 优化获取有效页面数
# weibo_v4 添加当页图片保存函数，缩短代码
# weibo_v5
    # 1.从最后一页开始存储图片，直至第一页
    # 2.记录已下载图片张数
    # 3.第一次输入的blogger写入到文本文档bloglist.txt
    # 4.新增：一次更新txt所有blog的图片
# weibo_v6 修复v5版本try之后find_page重复增加问题
    # 不使用find_page和cur_page全局变量
    # 新增文本文档txt，保存已所有下载图片的url（此方法耗时和空间），但是目前唯一确保不会楼下图片
# weibo_v7
    # 修复v6远程断开之后，存储名称异常问题
# weibo_v8
    # 去除页的概念，一次获取所有的图片/视频url，并与保存的url比较：不在保存列表中，下载图片；否则跳过
    # 下载超时设置
# weibo_v9
    # 获取所有url时，当页获取失败，重新获取当页，而非所有页重新获取
# weibo_v10
    # 剔除视频下载：图片使用weibo下载，视频使用douyin下载
# weibo_v11
    # 重构图片url获取，并下载live图片
# weibo_v12
    #
# weibo_v13
    # 以微博时间为单位进行记录，非单个url记录
# weibo_v14
    # 微博最大只下载500条左右
blogger_max_num = 0 # 0是不启用最大限制
# weibo_v15
    # 添加是否启用时间间隔（避免反爬机制）：获取页面间隔、下载间隔、更新所有博主间隔
is_time_interval = True  # 是否启用时间间隔
def  time_interval(type):
    if is_time_interval:
        time_interval = 0
        if "get_page" == type: #获取页面间隔1~2s
            time_interval = 1 + random.random()
        elif "download" == type: #下载间隔0~0.5s
            time_interval = 0.5 * random.random()
        elif "update_all" == type: #更新所有博主时间隔3s
            time_interval = 3

        if 0 != time_interval:
            time.sleep(time_interval)



header = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36 Edg/134.0.0.0',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://m.weibo.cn/'
}

context = ssl._create_unverified_context()

# 目录结构如下
# /blog/
#       /bloglist.txt （记录所有blogger的名字和url）
#       /blogger/（每个blogger都是一个文件夹）
#                /（所有图片）
#                /picture_url.txt（记录已下载图片的url）

'''
{
    "data": {
        "cards": [ //每一条微博是一个元素
            {
                "card_type": 9, //表示是否是微博动态
                "mblog": {
                    "pic_num": 9, //一条微博图片数量
                    "created_at": "Tue Apr 25 14:07:58 +0800 2023", //微博发布时间
                    "pics": [ //一条微博图片列表(也可能是字典)
                        {
                            "large": {
                                "url": "https:\/\/wx2.sinaimg.cn\/large\/0077dnqEgy1h8pk5ocdn5j30zu0k2qfu.jpg"
                            }
                        },
                        {
                            "large": {
                                "url": "https:\/\/wx1.sinaimg.cn\/large\/0077dnqEgy1h8pk5nhdiyj32c0340e84.jpg"
                            }
                        }
                        ......
                    ],
                    "live_photo": [ //一条微博live列表：不一定存在
                        "https:\/\/video.weibo.com\/media\/play?livephoto=https%3A%2F%2Flivephoto.us.sinaimg.cn%2F003lp1UYgx081eXLvLtm0f0f0100oU2X0k01.mov",
                        "https:\/\/video.weibo.com\/media\/play?livephoto=https%3A%2F%2Flivephoto.us.sinaimg.cn%2F001jLzxJgx081eY5Pua30f0f0100loKc0k01.mov"
                    ]
                    "page_info": { //一条微博视频：不一定存在
                        "urls": {
                            "mp4_720p_mp4": "https://f.video.weibocdn.com/o0/OvaNt8oQlx085cEnX05O01041200CFBa0E010.mp4?label=mp4_720p&template=720x1280.24.0&ori=0&ps=1CwnkDw1GXwCQx&Expires=1683465938&ssig=hVqu0cIcpp&KID=unistore,video",
                            }
                    },
                }
            }
            ......
        ]
    }
}
'''

# 如下为全局变量
download_dir  = ''
blogger_list_txt_dir = ''
blogger_download_dir = ''
blogger_picture_url_txt_dir = ''
blogger_live_url_txt_dir = ''
blogger_video_url_txt_dir = ''

#设置总目录路径
def set_total_path():
    path_mode = '1'
    #path_mode = input("  0:相对路径；1:绝对路径：")
    global download_dir
    while True:
        if path_mode == '0':
            download_dir = './blog/'
            break
        elif path_mode == '1':
            download_dir = 'F:/图片/blog/'
            # download_dir = input("请输入绝对路径：")
            break
        else:
            print("选择路径指令错误，请重新输入！")
    make_dir(download_dir)
    global blogger_list_txt_dir
    blogger_list_txt_dir = download_dir + 'bloggerlist.txt'
    make_txt(blogger_list_txt_dir)

#设置子目录路径
def set_sub_path(blogger_name):
    global blogger_download_dir
    blogger_download_dir = download_dir + blogger_name + '/'
    make_dir(blogger_download_dir)
    global blogger_picture_url_txt_dir
    blogger_picture_url_txt_dir = download_dir + blogger_name + '/picture_url.txt'
    make_txt(blogger_picture_url_txt_dir)
    global blogger_live_url_txt_dir
    blogger_live_url_txt_dir = download_dir + blogger_name + '/live_url.txt'
    make_txt(blogger_live_url_txt_dir)
    global blogger_video_url_txt_dir
    blogger_video_url_txt_dir = download_dir + blogger_name + '/video_url.txt'
    make_txt(blogger_video_url_txt_dir)

def make_dir(dir):
    if not  os.path.exists(dir):
        os.makedirs(dir)
def make_txt(txt_str):
    file_handle = open(txt_str, mode='a')
    file_handle.close()

def rm_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)

#以每一行格式读取txt文档，返回一个列表
def read_txt(txt_dir):
    txt_list = []
    file_handle = open(txt_dir, mode='r')
    while True:
        line = file_handle.readline().splitlines()
        if line:
            #print(line[0])
            txt_list.append(line[0])
        else:
            break
    file_handle.close()
    return txt_list

#追加写一行到txt文档
def write_txt(txt_dir, str):
    file_handle = open(txt_dir, mode = 'a')
    file_handle.write(str + '\n')
    file_handle.close()

def write_list_txt(txt_dir, list, length):
    file_handle = open(txt_dir, mode='w')
    for index in range(0,length):
        file_handle.write(list[index]+'\n')
    file_handle.close()

def month_eng_to_num(month_eng):
    if month_eng == 'Jan':
        return '01'
    elif month_eng == 'Feb':
        return '02'
    elif month_eng == 'Mar':
        return '03'
    elif month_eng == 'Apr':
        return '04'
    elif month_eng == 'May':
        return '05'
    elif month_eng == 'Jun':
        return '06'
    elif month_eng == 'Jul':
        return '07'
    elif month_eng == 'Aug':
        return '08'
    elif month_eng == 'Sep':
        return '09'
    elif month_eng == 'Oct':
        return '10'
    elif month_eng == 'Nov':
        return '11'
    elif month_eng == 'Dec':
        return '12'
    else:
        return '00'

def get_all_url(blogger_url):
    # 记录所有图片的url：字典结构，key=微博发布时间，value=每条微博中图片的url list
    all_picture_url_dict = dict()
    # 记录所有live的url：字典结构，key=微博发布时间，value=每条微博中live的url list
    all_live_url_dict = dict()
    # 记录所有视频的url：字典结构，key=微博发布时间，value=每条微博中视频的url list
    all_video_url_dict = dict()
    since_id = '0'
    for page in range(1, 1000):
        # 重新获取次数
        num = 3
        for i in range(0, 4):
            time_interval("get_page")
            # 最多获取三次，否则退出
            if i == num:
                print("\n    -->当前url({})获取异常次数超过{}次，退出下载！".format(real_url, num))
                exit()
            if blogger_max_num != 0 and blogger_max_num < len(all_picture_url_dict):
                print('\r [已获取图片微博：%d条；live微博：%d条；视频微博：%d条]' % (len(all_picture_url_dict), len(all_live_url_dict), len(all_video_url_dict)))
                print()
                return all_picture_url_dict, all_live_url_dict, all_video_url_dict
            try:
                real_url = blogger_url + "&since_id=" + since_id
                print('\r [已获取图片微博：%d条；live微博：%d条；视频微博：%d条] 开始获取第%d页URL：%s ' %
                      (len(all_picture_url_dict), len(all_live_url_dict), len(all_video_url_dict), page, real_url), end='')
                req = request.Request(url=real_url, headers=header)
                resp = request.urlopen(req, context=context).read().decode()
                resp_json = json.loads(resp)
                #print(resp_json)

                # 若当页'ok':0，表示已无视频，返回结果
                #if not resp_json['ok']:
                #    print('\n 当前第%d页是最后一页：共获取图片微博%d条，live微博%d条，视频微博%d条' % (
                #          page, len(all_picture_url_dict), len(all_live_url_dict), len(all_video_url_dict)))
                #    print()
                #    return all_picture_url_dict, all_live_url_dict, all_video_url_dict
                #    print('\n 所有url获取完成！')

                for key_cards in resp_json['data']['cards']: #每条微博开始获取url
                    create_time_ori = key_cards['mblog']['created_at']
                    # 2023-04-21 00.00.00
                    create_time = create_time_ori[26:31] + '-' + month_eng_to_num(create_time_ori[4:7]) + '-' + create_time_ori[8:10] + ' ' \
                                  + create_time_ori[11:13] + '.' + create_time_ori[14:16] + '.' + create_time_ori[17:19]
                    #print(create_time)
                    picture_url_mblog = [] # 记录每条微博图片url
                    live_url_mblog = [] # 记录每条微博live url
                    video_url_mblog = [] # 记录每条微博视频 url
                    if key_cards['card_type'] != 9:
                        continue
                    else:
                        if 'mblog' not in key_cards:
                            continue
                        # 每条微博图片url获取
                        if 'pics' in key_cards['mblog']:
                            if type(key_cards['mblog']['pics']) == list:
                                for pics_url in key_cards['mblog']['pics']:
                                    picture_url_mblog.append(pics_url['large']['url'].replace('\/', '/'))
                            elif type(key_cards['mblog']['pics']) == dict:
                                i = 0
                                while True:
                                    if str(i) in key_cards['mblog']['pics']:
                                        picture_url_mblog.append(key_cards['mblog']['pics'][str(i)]['large']['url'].replace('\/', '/'))
                                        i += 1
                                    else:
                                        break

                        # 每条微博live url获取
                        if 'live_photo' in key_cards['mblog']:
                            for live_photo_url in key_cards['mblog']['live_photo']:
                                live_url_mblog.append(live_photo_url.replace('\/', '/'))

                        # 每条微博视频 url获取
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


                # 若当页json中['data']['cardlistInfo']无'since_id'，表示已无下一页
                if 'cardlistInfo' not in resp_json['data'] or 'since_id' not in resp_json['data']['cardlistInfo']:
                    print('\r [已获取图片微博：%d条；live微博：%d条；视频微博：%d条]' % (len(all_picture_url_dict), len(all_live_url_dict), len(all_video_url_dict)))
                    print()
                    return all_picture_url_dict, all_live_url_dict, all_video_url_dict
                    # print('\n 所有url获取完成！')
                since_id = str(resp_json['data']['cardlistInfo']['since_id'])
                break
            except Exception as error:
                print('\n     error: ', end='')
                print(error)
                print('     -->异常导致重新获取第' + str(page) + '页的URL')

def save_single_url(url, file_name):
    i = 0
    # 重新下载次数
    num = 3
    while True:
        time_interval("download")
        #最多下载三次，否则跳过
        if i > num:
            print("\n    -->当前url({})下载异常次数超过{}次，退出下载！".format(url, num))
            return False
        try:
            #if i != 0:
            #    print("    -->第" + str(i) + "次重新下载：" + url)
            # request.urlretrieve下载超时5s，重新下载，防止线程堵塞
            socket.setdefaulttimeout(5)
            request.urlretrieve(url, file_name)  # 最大99999
            return True
        except Exception as error:
            i += 1
            #print(' ', end='')
            #print(error)
            # print(url)

# 根据类型下载dict中所有得url
def download_by_type(all_url_dict, blogger_url_txt_dir, type):
    saved_url_list = read_txt(blogger_url_txt_dir)
    all_mblog_num = len(all_url_dict)
    if all_mblog_num:
        download_mblog_num = 0
        for creat_time, url_mblog in all_url_dict.items():
            for index in range(0, len(url_mblog)):
                url = url_mblog[index]
                print('\r [{}已下载进度：{}%({}/{})] 开始下载<{}>时刻第{}张(条){}：{}'.format(
                    type, int(download_mblog_num / all_mblog_num * 100), download_mblog_num,
                    all_mblog_num, creat_time, index + 1, type, url), end='')
                file_name = ''
                if type == '图片' :
                    file_name = blogger_download_dir + creat_time + ' - ' + str(index + 1) + '.jpg'
                elif type == 'live':
                    file_name = blogger_download_dir + creat_time + ' - ' + str(index + 1) + '.mov'
                elif type == '视频':
                    file_name = blogger_download_dir + 'video ' + creat_time + ' - ' + str(index + 1) + '.mp4'
                    # 视频url是动态的，所以使用"https......mp4"字符串来存储比较
                    mp4_index = url.find('mp4')
                    url = url[0:(mp4_index + 3)]
                if url not in saved_url_list and save_single_url(url_mblog[index], file_name):
                    saved_url_list.append(url)
                    write_txt(blogger_url_txt_dir, url)
            download_mblog_num += 1
            print('\r [{}已下载进度：{}%({}/{})]'.format(type, int(download_mblog_num / all_mblog_num * 100),
                                                          download_mblog_num, all_mblog_num), end='')
        print()


# 下载图片/视频
def download(blogger_name, blogger_url):
    set_sub_path(blogger_name)
    print('*'*20 + ' <blogger：' + blogger_name + '> ' + '*'*20)
    all_picture_dict, all_live_dict, all_video_dict = get_all_url(blogger_url)

    # 下载图片
    download_by_type(all_picture_dict, blogger_picture_url_txt_dir, '图片')
    # 下载live
    download_by_type(all_live_dict, blogger_live_url_txt_dir, 'live')
    # 下载视频
    download_by_type(all_video_dict, blogger_video_url_txt_dir, '视频')

    print('*' * 45 + '\n')
# main 主入口
if __name__ == '__main__':
    set_total_path()
    #print(download_dir)
    while True:
        function_selection = input('\n  a:新下载blog；b:更新所有blog；c:单独更新blog；d:删除blog；e:从当前blogger更新后续所有blog；l:获取blogger列表；x:退出程序：\n请输入对应得指令：')
        blogger_list = read_txt(blogger_list_txt_dir)
        if function_selection == 'a':
            blogger_name = input("blogger name:")
            if blogger_name in blogger_list:
                print('当前blogger：' + blogger_name + ' 已在列表中！')
            elif not blogger_name:
                print('blogger_name为空！')
            else:
                blogger_url_input = input('blogger url(自动添加"&since_id="):')
                if not blogger_url_input:
                    print('blogger_url为空！')
                    continue
                blogger_url = blogger_url_input
                if blogger_url_input not in blogger_list:
                    # 新下载的blogger写入到文本文档bloglist.txt
                    write_txt(blogger_list_txt_dir, blogger_name)
                    write_txt(blogger_list_txt_dir, blogger_url_input)
                else:
                    blogger_name = blogger_list[blogger_list.index(blogger_url_input) - 1]
                    print('当前blogger url已在列表中，使用列表中的名字 <' + blogger_name + '>')
                download(blogger_name, blogger_url)
        elif function_selection == 'b':
            for i in range(0,len(blogger_list),2):
                print(" [更新所有blog进度：%d%%(%d/%d)]" % ((i/2 + 1)/(len(blogger_list)/2)*100 ,i/2 + 1, len(blogger_list)/2))
                blogger_name = blogger_list[i]
                blogger_url = blogger_list[i+1]
                download(blogger_name, blogger_url)
                time_interval("update_all")
        elif function_selection == 'c' or function_selection == 'd':
            for i in range(0, len(blogger_list),2):
                print(str(int(i/2+1)) + '：' + blogger_list[i])
            blog_id = int(input('输入对应得blog id：'))
            while True:
                if blog_id <= 0 or blog_id > len(blogger_list)/2:
                    blog_id = int(input('blog id 输入错误，重新输入：'))
                else:
                    break
            blogger_name = blogger_list[(blog_id - 1) * 2]
            blogger_url = blogger_list[(blog_id - 1) * 2 + 1]
            if function_selection == 'c':
                download(blogger_name, blogger_url)
            elif function_selection == 'd':
                rm_dir(download_dir + blogger_name + '/')
                blogger_list.remove(blogger_name)
                blogger_list.remove(blogger_url)
                write_list_txt(blogger_list_txt_dir, blogger_list, len(blogger_list))
        elif function_selection == 'e':
            for i in range(0, len(blogger_list),2):
                print(str(int(i/2+1)) + '：' + blogger_list[i])
            blog_id = int(input('输入对应得blog id：'))
            while True:
                if blog_id <= 0 or blog_id > len(blogger_list)/2:
                    blog_id = int(input('blog id 输入错误，重新输入：'))
                else:
                    break
            for i in range(blog_id, len(blogger_list),2):
                print(" [更新所有blog进度：%d%%(%d/%d)]" % (i/(len(blogger_list)/2)*100 ,i, len(blogger_list)/2))
                blogger_name = blogger_list[(i - 1) * 2]
                blogger_url = blogger_list[(i - 1) * 2 + 1]
                download(blogger_name, blogger_url)
                time_interval("update_all")
        elif function_selection == 'l':
            for i in range(0, len(blogger_list),2):
                print(str(int(i/2+1)) + '：' + blogger_list[i])
        elif function_selection == 'x':
            exit()
        else:
            print('指令输入错误，请重新输入！')





