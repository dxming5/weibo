# 集中配置区

# 下载根目录（绝对路径模式）
DOWNLOAD_DIR = 'F:/图片/blog/'

# 登录微博后从浏览器复制的 Cookie，用于绕过 432 风控
# 获取方式：浏览器打开 https://m.weibo.cn 并登录 -> F12 开发者工具 ->
#          Network -> 任意请求 -> Request Headers 里的 Cookie 整段复制
COOKIE = ''

# 单博主最大下载条数，0 为不限制
BLOGGER_MAX_NUM = 0

# 是否启用时间间隔（反爬机制）
IS_TIME_INTERVAL = True

# 单文件下载超时（秒）
DOWNLOAD_TIMEOUT = 5

# 单 URL 最大重试次数
MAX_RETRY = 3
