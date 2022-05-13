import pymssql


connect = pymssql.connect(host='localhost', server='LAPTOP-CKREUVIR', port='1433', user='*****',
                                password='*****',
                                database='shop')
print(connect)
cursor = connect.cursor()

def cursor_init(user):
    global connect, cursor
    if user == 'login1':
        connect = pymssql.connect(host='localhost', server='LAPTOP-CKREUVIR', port='1433', user='*****',
                                  password='*****',
                                  database='shop')
    elif user == 'cus':
        connect = pymssql.connect(host='localhost', server='LAPTOP-CKREUVIR', port='1433', user='*****',
                                  password='*****',
                                  database='shop')
    elif user == 'adm':
        connect = pymssql.connect(host='localhost', server='LAPTOP-CKREUVIR', port='1433', user='*****',
                                  password='*****',
                                  database='shop')

    print(connect)
    cursor = connect.cursor()


reserve_index = [6, 7]
good_index = [1]
customer_index = [1, 3]
Order_detail_index = []


def be_str(s):
    return "\'" + str(s) + "\'"


class sql_insert:
    # 插入顶语句
    def insert_top(self, command):
        try:
            cursor.execute(command)
            connect.commit()
            return True
        except:
            return False

    # 插入新商品
    def insert_good(self, gid, name, price, stock):
        command = ("insert into Commidity(Gid,Gname,Gprice,Gstock) ",
                   "values (", be_str(gid), ",", be_str(name), ",", price, ",", stock, ")")
        return self.insert_top(''.join(command))

    # 插入新订单
    def insert_reserve(self, rid, cusid, count, cost, date, phone, address, state):
        command = ("insert into Reserve(Rid, Cusid, Gcount, Cost, Date, Phone, Address, State) ",
                   "values (", be_str(rid), ",", be_str(cusid), ",", count, ",", cost, ",", be_str(date), ",",
                   be_str(phone), ",", be_str(address), ",", be_str(state), ")")
        return self.insert_top(''.join(command))

    # 插入订单详情
    def insert_order_detail(self, rid, gid, number, price):
        command = ("insert into Order_detail(Rid, Gid,Gnumber, Gprice) ",
                   "values (", be_str(rid), ",", be_str(gid), ",", number, ",", price, ")")
        return self.insert_top(''.join(command))

    # 插入消费者账户
    def insert_cus_pass(self, cusid, password):
        command = ("insert into Cus_pass(Cusid, Password) ",
                   "values (", be_str(cusid), ",", be_str(password), ")")
        return self.insert_top(''.join(command))

    def insert_customers(self, cusid, name, phone, address):
        command = ("insert into Customers(Cusid, Cusname, Phone, Address) ",
                   "values (", be_str(cusid), ",", be_str(name), ",", be_str(phone), ",", be_str(address), ")")
        return self.insert_top(''.join(command))


