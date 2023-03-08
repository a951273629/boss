## Boss直聘全自动打招呼

**使用sqlite3连接chrome浏览器，获取本地浏览器cookie。使用cryptography本地解密cookie，获取登录的token**

**使用selenium模块连接chrome浏览器动态获取__zp_stoken__ 和geek_zp_token，来动态反爬。规避BOSS反爬的检测**

开发环境

- vscode

- python 3.10

使用的库

- requests
- sqlite3
- win32crypt
- cryptography
- selenium



**安装依赖**

```sh
pip install requriement.txt
```

**项目入口**`boss.py`



**启动项目**

1. pip 安装依赖
2. **需要手动执行一下 start.bat来启动浏览器，手动登录一下boss。执行start.bat浏览器数据储存位置在home_path = 'E:\dataChrome'下**
3. 执行`boss.py`



后言:boss的反爬真的十分厉害，反爬主要集中在获取工作列表接口上面: ` https://www.zhipin.com/wapi/zpgeek/search/joblist.json`就算动态更新了`__zp_stoken__`字段，也会被检测到。但是多更新几次又可以请求这个列表接口。非常玄学

