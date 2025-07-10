import logging
import requests
import random
from lxml import etree

logger = logging.getLogger("torrent")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

# 现在使用的是 torznab 的地址获取一个磁力链接 这个是开源项目 https://github.com/bitmagnet-io/bitmagnet
def random_one_magnet():
    magnet = ""
    # Torznab 服务器的 URL
    TORZNAB_URL = "http://localhost:3333/torznab"

    # Your API key for authentication, if required
    API_KEY = None

    # 随机生成一个查询关键词（可以根据需要修改）
    QUERY_TERMS = ["movie", "tv", "music", "software", "game"]
    query_term = random.choice(QUERY_TERMS)

    # 设定所需的最大大小（小于 1G）
    max_size = 1024 * 1024 * 1024  # 1 GB in MB

    # 发起请求
    params = {
        't': 'search',
        'q': query_term,
        'size': f'0-{max_size}',  # 请求小于1GB的结果
    }

    if API_KEY:
        params['apikey'] = API_KEY

    response = requests.get(TORZNAB_URL, params=params)

    # 检查响应状态
    if response.status_code == 200:
        # 使用 lxml 解析 XML 响应
        tree = etree.fromstring(response.content)

        # 使用 XPath 获取所有 <item> 元素
        sizes = tree.xpath("//size")
        list.sort(sizes, key=lambda item: int(item.text))
        if int(sizes[0].text) < max_size:
            enclosure_url = sizes[0].xpath("../enclosure/@url")
            return enclosure_url[0]
        # if magnets:
        #     # 随机选择一个项
        #     magnet = random.choice(magnets)
        #     logger.debug(f"随机获取的磁力链接: {magnet}")
        # else:
        #     logger.debug("没有找到符合条件的磁力链接。")
    
    logger.error("没有找到合适的磁力")
    return random_one_magnet()

if __name__ == "__main__":
    # s = [value.value for value in 模式选项]
    # print(s)
    print(random_one_magnet())