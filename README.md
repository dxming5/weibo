# Weibo Downloader

一个简单易用的微博图片/视频下载工具，支持批量下载和增量更新。

## 功能特性

- **多类型下载**：支持下载微博图片、Live 图片和视频
- **增量更新**：自动跳过已下载内容，避免重复下载
- **批量管理**：支持同时管理多个博主，一键更新所有博主
- **断点续传**：网络中断后可继续下载，不丢失进度
- **反爬机制**：内置时间间隔设置，降低被封禁风险
- **进度显示**：实时显示下载进度和获取状态

## 目录结构（模块化）

```
/weibo/
├── main.py            # 入口：CLI 菜单（a/b/c/d/e/l/x）
├── config.py          # 集中配置（下载路径 / Cookie / 限速 / 重试）
├── util.py            # 工具函数（time_interval、month_eng_to_num）
├── storage.py         # 路径管理 + txt 读写（bloggerlist.txt、各博主 url 记录）
├── fetcher.py         # 网络请求 + JSON 解析（get_all_url）
├── downloader.py      # 下载与去重（save_single_url / download_by_type / download）
├── README.md
└── (下载输出目录，默认 F:/图片/blog/)
    ├── bloggerlist.txt          # 记录所有博主名称和URL（成对存储）
    └── <blogger_name>/          # 每个博主一个独立文件夹
        ├── 图片文件(.jpg/.mov/.mp4)
        ├── picture_url.txt      # 已下载图片URL记录
        ├── live_url.txt         # 已下载Live URL记录
        └── video_url.txt        # 已下载视频URL记录
```

## 使用方法

### 运行环境

- Python 3.x
- 无需额外依赖（使用标准库）

### 配置（必做）

编辑 `config.py`：

```python
DOWNLOAD_DIR = 'F:/图片/blog/'   # 改为你的目标路径

# 登录微博后从浏览器复制的 Cookie，用于绕过 432 风控（未登录会被拦截）
# 获取：浏览器打开 https://m.weibo.cn 并登录 -> F12 -> Network -> 任意请求 -> Request Headers 里的 Cookie
COOKIE = ''

BLOGGER_MAX_NUM = 0   # 单博主最大下载条数（0为不限制）
IS_TIME_INTERVAL = True  # 是否启用时间间隔（反爬）
```

> 若运行时出现 `HTTP Error 432`，说明 Cookie 未配置或已过期，请重新填入。

### 启动

```bash
python main.py
```

### 操作指令

| 指令 | 功能 |
|------|------|
| `a` | 新增博主下载 |
| `b` | 更新所有博主的图片/live/视频 |
| `c` | 单独更新指定博主 |
| `d` | 删除指定博主及下载内容 |
| `e` | 从指定博主开始更新后续所有博主 |
| `l` | 查看博主列表 |
| `x` | 退出程序 |

### 添加博主

选择 `a` 后输入博主名称和微博移动端主页地址，例如：
```
blogger url(自动添加"&since_id="):https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&type=uid&value=7650634768&containerid=1076037650634768
```
脚本会自动拼接 `&since_id=` 翻页。

## 版本历史

| 版本 | 更新内容 |
|------|----------|
| v1~v15 | 早期单文件版本迭代（见 git 历史） |
| v16 | 模块化重构：拆分 config/util/storage/fetcher/downloader/main；修复 `e` 指令索引越界；修复批量任务中单博主失败误 `exit()` 的问题；配置集中化 |

## 配置选项

在 `config.py` 中可调整：

```python
DOWNLOAD_DIR = 'F:/图片/blog/'   # 下载根目录
COOKIE = ''                      # 登录 Cookie（绕过 432）
BLOGGER_MAX_NUM = 0              # 单博主最大下载条数，0 为不限制
IS_TIME_INTERVAL = True          # 是否启用反爬时间间隔
DOWNLOAD_TIMEOUT = 5             # 单文件下载超时（秒）
MAX_RETRY = 3                    # 单 URL 最大重试次数
```

## 免责声明

本工具仅供学习交流使用，请勿用于商业目的或违反微博服务条款的行为。
