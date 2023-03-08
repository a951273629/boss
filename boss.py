import sqlite3
import requests
import os
import decode
import time
import json
import re
from selenium_boss import Browser
# 获取 Chrome 浏览器的 cookie 数据库路径

'''
 此接口获取城市
 https://www.zhipin.com/wapi/zpgeek/common/data/citysites.json


 职位接口
https://www.zhipin.com/wapi/zpCommon/data/position.json

个人信息接口
https://www.zhipin.com/wapi/zpuser/wap/getUserInfo.json

首页
https://www.zhipin.com/web/geek/job?query=&page=6

工作列表  boss主要的反爬就在工作列表上
https://www.zhipin.com/wapi/zpgeek/search/joblist.json
'''


class Boss:
    # 设置 User-Agent

    headers = {
        "accept": "application/json, text/plain, */*",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        "accept-language": "zh-CN,zh;q=0.9",
        "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
    }
    browser = Browser()
    cookies = {}

    def __init__(self):
        self.session = requests.Session()

        self.session.verify = False
        # 设置user-agent
        self.session.headers.update(self.headers)

        self.init_cookies()
        print('cookies@', self.session.cookies.get_dict())
        print('请求头@', self.session.headers)
        self.boss_ids = self.open_boss_data()
        pass
    # 初始化token

    def init_cookies(self):
        # 连接Chrome浏览器的cookie数据库
        self.conn = sqlite3.connect(self.get_cookie_file())
        # 从本地浏览器储存中获取cookie
        self.cookies = self.get_cookies('zhipin.com')
        self.session.cookies.update(self.cookies)
        self.session.headers.update({"token": self.get_use_token(),
                                     "zp_token": self.session.cookies.get('geek_zp_token')})

    def fresh_cookie_header(self):
        self.cookies = self.browser.fresh_cookie()
        # 更新检测的token字段
        self.session.cookies.update(
            {'__zp_stoken__': self.cookies.get('__zp_stoken__'),
             'geek_zp_token': self.cookies.get('geek_zp_token'),
             '__a': self.cookies.get('__a'), })

        self.session.headers.update({"token": self.get_use_token(),
                                     "zp_token": self.session.cookies.get('geek_zp_token')})

    def get_cookie_file(self):
        # 谷歌浏览器数据储存位置 执行start.bat后会自动生成
        home_path = 'E:\dataChrome'
        # home_path = os.path.expanduser('~')
        # cookie_path = os.path.join(home_path, 'AppData', 'Local', 'Google', 'Chrome',
        #                            'User Data', 'Default', 'Network', 'Cookies')
        cookie_path = os.path.join(home_path, 'Default', 'Network', 'Cookies')
        print(cookie_path)
        return cookie_path

    # 读取 Chrome 浏览器的 cookie 数据库，并获取指定网站的 cookie
    def get_cookies(self, url):

        c = self.conn.cursor()
        c.execute(
            'SELECT name, encrypted_value FROM cookies  WHERE host_key LIKE ?', ('%'+url+'%',))
        cookies = c.fetchall()
        c.close()
        self.conn.close()
        cookie_dict = {}
        for cookie in cookies:
            # cookie 解密
            cookie_dict[cookie[0]] = decode.decode_cookies(cookie[1])
        return cookie_dict

    # 打开存储id的json数据
    def open_boss_data(self, json_file_path="send.json"):

        if os.path.exists(json_file_path):
            # 如果文件存在则读取文件内容
            with open(json_file_path, "r") as f:
                data = json.load(f)
        else:
            # 如果文件不存在则创建文件
            data = {}
            with open(json_file_path, "w") as f:
                json.dump(data, f)
        return data
    # 保存数据到本地

    def save_boss_data(self, json_file_path="send.json"):

        with open(json_file_path, "w") as f:
            json.dump(self.boss_ids, f)
        pass

    # 获取用户token 放在请求头中
    def get_use_token(self):
        response = self.session.get(
            f'https://www.zhipin.com/wapi/zpuser/wap/getUserInfo.json')
        user_json = response.json()
        token = user_json['zpData']['token']

        return token
    # 访问首页 更新ref

    def get_head(self, page='1'):
        url = f'https://www.zhipin.com/web/geek/job?query=&page={page}'
        header = {
            "referer": url
        }
        self.session.headers.update(header)
        self.session.get(url=url)
        pass

    # 更新token

    def update_token(self):
        # 毫秒级的时间戳
        now_time = int(time.time()*1000)
        response = self.session.get(
            f'https://www.zhipin.com/wapi/zppassport/get/zpToken?v={now_time}')
        time_json = response.json()
        # print('新的token出现@', time_json)
        token = str(time_json['zpData']['token'])
        print('token@', token)
        # 更新请求头和cookie
        self.session.cookies.update({"geek_zp_token": token})
        self.session.headers.update({"zp_token": token})

    # 获取指定城市的code
    def get_city_code(self, city_name="深圳"):
        response = self.session.get(
            f'https://www.zhipin.com/wapi/zpgeek/common/data/citysites.json')
        city_json = response.json()
        city_list = city_json['zpData']
        for city in city_list:
            if (city['name'] == city_name):
                print('城市@', city['name'])
                return city['code']
        pass

    # 获取指定职位的code
    def get_position_code(self, position_first="前端开发", position_last="前端开发工程师"):
        response = self.session.get(
            f'https://www.zhipin.com/wapi/zpCommon/data/position.json')
        position_json = response.json()

        position_list = position_json['zpData'][0]['subLevelModelList']

        for position in position_list:
            if (position['name'] == position_first):
                for po in position['subLevelModelList']:
                    if (po['name'] == position_last):
                        return po['code']
        pass

    # https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=&city=101210100&experience=104&degree=203&industry=&scale
    # =303,304,305,306,302&stage=&position=100901&jobType=&salary=404&multiBusinessDistrict=&multiSubway=&page=1&pageSize=30
    # 获取公司列表
    def get_company(self, city='101210100', experience={'102', '101', '103'}, degree='0', scale={'302', '303', '304', '305', '306'}, position='100901', salary='0', page='1'):
        scale_str = str(','.join(scale))
        experience_str = str(','.join(experience))
        while True:
            response = self.session.get(
                f'https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=&city={city}&experience={experience_str}&degree={degree}&industry=&scale={scale_str}& \
                stage=&position={position}&jobType=&salary={salary}&multiBusinessDistrict=&multiSubway=&page={page}&pageSize=30')
            company_json = response.json()
            print(company_json['code'])
            if (str(company_json['code']) != '37'):
                break
            else:
                print('爬虫被监测了,更新cookie@', company_json['code'])
                self.fresh_cookie_header()

        company_list = company_json['zpData']['jobList']
        return company_list

    # 发送post请求打招呼
    def hello(self, securityId='', jobId='', lid=''):
        url = f'https://www.zhipin.com/wapi/zpgeek/friend/add.json?securityId={securityId}&jobId={jobId}&lid={lid}'
        response = self.session.post(url=url)
        hello_json = response.json()
        print('打招呼@@@@@@@@', hello_json)
        pass

    # 打招呼线程
    def start_hello(self):
        try:
            position_code = self.get_position_code()
            city_code = self.get_city_code()
            time.sleep(2)
            i = 1
            while (i <= 10):
                company_list = self.get_company(
                    city=city_code, position=position_code, page=str(i))

                for item in company_list:
                    if 'encryptBossId' in self.boss_ids:
                        continue
                    self.boss_ids[item['encryptBossId']] = 1
                    self.hello(securityId=item['securityId'],
                               jobId=item['encryptJobId'],
                               lid=item['lid'])

                    time.sleep(0.8)
            print(f'完成:{i}')
            self.save_boss_data()
            i = i+1
        except Exception as e:
            print('异常退出,保存数据:', e)
            self.save_boss_data()
            raise
            # 进行中断操作也会走这里 KeyboardInterrupt
        finally:
            self.save_boss_data()
        pass
    # 把公司规模大于1000的过滤出来方便以后官网投递

    def get_big_brand(self):
        position_code = self.get_position_code()
        city_code = self.get_city_code()
        time.sleep(0.8)

        # 把员工规模大于1000的存储在本地

        def than_thousand(item):
            min = str(item['brandScaleName']).split('-')[0]
            min = re.findall(r'\d*', min)[0]
            if int(min) >= 1000:
                print(item['brandScaleName'], item['brandName'])
                return True
            return False
        # 公司信息保存到本地

        def save_brand_data(json_file_path="brand.json", brand_list=[]):
            brand = {
                str(city_code): brand_list
            }
            with open(json_file_path, "w", encoding="utf-8") as f:
                json.dump(brand, f, ensure_ascii=False)

        brand_list = []
        i = 1
        while (i <= 10):
            try:
                company_list = self.get_company(
                    city=city_code, position=position_code, page=str(i))

                filter_list = list(filter(than_thousand, company_list))
                for item in filter_list:
                    brand_list.append({
                        'name': item['brandName'],
                        'salary': item['brandScaleName']
                    })

            except Exception as e:
                save_brand_data(brand_list=brand_list)
                print('异常退出,保存数据:', e)
                exit(0)
            # 进行中断操作也会走这里 KeyboardInterrupt
            finally:
                save_brand_data(brand_list=brand_list)
                print(f'完成:{i}')
                i = i+1

            time.sleep(2)
            # old = self.session.cookies.get('__zp_stoken__')
            # self.fresh_cookie_header()
            # new = self.session.cookies.get('__zp_stoken__')
            # if old == new:
            #     print('两次一样的@@@@@-------------------@@@@@@@@@@', new)
            # else:
            #     print('两次__zp_stoken__不一样@@@@@@@@@@@@@@@@@@@@@@@@@@@\n', new)
            # time.sleep(random.uniform(1, 2))
        pass


boss = Boss()
boss.start_hello()
