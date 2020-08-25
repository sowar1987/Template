import sys
from PyQt5.QtWidgets import QApplication
# from sales_window import Sales_MainWindow  # 导入销量排行榜窗体文件中的ui类
# from heat_window import Heat_MainWindow  # 导入热评排行榜窗体文件中的ui类
from frontend.main_window import Main_MainWindow, flag  # 导入主窗体文件中的ui类
# from frontend.attention_window import Attention_MainWindow  # 导入关注窗体文件中的ui类
# from evaluate_warning_window import Evaluate_Warning_MainWindow  # 导入评价预警窗体中的ui类
# from price_warning_window import Price_Warning_MainWindow  # 导入价格预警窗体中的ui类
# from evaluation_chart_window import Evaluation_Chart_MainWindow  #导入关注商品评价分析窗体中的ui类
# from press_bar_window import Press_Bar_MainWindow  # 导入关注商品出版社占有比例窗体中的ui类
# from about_window import About_MainWindow
from deamon.crawl import Crawl  # 导入自定义爬取文件
from deamon.mysql import MySQL  # 导入自定义数据库文件
from PyQt5 import QtWidgets, QtCore, QtGui
import requests  # 导入网络请求模块
# from PyQt5.QtGui import QPalette, QPixmap, QColor  # 导入调色板、位图、颜色
import webbrowser
from threading import Thread

# 销量榜数据表名称
sales_volume_rankings_table_name = 'sales_volume_rankings'
# 热评榜数据表名称
heat_rankings_table_name = 'heat_rankings'
# 计算机与互联网图书销量榜地址
sales_volume_url = 'http://book.jd.com/booktop/0-0-0.html?category=3287-0-0-0-10001-{page}'
# 计算机与互联网图书热评排行榜地址
heat_rankings_url = 'http://book.jd.com/booktop/0-0-1.html?category=3287-0-0-1-10001-{page}'


# 显示消息提示框，参数title为提示框标题文字，message为提示信息
def messageDialog(title, message):
    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, title,
                                    message)
    msg_box.exec_()