class sql_select:
    # 查询顶语句
    def select_top(self, command, l):
        try:
            cursor.execute(command)
            result_all = cursor.fetchall()
            answer = []
            for result in result_all:
                result = list(result)
                for i in range(len(result)):
                    if i in l:
                        result[i] = result[i].encode('latin-1').decode('gbk')
                    if isinstance(result[i], str):
                        result[i] = result[i].replace(' ', '')
                answer.append(result)
            return answer
        except:
            return False


    # 查询管理员账户和密码
    def select_adm_top(self):
        return self.select_top("select * from Administrators", [])

    # 查询消费者账户和密码
    def select_cus_pass_top(self, cusid, password):
        command = ("select * from Cus_pass where Cusid = ", be_str(cusid), " and Password= ", be_str(password))
        return self.select_top(''.join(command), [])

    def select_pass_based_cusid(self, cusid):
        command = ("select Password from Cus_pass where Cusid= ", be_str(cusid))
        return self.select_top(''.join(command), [])

    def select_customer_top(self, cusid):
        command = ("select * from Customers where Cusid= ", be_str(cusid))
        return self.select_top(''.join(command), customer_index)

    # 查询订单顶语句
    def select_reserve_top(self, command):
        return self.select_top(command, reserve_index)

    # 查询订单详情顶语句
    def select_Order_detail_top(self, command):
        return self.select_top(command, Order_detail_index)

    # 查询商品顶语句
    def select_good_top(self, command):
        return self.select_top(command, good_index)

    # 查询所有订单
    def select_reserve_all(self):
        return self.select_reserve_top("select * from Reserve")

    # 查询订单Rid
    def select_reserve_rid(self, rid):
        command = ("select * from Reserve where Rid = ", be_str(rid))
        return self.select_reserve_top(''.join(command))

    # 查询订单Cusid
    def select_reserve_cusid(self, cusid):
        command = ("select * from Reserve where Cusid = ", be_str(cusid))
        return self.select_reserve_top(''.join(command))

    # 查询订单状态
    def select_reserve_state(self, state):
        command = ("select * from Reserve where State = ", be_str(state))
        return self.select_reserve_top(''.join(command))

    def select_reserve_cusid_state(self,cusid, state):
        command = ("select * from Reserve where State = ", be_str(state), " and Cusid = ", be_str(cusid))
        return self.select_reserve_top(''.join(command))

    def select_reserve_cusid_rid(self, rid, cusid):
        command = ("select * from Reserve where Rid = ", be_str(rid), " and Cusid = ", be_str(cusid))
        return self.select_reserve_top(''.join(command))

    # 查询所有商品
    def select_good_all(self):
        return self.select_good_top("select * from Commidity")

    def select_good_view(self):
        return self.select_top("select * from Good_info", [0])

    # 查询商品Gid
    def select_good_gid(self, gid):
        command = ("select * from Commidity where Gid = ", be_str(gid))
        return self.select_good_top(''.join(command))

    def select_good_name(self, name):
        command = ("select * from Commidity where Gname = ", be_str(name))
        return self.select_good_top(''.join(command))

    def select_good_stock(self, name):
        command = ("select Gstock from Good_info where Gname = ", be_str(name))
        return self.select_top(''.join(command), [])

    # 查询商订单详情中的Gid
    def select_order_detail_gid(self, gid):
        command = ("select * from Order_detail where Gid = ", be_str(gid))
        return self.select_Order_detail_top(''.join(command))

    def select_order_detail_rid(self, rid):
        command = ("select * from Order_detail where Rid = ", be_str(rid))
        return self.select_Order_detail_top(''.join(command))


class sql_delete:
    #  删除顶语句
    def delete_top(self, command):
            # cursor.execute(command)
            # connect.commit()
        try:
            cursor.execute(command)
            connect.commit()
            return True
        except:
            return False

    #  删除商品
    def delete_good(self, gid):
        command = ("delete from Commidity where Gid = ", be_str(gid))
        return self.delete_top(''.join(command))

    #  删除订单
    def delete_reserve(self, rid):
        command = ("delete from Reserve where Rid = ", be_str(rid))
        return self.delete_top(''.join(command))


class sql_update:
    # 修改顶语句
    def update_top(self, command):
        try:
            cursor.execute(command)
            connect.commit()
            return True
        except:
            return False

    # 修改商品名称
    def update_good_name(self, name, gid):
        command = ("update Commidity set Gname = ", be_str(name), " where Gid = ", be_str(gid))
        return self.update_top(''.join(command))

    # 修改商品价格
    def update_good_price(self, price, gid):
        command = ("update Commidity set Gprice = ", price, " where Gid = ", be_str(gid))
        return self.update_top(''.join(command))

    # 修改商品库存
    def update_good_stock(self, stock, gid):
        command = ("update Commidity set Gstock = ", stock, " where Gid = ", be_str(gid))
        return self.update_top(''.join(command))

    # 修改增加库存
    def add_stock(self, num, gid):
        command = ("update Commidity set Gstock = Gstock +", num, "where Gid = ", be_str(gid))
        return self.update_top(''.join(command))

    # 修改订单状态
    def update_reserve_state(self, rid, state):
        command = ("update Reserve set State = ", be_str(state), "where Rid = ", be_str(rid))
        return self.update_top(''.join(command))

    def update_password(self, cusid, password):
        command = ("update Cus_pass set Password = ", be_str(password), "where cusid = ", be_str(cusid))
        return self.update_top(''.join(command))
