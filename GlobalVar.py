import pymysql
import datetime
import logging
from getconfig import getConfig
if getConfig('output', 'log') == 'True':
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.ERROR)

def InitDB():
    global conn
    conn = pymysql.connect('localhost', 'root', '123456', 'mydb')
    conn.text_factory = str
    global cursor
    cursor = conn.cursor()

def GetDBConn():
    return conn

def GetDBCursor():
    return cursor

def GetDateTime():
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return date

def UpdateRunningInfo(companyname, info, isSucceed = False):
    date = GetDateTime()
    if isSucceed:
        status = '成功'
        SQL_UPDATE = 'update SpiderRunningStatus set info=%s, status=%s, update_time=%s, last_succeed_time=%s where companyname=%s'
        PARA = (info, status, date, date, companyname)
    else:
        status = '失败'
        SQL_UPDATE = 'update SpiderRunningStatus set info=%s, status=%s, update_time=%s where companyname=%s'
        PARA = (info, status, date, companyname)

    try:
        cursor.execute(SQL_UPDATE, PARA)
    except:
        logging.warning('%s 更新运行信息表失败' % companyname)
        logging.warning(PARA)
        conn.rollback()
    # 关闭Cursor # 提交事务 # 关闭Connection
    cursor.close()
    conn.commit()
    conn.close()

def ImportDataFromFile():
    conn = pymysql.connect('localhost', 'root', '123456', 'mydb')
    conn.text_factory = str
    cursor = conn.cursor()
    # 判断表是否存在
    with open('CreateTable.sql', 'r') as f:
        SQL = f.read().split(';')
    cursor.execute('show tables')
    results = cursor.fetchall()
    TableNow = [i[0] for i in results]

    if 'projectmanager' not in TableNow:
        cursor.execute(SQL[0])
    if 'companyperformance' not in TableNow:
        cursor.execute(SQL[1])
    if 'spiderrunningstatus' not in TableNow:
        cursor.execute(SQL[2])

    companys = []
    with open('companys.txt', encoding='utf8') as f:
        all = f.read().strip().split('\n')
    for i in all:
        companys.append(i)
    logging.info("Import data, comanys num: %d" % companys.__len__())
    try:
        cursor.executemany('replace into SpiderRunningStatus(companyname) value(%s)', companys)
    except:
        logging.warning('导入companys.txt 内容到数据库失败！')
        conn.rollback()
        # 关闭Cursor # 提交事务 # 关闭Connection
    cursor.close()
    conn.commit()
    conn.close()

def GetCurrentAllCompanys():
    conn = pymysql.connect('localhost', 'root', '123456', 'mydb')
    conn.text_factory = str
    cursor = conn.cursor()
    SQL_SELECT = 'select companyname from SpiderRunningStatus'
    try:
        cursor.execute(SQL_SELECT)
    except:
        logging.warning('获取SpiderRunningStatus表所有企业名称失败')
        conn.rollback()
    results = cursor.fetchall()
    companys = []
    for result in results:
        companys.append(result[0])
    # 关闭Cursor # 提交事务 # 关闭Connection
    cursor.close()
    conn.commit()
    conn.close()
    return companys

def GetFailedCompanys():
    conn = pymysql.connect('localhost', 'root', '123456', 'mydb')
    conn.text_factory = str
    cursor = conn.cursor()
    SQL_SELECT = 'select companyname from SpiderRunningStatus where status = %s'
    PARA = ('失败')
    try:
        cursor.execute(SQL_SELECT, PARA)
    except:
        logging.warning('获取SpiderRunningStatus表信息失败')
        conn.rollback()
    results = cursor.fetchall()
    companys = []
    for result in results:
        companys.append(result[0])
    # 关闭Cursor # 提交事务 # 关闭Connection
    cursor.close()
    conn.commit()
    conn.close()
    return companys