# 主窗体初始化类
class Main(Main_MainWindow):
    def __init__(self):
        super(Main, self).__init__()
        # self.setupUi(self)

    # 左侧功能列表的事件处理方法
    def tree_itemClicked(self):
        if flag._flag == True:
            # 树形菜单item对象
            item = self.treeWidget.currentItem()
            if item.text(0) == '图书销量排行--Top100':
                self.update_rank('sales')
                # sales.open()  # 打开销量排行榜窗体

            if item.text(0) == '图书热评排行--Top100':
                self.update_rank('hot')
                # heat.open()  # 打开热评排行榜窗体
            if item.text(0) == '关注商品中、差评预警':
                evaluate.__init__()  # 初始化
                evaluate.warning()  # 处理评价预警信息
                evaluate.open()  # 打开评价预警窗体
            if item.text(0) == '关注商品价格变化预警':
                price.__init__()  # 初始化
                price.price()  # 处理价格预警信息
                price.open()  # 打开价格预警窗体

            if item.text(0) == '评价分析饼图':
                evaluation.__init__()  # 初始化
                evaluation.open()  # 打开评价分析饼图窗体

            if item.text(0) == '出版社占有比例':
                press_bar.__init__()  # 初始化
                press_bar.open()  # 打开出版社占有比例窗体
            # print(item.text(0))
            for table, url in self.dict_target.items():
                # 查询已经关注的图书数量
                attention_number = \
                    mysql.query_attention(cur, 'count(*)',
                                        table, "attention = '1'")[0][0]
                # 查询已经关注的图书信息在数据库中的id
                attention_id = mysql.query_attention(cur, 'id', table,
                                                     "attention = '1'")
                if attention_number != 0:
                    for i in range(attention_number):
                        # 查询已经关注的图书名称
                        name = mysql.query_attention(cur, 'book_name', table,
                                                     "attention = '1'")[i][0]
                        # 判断选中的名称与关注的名称是否相同
                        if item.text(0) == name:

                            # 获取书名，并将书名显示在关注窗体的编辑框内
                            self.attentionDialog(
                                '取消关注图书', '是否取消关注该图书？\n{book_name}'.format(
                                    book_name=item.text(0)),
                                attention_id[i][0], 'cancel')
                            break

    # 更新关注图书名称的显示
    def up_show_attention_name(self):
        attention_number = mysql.query_attention(
            cur, 'count(*)', sales_volume_rankings_table_name,
            "attention = '1'")[0][0]
        main.treeWidget.topLevelItem(3).child(0).setText(0, "无")
        main.treeWidget.topLevelItem(3).child(1).setText(0, "无")
        main.treeWidget.topLevelItem(3).child(2).setText(0, "无")
        # 关注图书的数据库中如果存在数据，就获取关注的图书名称并显示出来
        if attention_number != 0:
            for i in range(attention_number):
                name = mysql.query_attention(cur, 'book_name',
                                             sales_volume_rankings_table_name,
                                             "attention = '1'")[i][0]
                main.treeWidget.topLevelItem(3).child(i).setText(0, name)

    # 更新预警信息按钮的单击事件处理方法
    def up(self):
        warningDialog = QtWidgets.QMessageBox.warning(
            self, '警告', '关注商品的预警信息更新后，将以新的信息进行对比并预警！',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if warningDialog == QtWidgets.QMessageBox.Yes:
            # 查询已经关注的图书信息在数据库中的id
            attention = mysql.query_attention(
                cur, 'id,jd_id', sales_volume_rankings_table_name,
                "attention = '1'")

            for i in attention:
                # print(i)
                # 获取好评率与中评最新的时间
                good_rate, middle_time = mycrawl.get_evaluation(2, i[1])
                # 获取差评最新的时间
                good_rate, poor_time = mycrawl.get_evaluation(1, i[1])
                price = self.get_attention_price(i[1])  # 获取关注商品价格
                up = "middle_time='{mi_time}',poor_time='{p_time}',attention_price='{price}'".format(
                    mi_time=middle_time, p_time=poor_time, price=price)
                # 更新关注商品的预警信息
                mysql.update_attention(cur, sales_volume_rankings_table_name,
                                       up, " id = {id}".format(id=i[0]))
            # print('已更新预警信息！')
            main.update_status('已更新预警信息!')

    # 获取关注商品价格
    def get_attention_price(self, id):
        price_url = 'http://p.3.cn/prices/mgets?type=1&skuIds={id_str}'  # 获取价格的网络请求地址
        response = requests.get(
            price_url.format(id_str=id))  # 将京东id作为参数发送获取前100名图书价格
        price = response.json()  # 获取价格json数据，该数据为list类型
        for p in price:
            return p['op']

    # 排行榜窗体双击事件处理方法
    def rank_itemDoubleClicked(self):

        item = self.tableWidget.currentItem()  # 表格item对象
        # 判断是否是书名列
        if item.column() == 2:
            # 获取书名，并将书名显示在关注窗体的编辑框内
            self.attentionDialog(
                '关注图书', '是否关注该图书？\n{book_name}'.format(book_name=item.text()),
                0, 'check')
            # attention.lineEdit.setText(item.text())
            # attention.open()  # 显示关注窗体
            # 判断是否是图片列
            pass
        if item.column() == 1:
            # 获取书名，并将书名显示在关注窗体的编辑框内
            # 关注表格中图书所对应的id,因为表格数据与数据库内容相同，表格中的第0行是数据库中id为1的数据
            row = self.tableWidget.currentItem().row() + 1
            item_url = mysql.query_book_url(cur,
                                            sales_volume_rankings_table_name,
                                            row)
            webbrowser.open(item_url)

    # 排行榜窗体单击事件处理方法
    def rank_itemClicked(self):
        # print(self.label_title.text())
        if self.label_title.text() == '计算机与互联网图书销量排行榜':
            table_name = 'sales_volume_rankings'
            ranktype = '京东热销榜'
            self.show_preview(table_name, ranktype)
        elif self.label_title.text() == '计算机与互联网图书热评排行榜':
            table_name = 'heat_rankings'
            ranktype = '京东热评榜'
            self.show_preview(table_name, ranktype)

    def show_preview(self, table_name, ranktype):
        # 判断是否是书名列
        item = self.tableWidget.currentItem()  # 表格item对象
        if item.column() == 1:
            # 获取书名，并将书名显示在关注窗体的编辑框内
            # 关注表格中图书所对应的id,因为表格数据与数据库内容相同，表格中的第0行是数据库中id为1的数据
            row = self.tableWidget.currentItem().row() + 1
            item_jd_id = mysql.query_select_id(cur, table_name, row)
            img_path = sys.path[0][0:sys.path[0].rfind(
                '/src')] + '/src/download_data/picture/{ranktype}/'.format(
                    ranktype=ranktype) + item_jd_id + '.jpg'
            self.label.setFixedSize(350, 350)
            jpg = QtGui.QPixmap(img_path).scaled(self.label.width(),
                                                 self.label.height())
            self.label.setPixmap(jpg)
            # self.label.setPalette(palette)  # 为控件设置对应的调色板即可

    def attentionDialog(self, title, message, a_id, a_type):
        warningDialog = QtWidgets.QMessageBox.warning(
            self, title, message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if a_type == 'check':
            if warningDialog == QtWidgets.QMessageBox.Yes:
                self.insert_attention_message()
        if a_type == 'cancel':
            if warningDialog == QtWidgets.QMessageBox.Yes:
                # 在数据库中取消关注标记
                mysql.update_attention(cur, sales_volume_rankings_table_name,
                                       "attention='0'",
                                       " id = {id}".format(id=a_id))
                self.up_show_attention_name()
                if title != '无':
                    self.update_status('已取消关注图书《' + title + '》!')

    # 获取关注图书的预警信息,并进行关注
    def insert_attention_message(self):
        # 关注表格中图书所对应的id,因为表格数据与数据库内容相同，表格中的第0行是数据库中id为1的数据
        rows = main.tableWidget.currentItem().row() + 1
        # 准备关注的图书名称
        name = main.tableWidget.currentItem().text()
        # 查询已经关注的图书数量
        attention_number = \
            mysql.query_attention(cur, 'count(*)', sales_volume_rankings_table_name, "attention = '1'")[0][0]
        # 根据id查询图书是否已关注
        is_attention = \
            mysql.query_attention(cur, 'attention', sales_volume_rankings_table_name, "id={id}".format(id=rows))[0][0]
        # 查询已关注图书的jd_id
        jd_id = mysql.query_attention(cur, 'jd_id',
                                      sales_volume_rankings_table_name,
                                      "id={id}".format(id=rows))[0][0]
        # 获取好评率与中评最新的时间
        good_rate, middle_time = mycrawl.get_evaluation(2, jd_id)
        # 获取差评最新的时间
        good_rate, poor_time = mycrawl.get_evaluation(1, jd_id)
        # 获取关注商品的现在价格
        price = mysql.query_attention(cur, 'jd_price',
                                      sales_volume_rankings_table_name,
                                      "id={id}".format(id=rows))[0][0]
        # 判断是否有已经关注的图书
        if is_attention != '1':
            if attention_number <= 2:
                up = "middle_time='{mi_time}',poor_time='{p_time}',attention_price='{an_price}',attention='1'".format(
                    mi_time=middle_time, p_time=poor_time, an_price=price)
                # 更新数据库中的关注信息
                mysql.update_attention(cur, sales_volume_rankings_table_name,
                                       up, " id = {id}".format(id=rows))
                main.treeWidget.topLevelItem(3).child(
                    attention_number).setText(0, name)
                # print('已关注图书《' + name + '》!')
                main.update_status('已关注图书《' + name + '》!')
                # self.close()
            else:
                messageDialog('警告！', '仅可以关注3本图书！')
                # print('仅可以关注3本图书！')
                main.update_status('仅可以关注3本图书!')
                # self.close()
        else:
            messageDialog('警告！', '不可以关注相同的图书！')
            # self.close()
            # print('不可以关注相同的图书！')
            main.update_status('不可以关注相同的图书!')


# # 评价预警窗体初始化类
# class Evaluate_Warning(Evaluate_Warning_MainWindow):
#     def __init__(self):
#         super(Evaluate_Warning, self).__init__()
#         # self.setupUi(self)

#     # 打开窗体
#     def open(self):
#         self.show()

#     def warning(self):
#         warning_list = []  # 保存评价分析后得数据
#         # 查询关注图书的信息，其中包含图书名称，中评时间与差评时间
#         attention_message = mysql.query_attention(
#             cur, 'book_name,middle_time,poor_time,jd_id',
#             sales_volume_rankings_table_name, "attention = '1'")
#         # 判断是否有关注图书的信息
#         if len(attention_message) != 0:
#             middle_time = ''
#             poor_time = ''
#             for i in range(len(attention_message)):
#                 # 获取好评率与中评最新的时间
#                 good_rate, new_middle_time = mycrawl.get_evaluation(
#                     2, attention_message[i][3])
#                 # # 获取差评最新的时间
#                 good_rate, new_poor_time = mycrawl.get_evaluation(
#                     1, attention_message[i][3])
#                 if attention_message[i][1] == new_middle_time:
#                     middle_time = '无'
#                 else:
#                     middle_time = '有'
#                 if attention_message[i][2] == new_poor_time:
#                     poor_time = '无'
#                 else:
#                     poor_time = '有'
#                 warning_list.append(
#                     (attention_message[i][0], middle_time, poor_time))
#             for i in range(len(attention_message)):
#                 for j in range(3):
#                     temp_data = warning_list[i][j]  # 临时记录，不能直接插入表格
#                     data = QtWidgets.QTableWidgetItem(
#                         str(temp_data))  # 转换后可插入表格
#                     data.setTextAlignment(QtCore.Qt.AlignCenter)
#                     evaluate.tableWidget.setItem(i, j, data)

# # 价格预警窗体初始化类
# class Price_Warning(Price_Warning_MainWindow):
#     def __init__(self):
#         super(Price_Warning, self).__init__()
#         # self.setupUi(self)

#     # 打开窗体
#     def open(self):
#         self.show()

#     # 价格信息处理
#     def price(self):
#         price_list = []  # 保存价格分析后的数据
#         # 查询关注图书的信息，其中包含图书的京东价格以及京东id
#         attention_message = mysql.query_attention(
#             cur, 'attention_price,jd_id,book_name',
#             sales_volume_rankings_table_name, "attention = '1'")
#         # # # 判断是否有关注图书的信息
#         if len(attention_message) != 0:
#             jd_id_str = ''
#             for i in range(len(attention_message)):
#                 jd_id = 'J_' + attention_message[i][1] + ','
#                 jd_id_str = jd_id_str + jd_id
#             price_url = 'http://p.3.cn/prices/mgets?type=1&skuIds={id_str}'
#             response = requests.get(
#                 price_url.format(id_str=jd_id_str))  # 将京东id作为参数发送获取前100名图书价格
#             price_json = response.json()  # 获取价格json数据，该数据为list类型
#             change = ''
#             for index, item in enumerate(price_json):
#                 # 京东价格
#                 new_jd_price = item['op']
#                 if float(attention_message[index][0]) < float(new_jd_price):
#                     change = '上涨'
#                 if float(attention_message[index][0]) == float(new_jd_price):
#                     change = '无'
#                 if float(attention_message[index][0]) > float(new_jd_price):
#                     change = '下浮'
#                 price_list.append((attention_message[index][2], change))
#             for i in range(len(attention_message)):
#                 for j in range(2):
#                     temp_data = price_list[i][j]  # 临时记录，不能直接插入表格
#                     data = QtWidgets.QTableWidgetItem(
#                         str(temp_data))  # 转换后可插入表格
#                     data.setTextAlignment(QtCore.Qt.AlignCenter)
#                     price.tableWidget.setItem(i, j, data)

# # 评价分析图窗体初始化类
# class Evaluation_Chart(Evaluation_Chart_MainWindow):
#     def __init__(self):
#         super(Evaluation_Chart, self).__init__()
#         # self.setupUi(self)

#     # 打开窗体
#     def open(self):
#         self.show()

# # 出版社占有比例窗体初始化类
# class Press_Bar(Press_Bar_MainWindow):
#     def __init__(self):
#         super(Press_Bar, self).__init__()
#         # self.setupUi(self)

#     # 打开窗体
#     def open(self):
#         self.show()

# # 关于窗体初始化类
# class About_Window(About_MainWindow):
#     def __init__(self):
#         super(About_Window, self).__init__()
#         # self.setupUi(self)

#     # 打开窗体
#     def open(self):
#         self.show()

if __name__ == "__main__":
    # 创建自定义数据库对象
    mysql = MySQL()
    #创建table_name表
    table_name = sales_volume_rankings_table_name
    sql_fields = """
            create table {table_name}(
            id int not null,
            book_name   char(45),
            jd_price    char(45),
            ding_price  char(45),
            press       char(45),
            item_url    char(45),
            item_picture    char(127),
            jd_id       char(45),
            middle_time char(45),
            poor_time   char(45),
            attention_price  char(45),
            attention   char(45))
        """.format(table_name=table_name)
    mysql.create_table(table_name, sql_fields)
    table_name = heat_rankings_table_name
    sql_fields = """
            create table {table_name}(
            id int not null,
            book_name   char(45),
            jd_price    char(45),
            ding_price  char(45),
            press       char(45),
            item_url    char(45),
            item_picture    char(127),
            jd_id       char(45),
            middle_time char(45),
            poor_time   char(45),
            attention_price  char(45),
            attention   char(45))
        """.format(table_name=table_name)
    mysql.create_table(table_name, sql_fields)
    # 创建爬虫对象
    mycrawl = Crawl()
    # 连接数据库
    # sql = mysql.connection_sql()
    # 连接数据库并创建游标
    cur = mysql.connection_sql().cursor()
    # QApplication相当于main函数，也就是整个程序（很多文件）的主入口函数。
    # 对于GUI程序必须至少有一个这样的实例来让程序运行。
    app = QApplication(sys.argv)
    #生成Main类的实例。
    main = Main()

    # 显示主窗体
    #有了实例，就得让它显示，show()是QWidget的方法，用于显示窗口。
    main.show()
    # # 销量排行窗体对象
    # sales = Sales()
    # # 热评排行窗体对象
    # heat = Heat()

    # # 评价预警窗体对象
    # evaluate = Evaluate_Warning()
    # # 价格预警窗体对象
    # price = Price_Warning()
    # # 关注图书评价分析图窗体对象
    # evaluation = Evaluation_Chart()

    # # 出版社占有比例窗体对象
    # press_bar = Press_Bar()

    # # 关于窗体对象
    # about = About_Window()

    # # 指定菜单栏关于选项单击事件处理方法
    # main.action_about.triggered.connect(about.open)

    # 指定左侧树形菜单的事件处理方法
    main.treeWidget.itemClicked['QTreeWidgetItem*',
                                'int'].connect(main.tree_itemClicked)
    # 指定更新商品排行信息按钮的事件处理方法
    main.pushButton.clicked.connect(main.up)

    # 指定排行榜表格的双击事件处理方法
    main.tableWidget.itemDoubleClicked.connect(main.rank_itemDoubleClicked)

    # 指定排行榜表格的单击事件处理方法
    main.tableWidget.itemClicked.connect(main.rank_itemClicked)

    # # 指定热评榜表格的双击事件处理方法
    # heat.tableWidget.itemDoubleClicked.connect(heat.heat_itemDoubleClicked)

    flag.valueChanged.connect(main.update_charts)
    # time.sleep(10)
    #  初始化数据库
    p = Thread(target=main.init_database, args=())
    p.start()
    # p.join()

    # 调用sys库的exit退出方法，条件是app.exec_()，也就是整个窗口关闭。
    # 有时候退出程序后，sys.exit(app.exec_())会报错，改用app.exec_()就没事
    # https://stackoverflow.com/questions/25719524/difference-between-sys-exitapp-exec-and-app-exec
    sys.exit(app.exec_())
