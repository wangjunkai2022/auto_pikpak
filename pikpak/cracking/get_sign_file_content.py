import json
import os
from threading import Lock

# 获取包中的sign数组
# 假设G是一个全局变量，用于存储JSON数组
G = None
G_lock = Lock()


def decrypt_data(file_name, key):
    try:
        with open(file_name, 'rb') as file:
            data = list(file.read())
            if not data or len(data) == 0:
                print(f"buf empty, Read the last file and exit {data}")
                return None, 37
            for i in range(len(data)):
                data[i] = (data[i] ^ key[i % len(key)]) ^ (i & 255)
            return bytes(data[:-1]).decode('utf-8'), data[-1] & 255
    except Exception as e:
        print(f"Error: {e}")
        return None, 37


def load_json_data():
    global G
    if G is None:
        with G_lock:
            if G is None:
                file_name = os.path.dirname(
                    os.path.abspath(__file__)) + "/" + "alg/alg"
                __file_name = file_name
                sb = []
                while True:
                    decrypted_str, next_int = decrypt_data(
                        __file_name, [1, 7, 9])
                    if decrypted_str is None:
                        break
                    sb.append(decrypted_str)
                    if next_int == 37:
                        break
                    __file_name = f"{file_name}{next_int}"
                if len(sb) == 0:
                    raise Exception("StringBuilder length is 0")
                json_data = json.loads(''.join(sb))
                print(f"JSON data: {json_data}")
                G = json_data.get("algorithms", [])
    return G


# 示例使用
try:
    algorithms = load_json_data()
    print("Algorithms:", algorithms)
except Exception as e:
    print(f"An error occurred: {e}")
