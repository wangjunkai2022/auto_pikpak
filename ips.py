#!/usr/bin/python3
import datetime
import os
import requests
from bs4 import BeautifulSoup
import re
import httpx
import asyncio
import requests
import json

# import urllib3
# 
# import certifi
# import cryptography
# import pyOpenSSL

from concurrent.futures import ProcessPoolExecutor

pattern = r"\?page=[a-z0-9]+"


async def get_proxy_list():
    types = {
        1: None,
        2: "http",
        3: None,
        4: 'https',
        5: 'socks5',
        6: None,
        7: "http",  # http/https
        8: None,
        9: None,
    }
    now_time = datetime.datetime.utcnow()
    # 格式化时间字符串
    str_time = now_time.strftime("%Y-%m-%d")
    domain = "checkerproxy.net"
    url = f"https://{domain}/api/archive/{str_time}"
    # print(url)
    ips = []
    req = requests.get(url)
    if req and req.status_code == 200:
        data = json.loads(req.text)
        for ip_data in data:
            if ip_data['addr']:
                proxy_type = types[ip_data["type"]]
                if proxy_type == "http":
                    ips.append(f"{ip_data['addr']} {proxy_type}")

    return ips


async def check_proxy(proxy):
    try:
        # url = 'https://google.com'
        # timeout = httpx.Timeout(connect=1, read=1, write=1, pool=None)
        proxy_data = proxy.split()
        url = f'{proxy_data[1]}://inapp.mypikpak.com/ping'
        async with httpx.AsyncClient(proxies={
            f"{proxy_data[1]}://": f"{proxy_data[1]}://{proxy_data[0]}"
        }) as client:
            response = await client.get(url, timeout=2)
            if response.status_code == 200:
                print(f'{proxy} is working')
                return proxy
    except Exception as error:
        print(f'error:\t{error}\t{proxy} is not working')
        pass
    return


async def get_pikpak_proyxs():
    ips = await get_proxy_list()
    # proxies = []
    tasks = [check_proxy(proxy) for proxy in ips]
    proxies = await asyncio.gather(*tasks)
    # ips = ips[0:10]
    # with ProcessPoolExecutor(max_workers=10) as pe:
    #     future_tasks = []
    #     for ip in ips:
    #         future_tasks.append(pe.submit(check_proxy(ip)))
    #     for future in future_tasks:
    #         try:
    #             result = future.result()
    #             if result:
    #                 proxies.append(result)
    #         except:
    #             pass

    # for proxy in ips:
    #     if check_proxy(proxy):
    #         # print(proxy)
    #         proxies.append(proxy)
    #     else:
    #         pass
    #         # print(f"{proxy} 无法ping")
    while None in proxies:
        proxies.remove(None)
    print(proxies)
    # temp_file = "ip_isOk11.txt"
    # 
    # # 获取当前时间
    # now_time = datetime.datetime.now()
    # # 格式化时间字符串
    # str_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
    # # if not os.path.exists(temp_file):
    # #     os.system(r"touch {}".format(temp_file))  # 调用系统命令行来创建文件
    # input_str = f"\n\n时间:\n\t{str_time}\n{proxies}"
    # with open(temp_file, 'w') as f:  # 设置文件对象
    #     f.write(input_str)  # 将字符串写入文件中

    return proxies


def ipTest():
    f = open("ips.txt")
    ips = f.read()
    ips = ips.split("\n")
    proxies = []
    for proxy in ips:
        if check_proxy(proxy):
            print(proxy)
            proxies.append(proxy)
    print(proxies)
    temp_file = "ip_isOk.txt"

    import datetime
    # 获取当前时间
    now_time = datetime.datetime.now()
    # 格式化时间字符串
    str_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
    # if not os.path.exists(temp_file):
    #     os.system(r"touch {}".format(temp_file))  # 调用系统命令行来创建文件
    input_str = f"\n\n时间:\n\t{str_time}\n{proxies}"
    with open(temp_file, 'a') as f:  # 设置文件对象
        f.write(input_str)  # 将字符串写入文件中


if __name__ == '__main__':
    # main()
    asyncio.run(get_pikpak_proyxs())
    # ipTest()
    # url = "https://filesamples.com/samples/video/mp4/sample_1920x1080.mp4"
    # req = requests.get(str(url), headers=
    # {
    #     "User-Agent": r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.133 Safari/537.36'
    # }
    #                    , verify=False, stream=True)
    # path = "./test/test.mp4"
    # print(req)
    # 
    # with open(path, "wb") as code:
    #     for chunk in req.iter_content(chunk_size=10240):
    #         code.write(chunk)
