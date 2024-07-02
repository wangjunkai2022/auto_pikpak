
def custom_hash(value):
    min_int = -0x80000000
    max_int = 0x7fffffff

    if value > max_int:
        return min_int + (value - max_int) % (max_int - min_int + 1) - 1
    elif value < min_int:
        return max_int - (min_int - value) % (max_int - min_int + 1) + 1
    else:
        return value


def get_d(content):
    datas = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a]
    for index in range(len(content)):
        a = ord(content[index])
        b = unsigned_right_shift(datas[index % 4] ^ get_d1(a, 0x9e3779b9), 0x0)
        datas[index % 4] = get_d2(b, 0xd)
    for _ in range(8):
        for _index in range(4):
            datas[_index] = unsigned_right_shift(
                datas[_index] + get_d1(datas[(_index + 1) % 0x4], 0x85ebca6b), 0x0)
            datas[_index] = get_d2(datas[_index], 0x11)
            datas[_index] = unsigned_right_shift(
                (datas[_index] ^ datas[(_index + 2) % 4]), 0x0)
    _data_value = unsigned_right_shift(
        (datas[0] ^ datas[1] ^ datas[2] ^ datas[3]), 0x0)
    _data_value = get_d1(_data_value, 0xc2b2ae35)
    _data_value = unsigned_right_shift(
        _data_value ^ unsigned_right_shift(_data_value, 0x10), 0x0)
    _data_value = format(_data_value, "08x")
    print(_data_value)
    return _data_value


def unsigned_right_shift(n, bits):
    return (n % 0x100000000) >> bits


def get_d1(number, number2):
    a = unsigned_right_shift(number, 0x10) & 0xffff
    # var _0x2d6bd5 = _0xd53a54 >>> 0x10 & 0xffff
    b = 0xffff & number
    # , _0x1c4d50 = 0xffff & _0xd53a54
    c = unsigned_right_shift(number2, 0x10) & 0xffff
    # , _0x45abad = _0x17c071 >>> 0x10 & 0xffff
    d = 0xffff & number2
    # , _0x407dab = 0xffff & _0x17c071;
    return unsigned_right_shift(unsigned_right_shift((a * d + b * c & 0xffff) << 0x10, 0x0) + b * d, 0x0)
    # return ((_0x2d6bd5 * _0x407dab + _0x1c4d50 * _0x45abad & 0xffff) << 0x10 >>> 0x0) + _0x1c4d50 * _0x407dab >>> 0x0;


def get_d2(number1, number2):
    return ((number1 << number2) | (number1 >> (32 - number2))) & 0xffffffff


def get_d3(_0xd53a54, _0x17c071):
    _0x2d6bd5 = (_0xd53a54 >> 16) & 0xffff
    _0x1c4d50 = _0xd53a54 & 0xffff
    _0x45abad = (_0x17c071 >> 16) & 0xffff
    _0x407dab = _0x17c071 & 0xffff

    _temp1 = (_0x2d6bd5 * _0x407dab + _0x1c4d50 * _0x45abad) & 0xffff
    _temp2 = unsigned_right_shift((_temp1 << 16), 0) + _0x1c4d50 * _0x407dab
    return _temp2 & 0xffffffff



# 滑块数据加密
def r(e, t):
    n = t - 1
    if n < 0:
        n = 0
    r = e[n]
    u = r["row"] // 2 + 1
    c = r["column"] // 2 + 1
    f = r["matrix"][u][c]
    l = t + 1
    if l >= len(e):
        l = t
    d = e[l]
    p = l % d["row"]
    h = l % d["column"]
    g = d["matrix"][p][h]
    y = e[t]
    m = 3 % y["row"]
    v = 7 % y["column"]
    w = y["matrix"][m][v]
    b = i(f) + o(w)
    x = i(w) - o(f)
    return [
        s(a(i(f), o(f))),
        s(a(i(g), o(g))), 
        s(a(i(w), o(w))),
        s(a(b, x))
        ]


def i(e):
    return int(e.split(",")[0])


def o(e):
    return int(e.split(",")[1])


def a(e, t):
    return str(e) + "^⁣^" + str(t)


def s(e):
    t = 0
    n = len(e)
    for r in range(n):
        t = u(31 * t + ord(e[r]))
    return t


def u(e):
    t = -2147483648
    n = 2147483647
    if e > n:
        return t + (e - n) % (n - t + 1) - 1
    if e < t:
        return n - (t - e) % (n - t + 1) + 1
    return e


def c(e, t):
    return s(e + "⁣" + str(t))


def img_jj(e, t, n):
    return {"ca": r(e, t), "f": c(n, t)}


if __name__ == "__main__":
    r = get_d(
        # 1acfc3bc04b47541024bca11605f8ef9e99e6682a4dedc21ed3427f0462f852978b247ef12fd349183531
        "4ba5443008734546044adad1eb79ace0a99e6682b331dc21ed3427f0462f852978b247ef12fd406245002")
    print(r)
