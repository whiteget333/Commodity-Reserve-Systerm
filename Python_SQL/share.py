from My_Sql import sql_insert, sql_select, sql_delete, sql_update
import time
import pymssql


class PARAM:
    Login_win = None
    Cus_win = None
    Amd_win = None
    rid = None

    update_handle = sql_update()
    select_handle = sql_select()
    delete_handle = sql_delete()
    insert_handle = sql_insert()

rid_1 = eval(time.strftime("%Y%m%d", time.localtime(time.time()))) * 100

result = PARAM.select_handle.select_reserve_all()
PARAM.rid = max(eval(result[len(result) - 1][0]) + 1, rid_1)
print(PARAM.rid)


def is_number(s):
    try:
        if int(s) > 0:
            return True
        else:
            return False
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False



