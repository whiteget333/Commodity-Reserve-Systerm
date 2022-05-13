# -*- coding:utf8 -*-
import time

import pymssql
import PySide2
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt, QRegExp
from PySide2.QtGui import QBrush, QColor, QRegExpValidator
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QAction, QInputDialog, QLineEdit
import os
from share import PARAM, is_number
from My_Sql import sql_insert, sql_select, sql_delete, sql_update, cursor, connect, cursor_init

dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

'''
Administrators:
202215112  123456
202215113  123123
Customer:
ggggg 12345gg
dddbbb 123123
bbbddd 123456
'''

class Detail_Window:
    def __init__(self):
        self.ui = QUiLoader().load('ui/order_detail.ui')
        self.ui.pushButton_next.setText('确认签收')
        self.ui.pushButton_close.clicked.connect(self.ui.close)
        self.ui.pushButton_next.clicked.connect(self.ack)
        self.ui.pushButton_cancel.clicked.connect(self.cancel)
        self.ui.pushButton_cancel.setEnabled(True)
        self.ui.pushButton_next.setEnabled(True)

        self.rid = None
        self.state = None

    def detail_show(self, rid, state):
        self.rid = rid
        self.state = state
        self.button_set()
        self.ui.detail_table.setRowCount(0)
        ans = PARAM.select_handle.select_order_detail_rid(rid)  # Rid, Gid, Gnumber, Gprice
        result = []
        cost = 0
        for a in ans:
            name = PARAM.select_handle.select_good_gid(a[1])[0][1]
            cost += a[3]
            result.append([name, str(a[2]), str(a[3])])
        for i in range(len(result)):
            self.ui.detail_table.insertRow(i)
            for j in range(len(result[i])):
                item = QTableWidgetItem(str(result[i][j]))
                item.setFlags(Qt.ItemIsEnabled)  # 参数名字段不允许修改
                self.ui.detail_table.setItem(i, j, item)
        self.ui.label_cost.setText(str(cost))

    def button_set(self, ):
        if self.state != '已发货':
            self.ui.pushButton_next.setText(self.state)
            self.ui.pushButton_next.setEnabled(False)

        if self.state == '已付款':
            self.ui.pushButton_cancel.setText('取消订单')

        elif self.state == '已发货':
            self.ui.pushButton_cancel.setText('申请退货')
        else:
            self.ui.pushButton_cancel.setText(self.state)
            self.ui.pushButton_cancel.setEnabled(False)

    def ack(self):
        PARAM.update_handle.update_reserve_state(self.rid, '已签收')
        self.ui.pushButton_next.setText('已签收')
        self.ui.pushButton_next.setEnabled(False)

    def cancel(self):
        button_fun = self.ui.pushButton_cancel.text()
        if button_fun == '取消订单':
            choice = QMessageBox.question(self.ui, '确认', '确认取消订单吗?')
            if choice == QMessageBox.Yes:
                PARAM.update_handle.update_reserve_state(self.rid, '已取消')
                self.ui.close()
        elif button_fun == '申请退货':
            self.reject()

    def reject(self):
        choice = QMessageBox.question(self.ui, '确认', '确认申请退货吗?')
        if choice == QMessageBox.Yes:
            PARAM.update_handle.update_reserve_state(self.rid, '退货申请')
            self.ui.close()


