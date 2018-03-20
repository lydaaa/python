# coding:utf-8

'''
@author = super_fazai
@File    : chuchujie_9_9_parse.py
@Time    : 2018/2/23 10:36
@connect : superonesfazai@gmail.com
'''

"""
楚楚街9.9, 29.9, 49.9元商品页面解析系统
"""

import time
from random import randint
import json
import requests
import re
from pprint import pprint
from decimal import Decimal

from time import sleep
import datetime
import gc
import pytz
from scrapy.selector import Selector

from settings import HEADERS
from my_ip_pools import MyIpPools

class ChuChuJie_9_9_Parse(object):
    def __init__(self):
        self.headers = {
            'Accept': 'application/json,text/javascript,*/*;q=0.01',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'api-product.chuchujie.com',
            'Origin': 'https://m.chuchujie.com',
            'Referer': 'https://m.chuchujie.com/details/detail.html?id=10016793335',
            'Cache-Control': 'max-age=0',
            'User-Agent': HEADERS[randint(0, 34)],  # 随机一个请求头
        }
        self.result_data = {}

    def get_goods_data(self, goods_id):
        '''
        模拟构造得到data的url
        :param goods_id:
        :return: data 类型dict
        '''
        if goods_id == '':
            self.result_data = {}
            return {}

        print('------>>>| 对应的手机端地址为: ', 'https://m.chuchujie.com/details/detail.html?id=' + goods_id)

        '''
        1.原先直接去手机端页面api post请求数据但是死活就返回请求参数错误，反复研究无果, 就改为解析pc端的
        '''
        # tmp_url = 'https://api-product.chuchujie.com/api.php?method=product_detail'
        # self.headers['Referer'] = 'https://m.chuchujie.com/details/detail.html?id=' + str(goods_id)
        #
        # # 设置代理ip
        # ip_object = MyIpPools()
        # self.proxies = ip_object.get_proxy_ip_from_ip_pool()  # {'http': ['xx', 'yy', ...]}
        # self.proxy = self.proxies['http'][randint(0, len(self.proxies) - 1)]
        #
        # tmp_proxies = {
        #     'http': self.proxy,
        # }
        # # print('------>>>| 正在使用代理ip: {} 进行爬取... |<<<------'.format(self.proxy))
        #
        # params_2 = {
        #     "channel": "QD_appstore",
        #     "package_name": "com.culiukeji.huanletao",
        #     "client_version": "3.9.101",
        #     "ageGroup": "AG_0to24",
        #     "client_type": "h5",
        #     "api_version": "v5",
        #     "imei": "",
        #     "method": "product_detail",
        #     "gender": "1",      # 性别 0-女、1-男
        #     "token": "",
        #     "userId": "",
        #     "product_id": int(goods_id),
        # }
        #
        # params = {
        #     'data': json.dumps(params_2),
        # }
        #
        # try:
        #     # response = requests.post(
        #     #     url=tmp_url,
        #     #     headers=self.headers,
        #     #     data=json.dumps(params),
        #     #     proxies=tmp_proxies,
        #     #     timeout=13
        #     # )
        #     response = requests.get(
        #         url=tmp_url,
        #         headers=self.headers,
        #         params=params,
        #         proxies=tmp_proxies,
        #         timeout=13,
        #     )
        #     last_url = re.compile(r'\+').sub('', response.url)  # 转换后得到正确的url请求地址
        #     print(last_url)
        #     print(tmp_url + '&data=%7B%22channel%22%3A%22QD_appstore%22%2C%22package_name%22%3A%22com.culiukeji.huanletao%22%2C%22client_version%22%3A%223.9.101%22%2C%22ageGroup%22%3A%22AG_0to24%22%2C%22client_type%22%3A%22h5%22%2C%22api_version%22%3A%22v5%22%2C%22imei%22%3A%22%22%2C%22method%22%3A%22product_detail%22%2C%22gender%22%3A%221%22%2C%22token%22%3A%22%22%2C%22userId%22%3A%22%22%2C%22product_id%22%3A10016793335%7D')
        #     response = requests.get(last_url, headers=self.headers, proxies=tmp_proxies, timeout=13)  # 在requests里面传数据，在构造头时，注意在url外头的&xxx=也得先构造
        #
        #     data = response.content.decode('utf-8')
        #     print(data)
        #
        # except Exception:
        #     print('requests.post()请求超时....')
        #     print('data为空!')
        #     self.result_data = {}  # 重置下，避免存入时影响下面爬取的赋值
        #     return {}

        '''
        2. 改为解析pc端的商品页面数据
        '''
        tmp_url = 'http://wx.chuchujie.com/index.php?s=/WebProduct/product_detail/product_id/' + str(goods_id)

        body = self.get_url_body(tmp_url=tmp_url)
        # print(body)

        if body == '':
            print('获取到的body为空str!')
            self.result_data = {}
            return {}

        data = {}

        try:
            data['title'] = Selector(text=body).css('div.zy_info_rt h3::text').extract_first()
            if data['title'] == '':
                print('title为空!')
                raise Exception

            data['sub_title'] = ''

            data['shop_name'] = Selector(text=body).css('div.other.ft14.clearfix label b::text').extract_first()
            # print(data['shop_name'])

            # 获取所有示例图片
            all_img_url = [{
                'img_url': item
            } for item in list(Selector(text=body).css('p.s_img label img::attr("src")').extract())]
            # pprint(all_img_url)
            data['all_img_url'] = all_img_url

            '''
            获取p_info
            '''
            # 由于获取的是pc端的对应没有p_info
            data['p_info'] = []

            '''
            获取商品的div_desc
            '''
            div_desc = Selector(text=body).css('div.s_two').extract_first()
            # print(div_desc)
            if div_desc == '':
                print('div_desc为空!请检查!')
                raise Exception

            data['div_desc'] = div_desc

            '''
            获取detail_name_list
            '''
            detail_name_list = Selector(text=body).css('div.info-wd.bd-red dl.detail dt::text').extract()
            if len(detail_name_list) <= 1:
                detail_name_list = []

            else:
                detail_name_list = [{'spec_name': item} for item in detail_name_list[:-1]]

            # print(detail_name_list)
            data['detail_name_list'] = detail_name_list

            # 商品价格(原价)跟淘宝价格
            taobao_price = Selector(text=body).css('dl.detail p.price b::text').extract_first()
            price = Selector(text=body).css('dl.detail dd em.yjprice::text').extract_first()
            # print(taobao_price)
            # print(price)
            try:
                # 后面有'*' 是为了避免有价格为整数不是浮点类型的
                taobao_price = re.compile(r'(\d+\.{0,1}\d*)').findall(taobao_price)[0]
                price = re.compile(r'(\d+\.{0,1}\d*)').findall(price)[0]
            except IndexError:
                print('获取price失败,请检查!')
                raise IndexError

            if taobao_price == '' or price == '':
                print('获取到的taobao_price或者price为空值出错, 请检查!')
                raise Exception

            taobao_price = Decimal(taobao_price).__round__(2)
            price = Decimal(price).__round__(2)
            # print('商品促销价为: ', taobao_price, ' 商品原价为: ', price)
            data['price'] = price
            data['taobao_price'] = taobao_price

            '''
            获取每个规格对应价格跟规格以及其库存
            '''
            price_info_list = self.get_price_info_list(
                detail_name_list,
                body,
                price,
                taobao_price
            )
            # pprint(price_info_list)
            if price_info_list == '':
                raise Exception
            else:
                data['price_info_list'] = price_info_list

            '''
            是否卖光
            '''
            all_stock = int(Selector(text=body).css('dl.detail dd label em::text').extract_first())
            if all_stock == 0:
                is_delete = 1
            else:
                is_delete = 0
            data['is_delete'] = is_delete

        except Exception as e:
            print('遇到错误: ', e)
            self.result_data = {}
            return {}

        if data != {}:
            # pprint(data)
            self.result_data = data
            return data

        else:
            print('data为空!')
            self.result_data = {}  # 重置下，避免存入时影响下面爬取的赋值
            return {}

    def deal_with_data(self):
        '''
        处理得到规范的data数据
        :return: result 类型 dict
        '''
        data = self.result_data
        if data != {}:
            # 店铺名称
            shop_name = data['shop_name']

            # 掌柜
            account = ''

            # 商品名称
            title = data['title']

            # 子标题
            sub_title = data['sub_title']

            price = data['price']  # 商品价格
            taobao_price = data['taobao_price']  # 淘宝价

            # 商品标签属性名称
            detail_name_list = data['detail_name_list']

            # 要存储的每个标签对应规格的价格及其库存
            price_info_list = data['price_info_list']

            # 所有示例图片地址
            all_img_url = data['all_img_url']

            # 详细信息标签名对应属性
            p_info = data['p_info']

            # div_desc
            div_desc = data['div_desc']

            # 用于判断商品是否已经下架
            is_delete = data['is_delete']

            result = {
                # 'goods_url': data['goods_url'],         # goods_url
                'shop_name': shop_name,                 # 店铺名称
                'account': account,                     # 掌柜
                'title': title,                         # 商品名称
                'sub_title': sub_title,                 # 子标题
                'price': price,                         # 商品价格
                'taobao_price': taobao_price,           # 淘宝价
                # 'goods_stock': goods_stock,            # 商品库存
                'detail_name_list': detail_name_list,   # 商品标签属性名称
                # 'detail_value_list': detail_value_list,# 商品标签属性对应的值
                'price_info_list': price_info_list,     # 要存储的每个标签对应规格的价格及其库存
                'all_img_url': all_img_url,             # 所有示例图片地址
                'p_info': p_info,                       # 详细信息标签名对应属性
                'div_desc': div_desc,                   # div_desc
                'is_delete': is_delete                  # 用于判断商品是否已经下架
            }
            # pprint(result)
            # print(result)
            # wait_to_send_data = {
            #     'reason': 'success',
            #     'data': result,
            #     'code': 1
            # }
            # json_data = json.dumps(wait_to_send_data, ensure_ascii=False)
            # print(json_data)
            return result

        else:
            print('待处理的data为空的dict, 该商品可能已经转移或者下架')
            return {}

    def insert_into_chuchujie_xianshimiaosha_table(self, data, pipeline):
        data_list = data
        tmp = {}
        tmp['goods_id'] = data_list['goods_id']  # 官方商品id
        tmp['spider_url'] = data_list['goods_url']  # 商品地址

        '''
        时区处理，时间处理到上海时间
        '''
        tz = pytz.timezone('Asia/Shanghai')  # 创建时区对象
        now_time = datetime.datetime.now(tz)
        # 处理为精确到秒位，删除时区信息
        now_time = re.compile(r'\..*').sub('', str(now_time))
        # 将字符串类型转换为datetime类型
        now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')

        tmp['deal_with_time'] = now_time  # 操作时间
        tmp['modfiy_time'] = now_time  # 修改时间

        tmp['shop_name'] = data_list['shop_name']  # 公司名称
        tmp['title'] = data_list['title']  # 商品名称
        tmp['sub_title'] = data_list['sub_title']

        # 设置最高价price， 最低价taobao_price
        try:
            tmp['price'] = Decimal(data_list['price']).__round__(2)
            tmp['taobao_price'] = Decimal(data_list['taobao_price']).__round__(2)
        except:
            print('此处抓到的可能是楚楚街券所以跳过')
            return None

        tmp['detail_name_list'] = data_list['detail_name_list']  # 标签属性名称

        """
        得到sku_map
        """
        tmp['price_info_list'] = data_list.get('price_info_list')  # 每个规格对应价格及其库存

        tmp['all_img_url'] = data_list.get('all_img_url')  # 所有示例图片地址

        tmp['p_info'] = data_list.get('p_info')  # 详细信息
        tmp['div_desc'] = data_list.get('div_desc')  # 下方div

        tmp['miaosha_time'] = data_list.get('miaosha_time')
        tmp['gender'] = data_list.get('gender')
        tmp['page'] = data_list.get('page')

        # 采集的来源地
        tmp['site_id'] = 24  # 采集来源地(楚楚街9.9，19.9，29.9秒杀商品)

        tmp['miaosha_begin_time'] = data_list.get('miaosha_begin_time')
        tmp['miaosha_end_time'] = data_list.get('miaosha_end_time')

        tmp['is_delete'] = data_list.get('is_delete')  # 逻辑删除, 未删除为0, 删除为1
        # print('is_delete=', tmp['is_delete'])

        # print('------>>> | 待存储的数据信息为: |', tmp)
        print('------>>>| 待存储的数据信息为: |', tmp.get('goods_id'))

        pipeline.insert_into_chuchujie_xianshimiaosha_table(tmp)

    def update_chuchujie_xianshimiaosha_table(self, data, pipeline):
        data_list = data
        tmp = {}
        tmp['goods_id'] = data_list['goods_id']  # 官方商品id

        '''
        时区处理，时间处理到上海时间
        '''
        tz = pytz.timezone('Asia/Shanghai')  # 创建时区对象
        now_time = datetime.datetime.now(tz)
        # 处理为精确到秒位，删除时区信息
        now_time = re.compile(r'\..*').sub('', str(now_time))
        # 将字符串类型转换为datetime类型
        now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')

        tmp['modfiy_time'] = now_time  # 修改时间

        tmp['shop_name'] = data_list['shop_name']  # 公司名称
        tmp['title'] = data_list['title']  # 商品名称
        # tmp['sub_title'] = data_list['sub_title']

        # 设置最高价price， 最低价taobao_price
        try:
            tmp['price'] = Decimal(data_list['price']).__round__(2)
            tmp['taobao_price'] = Decimal(data_list['taobao_price']).__round__(2)
        except:
            print('此处抓到的可能是楚楚街券所以跳过')
            return None

        tmp['detail_name_list'] = data_list['detail_name_list']  # 标签属性名称

        """
        得到sku_map
        """
        tmp['price_info_list'] = data_list.get('price_info_list')  # 每个规格对应价格及其库存

        tmp['all_img_url'] = data_list.get('all_img_url')  # 所有示例图片地址

        tmp['p_info'] = data_list.get('p_info')  # 详细信息
        tmp['div_desc'] = data_list.get('div_desc')  # 下方div

        # tmp['miaosha_time'] = data_list.get('miaosha_time')

        # 采集的来源地
        # tmp['site_id'] = 24  # 采集来源地(楚楚街9.9，19.9，29.9秒杀商品)

        # tmp['miaosha_begin_time'] = data_list.get('miaosha_begin_time')
        # tmp['miaosha_end_time'] = data_list.get('miaosha_end_time')

        tmp['is_delete'] = data_list.get('is_delete')  # 逻辑删除, 未删除为0, 删除为1
        # print('is_delete=', tmp['is_delete'])

        # print('------>>> | 待存储的数据信息为: |', tmp)
        print('------>>>| 待存储的数据信息为: |', tmp.get('goods_id'))

        pipeline.update_chuchujie_xianshimiaosha_table(tmp)

    def get_price_info_list(self, *params):
        '''
        获取每个规格对应价格跟规格以及其库存
        :param params: 待传入的参数
        :return: '' 表示出错 | [] | [{}...]
        '''
        detail_name_list, body, price, taobao_price = params
        all_stock = int(Selector(text=body).css('dl.detail dd label em::text').extract_first())
        price_info_list = []
        if detail_name_list == []:
            pass

        elif len(detail_name_list) == 1:
            len_1_i_text_list = list(Selector(text=body).css('div.info-wd.bd-red dl.detail dd.tag i::text').extract())
            for item in len_1_i_text_list:
                tmp = {}
                spec_value = item

                if spec_value == '':
                    print('spec_value为空值, 请检查!')
                    price_info_list = ''
                    break
                    # raise Exception

                normal_price = str(price)
                detail_price = str(taobao_price)
                try:
                    rest_number = int(all_stock / len(len_1_i_text_list))   # 由于获取不到每个规格库存信息，所以先用总库存除以规格的数量
                except Exception:
                    print('rest_number获取失败, 请检查!')
                    raise Exception

                tmp['spec_value'] = spec_value
                tmp['normal_price'] = normal_price
                tmp['detail_price'] = detail_price
                tmp['img_url'] = ''  # 无图
                tmp['rest_number'] = rest_number
                price_info_list.append(tmp)

        else:  # detail_name_list > 1
            tmp_list = []       # 用来暂存规格
            for item in list(Selector(text=body).css('div.info-wd.bd-red dl.detail dd.tag').extract()):
                dd_i = tuple(Selector(text=item).css('i::text').extract())
                tmp_list.append(dd_i)

            # pprint(tmp_list)
            if len(tmp_list) == 2:
                # print('### detail_name_list ### 的len = 2')
                a, b = tmp_list

                for item_1 in a:
                    for item_2 in b:
                        tmp = {}
                        if item_1 == '' or item_2 == '':
                            print('spec_value为空值, 请检查!')
                            price_info_list = ''
                            break
                            # raise Exception
                        spec_value = str(item_1) + '|' + str(item_2)

                        normal_price = str(price)
                        detail_price = str(taobao_price)
                        rest_number = int(all_stock / (len(a) * len(b)))  # 由于获取不到每个规格库存信息，所以先用总库存除以规格的数量

                        tmp['spec_value'] = spec_value
                        tmp['normal_price'] = normal_price
                        tmp['detail_price'] = detail_price
                        tmp['img_url'] = ''  # 无图
                        tmp['rest_number'] = rest_number
                        price_info_list.append(tmp)

            elif len(tmp_list) == 3:
                print('### detail_name_list ### 的len >= 3')
                a, b, c = tmp_list

                for item_1 in a:
                    for item_2 in b:
                        for item_3 in c:
                            tmp = {}
                            if item_1 == '' or item_2 == '':
                                print('spec_value为空值, 请检查!')
                                price_info_list = ''
                                break
                                # raise Exception
                            spec_value = str(item_1) + '|' + str(item_2) + '|' + str(item_3)

                            normal_price = str(price)
                            detail_price = str(taobao_price)
                            rest_number = int(all_stock / (len(a) * len(b)))  # 由于获取不到每个规格库存信息，所以先用总库存除以规格的数量

                            tmp['spec_value'] = spec_value
                            tmp['normal_price'] = normal_price
                            tmp['detail_price'] = detail_price
                            tmp['img_url'] = ''  # 无图
                            tmp['rest_number'] = rest_number
                            price_info_list.append(tmp)

            else:
                print('### detail_name_list ### 的len >= 4, 出错!请检查!')
                raise Exception

        return price_info_list

    def get_url_body(self, tmp_url):
        '''
        根据url得到body
        :param tmp_url:
        :return: body   类型str
        '''
        # 设置代理ip
        ip_object = MyIpPools()
        self.proxies = ip_object.get_proxy_ip_from_ip_pool()  # {'http': ['xx', 'yy', ...]}
        self.proxy = self.proxies['http'][randint(0, len(self.proxies) - 1)]

        tmp_proxies = {
            'http': self.proxy,
        }
        # print('------>>>| 正在使用代理ip: {} 进行爬取... |<<<------'.format(self.proxy))

        tmp_headers = self.headers
        tmp_headers['Host'] = re.compile(r'://(.*?)/').findall(tmp_url)[0]
        tmp_headers['Referer'] = 'https://' + tmp_headers['Host'] + '/'

        try:
            response = requests.get(tmp_url, headers=tmp_headers, proxies=tmp_proxies, timeout=12)  # 在requests里面传数据，在构造头时，注意在url外头的&xxx=也得先构造
            body = response.content.decode('utf-8')

            body = re.compile('\t').sub('', body)
            body = re.compile('  ').sub('', body)
            body = re.compile('\r\n').sub('', body)
            body = re.compile('\n').sub('', body)
            # print(body)
        except Exception:
            print('requests.get()请求超时....')
            print('data为空!')
            body = ''

        return body

    def get_goods_id_from_url(self, chuchujie_url):
        '''
        得到goods_id
        :param chuchujie_url:
        :return: str
        '''
        # chuchujie_url = re.compile(r'http://').sub(r'https://', chuchujie_url)
        # chuchujie_url = re.compile(r';').sub('', chuchujie_url)
        # is_chuchujie_url = re.compile(r'https://m.chuchujie.com/details/detail.html').findall(chuchujie_url)
        # if is_chuchujie_url != []:
        #     if re.compile(r'https://m.chuchujie.com/details/detail.html?.*?id=(\d+).*?').findall(chuchujie_url) != []:
        #         goods_id = re.compile(r'https://m.chuchujie.com/details/detail.html?.*?id=(\d+).*?').findall(chuchujie_url)[0]
        #         # print(goods_id)
        #         print('------>>>| 得到的楚楚街商品id为:', goods_id)
        #         return goods_id
        #     else:
        #         print('获取goods_id时出错, 请检查!')
        #         return ''
        #
        # else:
        #     print('楚楚街商品url错误, 非正规的url, 请参照格式(https://m.chuchujie.com/details/detail.html)开头的...')
        #     return ''

        chuchujie_url = re.compile(r'http://').sub(r'https://', chuchujie_url)
        chuchujie_url = re.compile(r';').sub('', chuchujie_url)
        is_chuchujie_url = re.compile(r'https://wx.chuchujie.com/index.php').findall(chuchujie_url)
        if is_chuchujie_url != []:
            if re.compile(r'https://wx.chuchujie.com/index.php\?s=/WebProduct/product_detail/product_id/(\d+).*?').findall(chuchujie_url) != []:
                goods_id = re.compile(r'/product_id/(\d+).*?').findall(chuchujie_url)[0]
                # print(goods_id)
                print('------>>>| 得到的楚楚街商品id为:', goods_id)
                return goods_id
            else:
                print('获取goods_id时出错, 请检查!')
                return ''

        else:
            print('楚楚街商品url错误, 非正规的url, 请参照格式(https://wx.chuchujie.com/index.php?s=/WebProduct/product_detail/product_id/)开头的...')
            return ''

    def __del__(self):
        gc.collect()

if __name__ == '__main__':
    chuchujie_9_9 = ChuChuJie_9_9_Parse()
    while True:
        chuchujie_url = input('请输入待爬取的楚楚街商品地址: ')
        chuchujie_url.strip('\n').strip(';')
        goods_id = chuchujie_9_9.get_goods_id_from_url(chuchujie_url)
        data = chuchujie_9_9.get_goods_data(goods_id=goods_id)
        chuchujie_9_9.deal_with_data()
        # pprint(data)