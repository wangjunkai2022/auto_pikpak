#!/usr/bin/python3
import datetime
import os
import threading
import time

import requests
import asyncio
import requests
import json

from proxy_ip.kuaidaili import kuaidaili

pattern = r"\?page=[a-z0-9]+"


def get_proxy_list():
    types = {
        1: "http",
        2: "https",
        3: None,
        4: 'socks5',
        # 5: 'socks5',
        # 6: None,
        # 7: "http",  # http/https
        # 8: None,
        # 9: None,
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
                # if proxy_type == "http":
                if proxy_type:
                    ips.append(f"{ip_data['addr']} {proxy_type}")

    return ips


async def check_proxy(proxy):
    try:
        # url = 'https://google.com'
        # timeout = httpx.Timeout(connect=1, read=1, write=1, pool=None)
        proxy_data = proxy.split()
        url = f'https://inapp.mypikpak.com/ping'
        # transport = AsyncProxyTransport.from_url(f"{proxy_data[1]}://{proxy_data[0]}")
        # async with httpx.AsyncClient(transport=transport) as client:
        #     response = await client.get(url, timeout=2)
        #     if response.status_code == 200:
        #         print(f'{proxy} is working')
        #         return proxy
        response = requests.request("GET", url, proxies={
            "http": f"{proxy_data[1]}://{proxy_data[0]}",
            "https": f"{proxy_data[1]}://{proxy_data[0]}",
        }, timeout=2, verify=False)
        if response.status_code == 200:
            print(f'{proxy} is working')
            return proxy
    except Exception as error:
        print(f'error:\t{error}\t{proxy} is not working')
        pass
    return


async def get_pikpak_proyxs():
    ips = get_proxy_list()
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


def pingPikpak(proxy, ok_ips):
    try:
        start_time = time.time()
        proxy_data = proxy.split()
        url = f'https://inapp.mypikpak.com/ping'
        # transport = AsyncProxyTransport.from_url(f"{proxy_data[1]}://{proxy_data[0]}")
        # async with httpx.AsyncClient(transport=transport) as client:
        #     response = await client.get(url, timeout=2)
        #     if response.status_code == 200:
        #         print(f'{proxy} is working')
        #         return proxy
        response = requests.request("GET", url, proxies={
            "http": f"{proxy_data[1]}://{proxy_data[0]}",
            "https": f"{proxy_data[1]}://{proxy_data[0]}",
        }, timeout=2, verify=False)
        if response.status_code == 200:
            duration = time.time() - start_time
            print(f'{proxy} is working 耗时{duration:.2f}秒')
            if duration < 3:
                ok_ips.append(proxy_data)
                return True
    except:
        # print(f"{proxy} 失败")
        pass
    return False


def thread_get_all_ping_pikpak_proxy():
    # ips = get_proxy_list()
    _ips = kuaidaili().get_proxy_list()
    # index_count = 10
    # ips = [ips[i:i + index_count] for i in range(0, len(ips), index_count)]
    _ok_ips = []
    _ths = []
    for _ip in _ips:
        # for __ips in _ips:
        _th = threading.Thread(target=pingPikpak, args=(_ip, _ok_ips))
        # for t in ths:  # 循环启动10个线程
        _th.start()
        _ths.append(_th)
        # for t in ths:  # 等待10个线程结束
        #     t.join()
    for _th in _ths:
        _th.join()

    _ok_ips = remove_duplicates(_ok_ips)
    return _ok_ips


def remove_duplicates(lst):
    if not lst:  # 检查列表是否为空
        return []  # 如果为空，直接返回空列表

    unique_list = []
    seen = set()

    for item in lst:
        # 将列表转换为元组，以便可以将其添加到集合中
        item_tuple = tuple(item) if isinstance(item, list) else item

        if item_tuple not in seen:
            seen.add(item_tuple)
            unique_list.append(item)

    return unique_list


# cache_json_file = 'ips.json'
cache_json_file = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), "ips.json")

# 获取一个可以代理pikpak的ip


def pop_prxy_pikpak():
    try:
        with open(cache_json_file, mode="r", encoding="utf-8") as file:
            json_str = file.read()
            json_data = json.loads(json_str)
    except:
        json_data = {}
    _time = time.time() - json_data.get("time", 0)
    _used_ips = []
    if _time < 60 * 60 * 12:
        _used_ips = json_data.get("used_ips", [])
    for _proxy in thread_get_all_ping_pikpak_proxy():
        isAdd = False
        for __proxy in _used_ips:
            if _proxy == __proxy:
                isAdd = True
                break
        if isAdd:
            pass
        else:
            _used_ips.append(_proxy)
            break
    if isAdd:
        print("没有新的 未使用的代理ip了")
        return None
    json_data = {
        "time": time.time(),
        "used_ips": _used_ips,
    }
    with open(cache_json_file, mode='w', encoding="utf-8") as file:
        file.write(json.dumps(json_data, indent=4, ensure_ascii=False))

    return _used_ips[len(_used_ips)-1]


if __name__ == '__main__':
    pis = thread_get_all_ping_pikpak_proxy()
    print(pis)
    # main()
    # asyncio.run(get_pikpak_proyxs())
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
