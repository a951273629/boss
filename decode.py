import os
import json
import base64
from win32 import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def GetString(LocalState):
    with open(LocalState, 'r', encoding='utf-8') as f:
        s = json.load(f)['os_crypt']['encrypted_key']
    return s


def pull_the_key(base64_encrypted_key):
    encrypted_key_with_header = base64.b64decode(base64_encrypted_key)
    encrypted_key = encrypted_key_with_header[5:]
    key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return key


def DecryptString(key, data):
    nonce, cipherbytes = data[3:15], data[15:]
    aesgcm = AESGCM(key)
    plainbytes = aesgcm.decrypt(nonce, cipherbytes, None)
    plaintext = plainbytes.decode('utf-8')
    return plaintext

# 读取本地默认浏览器的默认秘钥


def get_key_file():
    home_path = 'E:\dataChrome'
    # home_path = os.path.expanduser('~')
    # cookie_path = os.path.join(home_path, 'AppData', 'Local', 'Google', 'Chrome',
    #                            'User Data', 'Local State')
    cookie_path = os.path.join(home_path, 'Local State')
    return cookie_path

# 测试解密


def decode_cookies(key_str):

    LocalState = get_key_file()  # 密钥文件

    key = pull_the_key(GetString(LocalState))
    return DecryptString(key, key_str)