class Enroll_Window:
    def __init__(self):
        self.ui = QUiLoader().load('ui/enroll.ui')
        self.ui.enroll_Button.clicked.connect(self.enroll)
        self.init_line()

    def init_line(self):
        rx = QRegExp("[0-9a-zA-Z]*")
        self.ui.id_line.setValidator(QRegExpValidator(rx))
        self.ui.id_line.setMaxLength(10)
        self.ui.key_line.setValidator(QRegExpValidator(rx))
        self.ui.key_line_2.setValidator(QRegExpValidator(rx))
        self.ui.key_line.setMaxLength(20)
        self.ui.key_line_2.setMaxLength(20)
        rx_2 = QRegExp("[0-9]*")
        self.ui.phone_line.setValidator(QRegExpValidator(rx_2))
        self.ui.phone_line.setMaxLength(11)
        self.ui.name_line.setMaxLength(10)
        self.ui.add_line.setMaxLength(25)

    def enroll(self):
        # 获取输入信息
        cusid = self.ui.id_line.text()
        password = self.ui.key_line.text()
        password_2 = self.ui.key_line_2.text()
        name = self.ui.name_line.text()
        phone = self.ui.phone_line.text()
        address = self.ui.add_line.text()
        if cusid and password and password_2 and name and phone and address:
            # 查看两次密码是否一致
            if password_2 != password:
                QMessageBox.critical(self.ui, '错误', '两次输入密码不一致')
            else:
                # 向Cus_pass表，Customers表插入信息
                if PARAM.insert_handle.insert_customers(cusid, name, phone, address) and PARAM.insert_handle.insert_cus_pass(cusid, password):
                    # 插入成功
                    QMessageBox.information(self.ui, '成功', '注册成功')
                    self.ui.close()
                else:
                    QMessageBox.critical(self.ui, '失败', '注册失败')
        else:
            QMessageBox.critical(self.ui, '错误', '请输入注册信息')


class Change_Win:
    def __init__(self, userid):
        self.ui = QUiLoader().load('ui/change.ui')
        self.ui.pushButton.clicked.connect(self.change)
        self.ui.pushButton_2.clicked.connect(self.ui.close)
        self.init_line()

        self.userid = userid

    def init_line(self):
        rx = QRegExp("[0-9a-zA-Z]*")
        self.ui.new_line.setValidator(QRegExpValidator(rx))
        self.ui.new_line.setMaxLength(20)
        self.ui.new_line_2.setValidator(QRegExpValidator(rx))
        self.ui.new_line_2.setMaxLength(20)

    def change(self):
        old = self.ui.old_line.text()
        new = self.ui.new_line.text()
        new_2 = self.ui.new_line_2.text()
        old_2 = PARAM.select_handle.select_pass_based_cusid(self.userid)[0][0]
        if old != old_2:
            QMessageBox.critical(self.ui, '错误', '原密码错误')
        elif new == new_2:
            PARAM.update_handle.update_password(self.userid, new)
            QMessageBox.information(self.ui, '成功', '修改成功')
            self.ui.close()
        else:
            QMessageBox.critical(self.ui, '错误', '两次输入密码不一致')


class insertgood_Window:
    def __init__(self):
        self.ui = QUiLoader().load('ui/insertgood.ui')
        self.ui.pushButton.clicked.connect(self.insert_good)

    def insert_good(self):
        gid = self.ui.lineEdit.text()
        name = self.ui.lineEdit_2.text()
        price = self.ui.lineEdit_3.text()
        stock = self.ui.lineEdit_4.text()
        if not PARAM.insert_handle.insert_good(gid, name, price, stock):
            QMessageBox.critical(self.ui, '失败', '添加失败')
        else:
            self.ui.close()


class LoginWindow:
    def __init__(self):
        self.ui = QUiLoader().load('ui/Login.ui')
        self.ui.Button_adm.clicked.connect(self.login_adm)
        self.ui.Button_cus.clicked.connect(self.login_cus)
        self.ui.enrollButton.clicked.connect(self.enroll)

        self.enroll_win = Enroll_Window()

    def login_adm(self):
        userid = self.ui.lineEdit_userid.text()
        password = self.ui.lineEdit_key.text()
        info = PARAM.select_handle.select_adm_top()
        for adm in info:
            if userid == adm[0] and password == adm[1]:
                PARAM.Amd_win = Adminis_Window(userid)
                PARAM.Amd_win.ui.show()
                self.ui.close()
                return
        QMessageBox.critical(self.ui, '错误', '用户名或密码错误')

    def login_cus(self):
        userid = self.ui.lineEdit_userid.text()  # 获取输入的账号
        password = self.ui.lineEdit_key.text()  # 获取输入的密码
        # 在Cus_pass表中搜索(userid, password)
        flag = PARAM.select_handle.select_cus_pass_top(userid, password)
        if not flag:
            # 没有相关账号和密码
            QMessageBox.critical(self.ui, '错误', '用户名或密码错误')
        else:
            # 查询到相关账号和密码
            PARAM.Cus_win = Customer_Window(userid)
            PARAM.Cus_win.ui.show()
            self.ui.close()

    def enroll(self):
        self.enroll_win.ui.show()


