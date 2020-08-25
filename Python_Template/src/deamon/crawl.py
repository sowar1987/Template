import requests  #  导入网络请求模块
from bs4 import BeautifulSoup  #  解析HTML模块
import json  #解析json数据的模块
import re  #正则表达式
import sys
import os
rankings_list = []  #保存排行榜数据的列表


class Crawl(object):
    #创建头部信息
    headers = {
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/83.0.4103.61 Chrome/83.0.4103.61 Safari/537.36'
    }

    def get_rankings(self, url):

        self.book_name_list = []  #  保存图书名称的列表
        self.press_list = []  #  保存出版社的列表
        self.item_url_list = []  #   保存排行中每本书的地址
        self.item_picture_list = []  #   保存排行中每本书图片的地址
        self.jd_id_list = []  #  保存京东ID的列表
        #  网页的页数
        page = 1
        #  100个京东ID的字符串，该字符串是前100名的京东商品ID
        self.jd_id_str_100 = ''
        #  因为前100名，每个网页显示20名，所以发送5次网页请求，每次请求不同的网页
        while True:
            #  发送网络请求，获取服务器响应
            response = requests.get(url.format(page=page),
                                    headers=self.headers)
            response.encoding = 'gb2312'  # 设置编码方式
            # 创建一个BeautifulSoup对象，获取页面正文
            html = BeautifulSoup(response.text, "html.parser")
            book_list = html.find('div', {'class', 'm m-list'})
            if not book_list:
                break
            book_list = book_list.find('ul',
                                       {'class', 'clearfix'}).select('li')
            # 获取图书所有信息
            # print('book_list',len(book_list))
            # 页数+1
            page += 1
            # 每页20个京东id
            jd_id_str_20 = ''
            for i in book_list:
                # 获取图书id
                jd_id = i.find(
                    'a', {'class', 'btn btn-default follow'}).get('data-id')
                # 获取图书名称
                book_name = i.find('a', {'class', 'p-name'}).text
                # 获取图书出版社
                press = i.find('div',
                               {'class', 'p-detail'}).find_all('dl')[1].dd.text
                item_url = i.find('div',
                                  {'class', 'p-img'}).find('a').get('href')
                item_url = 'http:' + item_url
                # print(i)
                item_picture = i.find(
                    'div', {'class', 'p-img'}).find('img').get('data-lazy-img')
                item_picture = 'http:' + item_picture

                self.book_name_list.append(book_name)  # 将图书名称添加至列表
                self.press_list.append(press)  # 将出版社添加至列表
                self.item_url_list.append(item_url)  # 将排行中每本书地址添加至列表
                self.item_picture_list.append(item_picture)  # 将排行中每本书地址添加至列表
                self.jd_id_list.append(jd_id)  # 将排行中每本书的京东id添加至列表
                # 京东商品id
                jd_id_str = 'J_' + jd_id + ','
                jd_id_str_20 = jd_id_str_20 + jd_id_str
            # 将获取到的100个京东id连接成字符串作为获取价格的请求参数
            self.jd_id_str_100 = self.jd_id_str_100 + jd_id_str_20
        return self.jd_id_str_100

    # 获取前100名图书价格
    def get_price(self, id, S_H):
        rankings_list.clear()  # 清空排行数据的列表
        price_url = 'http://p.3.cn/prices/mgets?type=1&skuIds={id_str}'  # 获取价格的网络请求地址
        response = requests.get(
            price_url.format(id_str=id))  # 将京东id作为参数发送获取前100名图书价格
        price = response.json()  # 获取价格json数据，该数据为list类型
        for index, item in enumerate(price):
            # 书名
            book_name = self.book_name_list[index]
            # 出版社
            press = self.press_list[index]
            # 京东价格
            jd_price = item['op']
            # 定价
            ding_price = item['m']
            # 每本书的地址
            item_url = self.item_url_list[index]
            # 每本书的图片地址
            item_picture = self.item_picture_list[index]

            # 每本书的京东id
            jd_id = self.jd_id_list[index]

            #  下载并保存图书图片
            #  下载图片存放路径
            img_path = str('{0}/download_data/picture/'.format(
                sys.path[0])) + S_H
            self.download_img(item_picture, jd_id, img_path)

            # 将所有数据添加到列表中
            rankings_list.append((index + 1, book_name, jd_price, ding_price,
                                  press, item_url, item_picture, jd_id))

    # 获取评价内容,score参数差评为1、中评为2、好评为3，0为全部
    def get_evaluation(self, score, id):
        # 好评率
        self.good_rate_show = None
        # 评价请求地址参数，callback为对应书名json的id，
        # productId书名对应的京东id
        # score评价等级参数差评为1、中评为2、好评为3，0为全部
        # sortType类型，6为时间排序，5为推荐排序
        # pageSize每页显示评价10条
        # page页数
        params = {
            'callback': 'fetchJSON_comment98vv10635',
            'productId': id,
            'score': score,
            'sortType': 6,
            'pageSize': 10,
            'isShadowSku': 0,
            'page': 0,
        }
        # 评价请求地址
        url = 'https://club.jd.com/comment/skuProductPageComments.action'
        # 发送请求
        evaluation_response = requests.get(url, params=params)
        if evaluation_response.status_code == 200:
            evaluation_response = evaluation_response.text
            try:
                # 去除json外层的括号与名称
                t = re.search(r'({.*})', evaluation_response).group(0)
            except Exception as e:
                print('评价的json数据匹配异常！')
            j = json.loads(t)  # 加载json数据
            commentSummary = j['comments']
            if self.good_rate_show == None:
                self.good_rate_show = j['productCommentSummary'][
                    'goodRateShow']
            for comment in commentSummary:
                # 评价内容
                c_contetn = comment['content']
                # 时间
                c_time = comment['creationTime']
                # 京东昵称
                c_name = comment['nickname']
                # 通过哪种平台购买
                # c_client = comment['userClientShow']
                # 会员级别
                # c_userLevelName = comment['userLevelName']
                # 好评差评 1差评 2-3 中评 4-5好评
                c_score = comment['score']
                # print(
                #     '\n{} {} {} {}  {}\n{}\n'.format(c_name, c_userLevelName, c_time, str(c_score) + '颗星', c_client,
                #                                         c_contetn))
            # 判断没有指定的评价内容时
            if len(commentSummary) == 0:
                # 返回好评率与无
                return self.good_rate_show, '无'
            else:
                # 根据不同需求返回不同数据，这里仅返回好评率与最新的评价时间
                return self.good_rate_show, commentSummary[0]['creationTime']

    def download_img(self, img_url, jd_id, img_path):
        # print(img_url)
        # header = {"Authorization": "Bearer " + api_token} # 设置http header，视情况加需要的条目，这里的token是用来鉴权的一种方式
        r = requests.get(img_url, headers=self.headers, stream=True)

        if not os.path.exists(img_path):
            os.makedirs(img_path)

        # print(r.status_code)  # 返回状态码
        if r.status_code == 200:
            open(img_path + jd_id + img_url[-4:],
                 'wb').write(r.content)  # 将内容写入图片
            # print("done")
        del r
