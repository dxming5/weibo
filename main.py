import storage
import downloader
import util

if __name__ == '__main__':
    storage.ensure_root()
    while True:
        function_selection = input('\n  a:新下载blog；b:更新所有blog；c:单独更新blog；d:删除blog；e:从当前blogger更新后续所有blog；l:获取blogger列表；x:退出程序：\n请输入对应得指令：')
        blogger_list = storage.read_lines(storage.BLOGGER_LIST_TXT)
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
                    # 新下载的 blogger 写入到文本文档 bloggerlist.txt
                    storage.append_line(storage.BLOGGER_LIST_TXT, blogger_name)
                    storage.append_line(storage.BLOGGER_LIST_TXT, blogger_url_input)
                else:
                    blogger_name = blogger_list[blogger_list.index(blogger_url_input) - 1]
                    print('当前blogger url已在列表中，使用列表中的名字 <' + blogger_name + '>')
                downloader.download(blogger_name, blogger_url)
        elif function_selection == 'b':
            total = len(blogger_list) // 2
            for i in range(0, len(blogger_list), 2):
                print(" [更新所有blog进度：%d%%(%d/%d)]" % ((i // 2 + 1) / total * 100, i // 2 + 1, total))
                blogger_name = blogger_list[i]
                blogger_url = blogger_list[i + 1]
                downloader.download(blogger_name, blogger_url)
                util.time_interval("update_all")
        elif function_selection == 'c' or function_selection == 'd':
            total = len(blogger_list) // 2
            for i in range(0, len(blogger_list), 2):
                print(str(i // 2 + 1) + '：' + blogger_list[i])
            blog_id = int(input('输入对应得blog id：'))
            while True:
                if blog_id <= 0 or blog_id > total:
                    blog_id = int(input('blog id 输入错误，重新输入：'))
                else:
                    break
            blogger_name = blogger_list[(blog_id - 1) * 2]
            blogger_url = blogger_list[(blog_id - 1) * 2 + 1]
            if function_selection == 'c':
                downloader.download(blogger_name, blogger_url)
            elif function_selection == 'd':
                storage.rm_dir(storage.blogger_paths(blogger_name)['dir'])
                blogger_list.remove(blogger_name)
                blogger_list.remove(blogger_url)
                storage.write_lines(storage.BLOGGER_LIST_TXT, blogger_list)
        elif function_selection == 'e':
            total = len(blogger_list) // 2
            for i in range(0, len(blogger_list), 2):
                print(str(i // 2 + 1) + '：' + blogger_list[i])
            blog_id = int(input('输入对应得blog id：'))
            while True:
                if blog_id <= 0 or blog_id > total:
                    blog_id = int(input('blog id 输入错误，重新输入：'))
                else:
                    break
            # 修复原 e 指令索引越界：从 (blog_id-1)*2 开始按步长 2 遍历
            for i in range((blog_id - 1) * 2, len(blogger_list), 2):
                print(" [更新所有blog进度：%d%%(%d/%d)]" % ((i // 2 + 1) / total * 100, i // 2 + 1, total))
                blogger_name = blogger_list[i]
                blogger_url = blogger_list[i + 1]
                downloader.download(blogger_name, blogger_url)
                util.time_interval("update_all")
        elif function_selection == 'l':
            total = len(blogger_list) // 2
            for i in range(0, len(blogger_list), 2):
                print(str(i // 2 + 1) + '：' + blogger_list[i])
        elif function_selection == 'x':
            exit()
        else:
            print('指令输入错误，请重新输入！')