class Customer_Window(QtWidgets.QMainWindow):
    def __init__(self, cusid):
        super().__init__()
        self.ui = QUiLoader().load('ui/Customer.ui')
        self.ui.id_label.setText(cusid)
        # 登录cus用户
        cursor_init('cus')
        self.ui.treeWidget.itemClicked.connect(self.handle)  # stackwidget界面切换，显示相应信息
        self.ui.good_table.clicked.connect(self.buy_good)    # 购买商品
        self.ui.shop_table.clicked.connect(self.delete_good)    # 从购物车中移除
        self.ui.reserve_table.clicked.connect(self.reserve_detail)    # 查看订单详情
        self.ui.pushButton_good.clicked.connect(self.seek_good)    # 搜索商品
        self.ui.pushButton_pay.clicked.connect(self.pay)    # 支付
        self.ui.pushButton_myr.clicked.connect(self.seek_myr)    # 搜索我的订单
        self.ui.toolButton.clicked.connect(self.change_key)    # 修改密码
        self.detail_win = Detail_Window()  # 订单详情界面
        self.change_win = Change_Win(cusid)    # 修改密码界面
        # 购物车
        self.shop = []
        self.cost = 0
        self.cusid = cusid
        # stackwidget界面索引
        self.good_page = 0
        self.shop_page = 1
        self.reserve_page = 2


    def seek_good(self):
        name = self.ui.lineEdit_good.text()
        result = PARAM.select_handle.select_good_name(name)
        if result:
            del result[0][0]
            self.good_table_show(result)
        else:
            QMessageBox.critical(self.ui, '错误', '无此商品')

    def seek_myr(self):
        rid = self.ui.lineEdit_myr.text()
        result = PARAM.select_handle.select_reserve_cusid_rid(rid, self.cusid)
        self.reserve_table_show(result)

    def change_key(self):
        self.change_win.ui.show()

    def handle(self, item):
        name = item.text(0)
        treelist = {
            "商品目录": "self.all_good",
            "购物车": "self.shop_table_show",

            "我的订单": "self.all_order",
            "已付款": "self.order_state",
            "已发货": "self.order_state",
            "已签收": "self.order_state",
            "退货申请": "self.order_state",
            "退货中": "self.order_state",
            "已退货": "self.order_state",
            "已取消": "self.order_state",
        }

        method = treelist.get(name)
        if method:
            eval(method)(name)

    def table_show(self, table, result):
        table.setRowCount(0)
        for i in range(len(result)):
            table.insertRow(i)
            for j in range(len(result[i])):
                item = QTableWidgetItem(str(result[i][j]))
                item.setFlags(Qt.ItemIsEnabled)  # 参数名字段不允许修改
                table.setItem(i, j, item)

    def good_table_show(self, result):
        self.ui.stackedWidget.setCurrentIndex(self.good_page)
        for i in range(len(result)):
            result[i][-1] = '购买'

        self.table_show(self.ui.good_table, result)
        for i in range(len(result)):
            self.ui.good_table.item(i, 2).setTextAlignment(Qt.AlignCenter)
            self.ui.good_table.item(i, 2).setForeground(QBrush(QColor(0, 0, 255)))

    def shop_table_show(self, _):
        self.ui.stackedWidget.setCurrentIndex(self.shop_page)
        self.table_show(self.ui.shop_table, self.shop)
        for i in range(len(self.shop)):
            self.ui.shop_table.item(i, 3).setTextAlignment(Qt.AlignCenter)
            self.ui.shop_table.item(i, 3).setForeground(QBrush(QColor(0, 0, 255)))
        self.ui.label_cost.setText(str(self.cost)+'元')

    def reserve_table_show(self, result):
        self.ui.stackedWidget.setCurrentIndex(self.reserve_page)
        for i in range(len(result)):
            del result[i][1]
            result[i].append('查看详情')
        self.table_show(self.ui.reserve_table, result)
        for i in range(len(result)):
            self.ui.reserve_table.item(i, 7).setTextAlignment(Qt.AlignCenter)
            self.ui.reserve_table.item(i, 7).setForeground(QBrush(QColor(0, 0, 255)))

    def pay(self):
        choice = QMessageBox.question(self.ui, '确认', '您确认要支付吗?')
        if choice == QMessageBox.Yes:
            try:
                # 生成订单信息
                rid = str(PARAM.rid)
                count = len(self.shop)
                times = time.time()
                local_time = time.localtime(times)
                date = time.strftime("%Y-%m-%d", local_time)
                # 查询顾客地址和联系方式
                ans = PARAM.select_handle.select_customer_top(self.cusid)
                phone = ans[0][2]
                address = ans[0][3]
                # 插入订单
                flag = PARAM.insert_handle.insert_reserve(rid, self.cusid, str(count), str(self.cost), date, phone, address, '已付款')
                for good in self.shop:
                    # 插入订单详情
                    gid = PARAM.select_handle.select_good_name(good[0])[0][0]
                    flag = flag and PARAM.insert_handle.insert_order_detail(rid, gid, good[1], good[2])
                if flag:
                    # 清空购物车
                    PARAM.rid += 1
                    self.shop = []
                    self.cost = 0
                else:
                    QMessageBox.critical(self.ui, '错误', '出错了，请稍后再试')
            except:
                QMessageBox.critical(self.ui, '错误', '出错了，请稍后再试')
            self.shop_table_show(None)

    def all_good(self, _):
        result = PARAM.select_handle.select_good_view()
        self.good_table_show(result)

    def all_order(self, _):
        result = PARAM.select_handle.select_reserve_cusid(self.cusid)
        self.reserve_table_show(result)

    def order_state(self, state):
        result = PARAM.select_handle.select_reserve_cusid_state(self.cusid, state)
        self.reserve_table_show(result)

    def delete_good(self, item):
        row = item.row()
        column = item.column()
        dee = self.ui.shop_table.item(row, column).text()
        if dee == '删除':
            choice = QMessageBox.question(self.ui, '确认', '您确认要执行该操作?')
            if choice == QMessageBox.Yes:
                name = self.ui.shop_table.item(row, 0).text()
                for element in self.shop:
                    if element[0] == name:
                        self.cost -= eval(element[2])
                        self.shop.remove(element)
                        break
                self.shop_table_show(None)

    def buy_good(self, item):
        row = item.row()
        column = item.column()
        shop = self.ui.good_table.item(row, column).text()
        if shop == '购买':
            name = self.ui.good_table.item(row, 0).text()
            price = eval(self.ui.good_table.item(row, 1).text())
            # input
            number, flag = QInputDialog.getText(self.ui, "输入", "请输入购买数量", QLineEdit.Normal, "")
            if flag:
                if number and is_number(number) and number != '0':
                    number = eval(number)
                    stock = PARAM.select_handle.select_good_stock(name)[0][0]
                    if number > stock:   # 库存不足
                        QMessageBox.critical(self.ui, '错误', '库存不足，库存仅剩'+str(stock)+'个')
                    else:
                        finish = False
                        for g in self.shop:
                            if name == g[0]:
                                g[1] = str(eval(g[1])+number)
                                price = number * price
                                g[2] = str(eval(g[2])+price)
                                self.cost += price
                                finish = True
                        if not finish:
                            price = number * price
                            self.cost += price
                            good = [name, str(number), str(price), "删除"]
                            self.shop.append(good)
                else:
                    QMessageBox.critical(self.ui, '错误', '请输入商品数量')

    def reserve_detail(self, item):
        row = item.row()
        column = item.column()
        detail = self.ui.reserve_table.item(row, column).text()
        if detail == '查看详情':
            rid = self.ui.reserve_table.item(row, 0).text()
            state = self.ui.reserve_table.item(row, 6).text()
            # 显示detail
            self.detail_win.detail_show(rid, state)
            self.detail_win.ui.show()


class Adminis_Window(QtWidgets.QMainWindow):
    def __init__(self, admid):
        super().__init__()
        self.ui = QUiLoader().load('ui/Administrator.ui')
        self.admid = admid
        # 登录adm用户
        # cursor_init('adm')
        # 树控件
        self.ui.treeWidget.itemClicked.connect(self.handle)  # stackwidget界面切换，显示相应信息
        # 按钮
        self.ui.reserve_table.clicked.connect(self.change_reserve_table_state)  # 更改订单状态
        self.ui.good_table_2.itemChanged.connect(self.change_good_table)  # 更改商品信息
        self.ui.pushButton_C.clicked.connect(self.seek_cusid)  # 搜索订单，根据客户ID
        self.ui.pushButton_R.clicked.connect(self.seek_rid)  # 搜索订单，根据订单ID
        self.ui.pushButton_G.clicked.connect(self.seek_gid)  # 搜索商品，根据商品ID
        self.ui.pushButton_G_2.clicked.connect(self.seek_gid_2)  # 搜索商品，根据商品ID
        self.ui.pushButton_R_d.clicked.connect(self.delete_reserve)  # 删除订单，订单ID
        self.ui.pushButton_G_d.clicked.connect(self.delete_good)  # 删除商品，商品ID
        self.ui.pushButton_G_Add.clicked.connect(self.add_stock)  # 进货
        # 添加商品界面
        self.insert_win = insertgood_Window()
        # stackwidget界面索引
        self.good_page = 0
        self.reserve_page = 1
        self.good_page_2 = 2

    # 根据Rid删除订单
    def delete_reserve(self):
        rid = self.ui.lineEdit_R_d.text()
        if not PARAM.select_handle.select_reserve_rid(rid):
            QMessageBox.critical(self.ui, '错误', '订单ID错误')
            return
        if PARAM.delete_handle.delete_reserve(rid):
            QMessageBox.information(self.ui, '成功', '删除成功')
        else:
            QMessageBox.critical(self.ui, '错误', '删除失败')

    # 根据Gid删除商品
    def delete_good(self):
        gid = self.ui.lineEdit_G_d.text()

        if not PARAM.select_handle.select_good_gid(gid):
            QMessageBox.critical(self.ui, '错误', '商品编号错误')
            return
        if PARAM.delete_handle.delete_good(gid):
            QMessageBox.information(self.ui, '成功', '删除成功')
        else:
            QMessageBox.critical(self.ui, '错误', '删除失败')

    # 根据Rid查询订单
    def seek_rid(self):
        rid = self.ui.lineEdit_R.text()
        result = PARAM.select_handle.select_reserve_rid(rid)
        self.table_show(self.ui.reserve_table, result)

    # 根据Cusid查询订单
    def seek_cusid(self):
        cusid = self.ui.lineEdit_C.text()
        result = PARAM.select_handle.select_reserve_cusid(cusid)
        self.table_show(self.ui.reserve_table, result)

    # 根据Gid查询商品，good_page页面
    def seek_gid(self):
        gid = self.ui.lineEdit_G.text()
        result = PARAM.select_handle.select_good_gid(gid)
        self.table_show(self.ui.good_table, result)

    # 根据Gid查询商品，good_page_2页面
    def seek_gid_2(self):
        self.ui.good_table_2.blockSignals(True)
        self.ui.stackedWidget.setCurrentIndex(self.good_page_2)
        gid = self.ui.lineEdit_G.text()
        result = PARAM.select_handle.select_good_gid(gid)
        self.table_show(self.ui.good_table_2, result, True)
        self.ui.good_table_2.blockSignals(False)

    def handle(self, item):
        name = item.text(0)
        treelist = {
            "订单": "self.all_order",
            "已付款": "self.order_state",
            "已发货": "self.order_state",
            "已签收": "self.order_state",
            "退货申请": "self.order_state",
            "退货中": "self.order_state",
            "已退货": "self.order_state",
            "已取消": "self.order_state",

            "商品": "self.all_good",
            "添加商品": "self.add_good",
            "进货": "self.all_good",
            "修改商品信息": "self.update_good",
        }

        method = treelist.get(name)
        if method:
            eval(method)(name)

    # 进货
    def add_stock(self):
        number = self.ui.lineEdit_G_An.text()
        gid = self.ui.lineEdit_G_A.text()
        if number and is_number(number):
            if PARAM.update_handle.add_stock(number, gid):
                QMessageBox.information(self.ui, '成功', '入库成功')
            else:
                QMessageBox.critical(self.ui, '错误', '入库失败')
        else:
            QMessageBox.critical(self.ui, '错误', '请输入正确数量')

    # 显示所有订单
    def all_order(self, _):
        # 设置page，数据加载到表格
        result = PARAM.select_handle.select_reserve_all()
        self.reserve_table_show(result)

    # 根据订单状态显示订单
    def order_state(self, state):
        result = PARAM.select_handle.select_reserve_state(state)
        self.reserve_table_show(result)

    # 点击reserve_table事件，改变订单状态
    def change_reserve_table_state(self, item):
        row = item.row()
        column = item.column()
        state = self.ui.reserve_table.item(row, column).text()
        rid = self.ui.reserve_table.item(row, 0).text()
        if state == '已付款':
            choice = QMessageBox.question(self.ui, '确认', '是否将订单状态改为已发货？')
            if choice == QMessageBox.Yes:
                PARAM.update_handle.update_reserve_state(rid, '已发货')
                self.ui.reserve_table.item(row, column).setText('已发货')
        elif state == '退货申请':
            choice = QMessageBox.question(self.ui, '确认', '是否同意退货，并将订单状态改为退货中？')
            if choice == QMessageBox.Yes:
                PARAM.update_handle.update_reserve_state(rid, '退货中')
                self.ui.reserve_table.item(row, column).setText('退货中')
        elif state == '退货中':
            choice = QMessageBox.question(self.ui, '确认', '是否已收到退货，并将订单状态改为已退货？')
            if choice == QMessageBox.Yes:
                PARAM.update_handle.update_reserve_state(rid, '已退货')
                self.ui.reserve_table.item(row, column).setText('已退货')

    # 表格显示函数  在修改商品信息界面editable=True
    def table_show(self, table, result, editable=False):
        table.setRowCount(0)
        for i in range(len(result)):
            table.insertRow(i)
            for j in range(len(result[i])):
                if editable and j:
                    item = QTableWidgetItem(str(result[i][j]))
                    table.setItem(i, j, item)
                else:
                    item = QTableWidgetItem(str(result[i][j]))
                    item.setFlags(Qt.ItemIsEnabled)  # 参数名字段不允许修改
                    table.setItem(i, j, item)

    # reserve_table显示函数
    def reserve_table_show(self, result):
        self.ui.stackedWidget.setCurrentIndex(self.reserve_page)
        return self.table_show(self.ui.reserve_table, result)

    # 显示所有商品
    def all_good(self, _):
        self.ui.stackedWidget.setCurrentIndex(self.good_page)
        result = PARAM.select_handle.select_good_all()
        return self.table_show(self.ui.good_table, result)

    # 添加商品
    def add_good(self, _):
        self.insert_win.ui.show()

    # 进入修改商品页面
    def update_good(self, _):
        self.ui.good_table_2.blockSignals(True)
        self.ui.stackedWidget.setCurrentIndex(self.good_page_2)
        result = PARAM.select_handle.select_good_all()
        self.table_show(self.ui.good_table_2, result, True)
        self.ui.good_table_2.blockSignals(False)

    # 表格改变事件，修改商品
    def change_good_table(self, item):
        row = item.row()
        column = item.column()
        gid = self.ui.good_table_2.item(row, 0).text()
        new_value = self.ui.good_table_2.item(row, column).text()
        if column == 1:
            if PARAM.select_handle.select_order_detail_gid(gid):
                QMessageBox.critical(self.ui, '失败', '有正在进行中的订单占用此商品')
                self.update_good(None)
            else:
                if PARAM.update_handle.update_good_name(new_value, gid):
                    QMessageBox.information(self.ui, '成功', '修改成功')
                else:
                    QMessageBox.critical(self.ui, '失败', '修改失败')
        elif column == 2:
            if PARAM.update_handle.update_good_price(new_value, gid):
                QMessageBox.information(self.ui, '成功', '修改成功')
            else:
                QMessageBox.critical(self.ui, '失败', '修改失败')
        else:
            if PARAM.update_handle.update_good_stock(new_value, gid):
                QMessageBox.information(self.ui, '成功', '修改成功')
            else:
                QMessageBox.critical(self.ui, '失败', '修改失败')



if __name__ == '__main__':
    app = QApplication([])
    PARAM.Login_win = LoginWindow()
    PARAM.Login_win.ui.show()
    # PARAM.Cus_win = Customer_Window('dddbbb')
    # PARAM.Cus_win.ui.show()
    app.exec_()
    cursor.close()
    connect.close()
    # connect.close()
