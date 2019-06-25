# -*- coding: utf-8 -*-

# todo  项目启动文件  使用方式      python main.py xxx公司

from index import InitVariable
from index import Search
from index import GetScore
from index import GetAchievement
from index import GetManager
from index import GetSelfAchievement
from index import CheckIfPerformanceExist
from gethtml import GetNewIpProxy
from GlobalVar import *
import time
import traceback
from multiprocessing import Pool, cpu_count, freeze_support
from apscheduler.schedulers.blocking import BlockingScheduler
import platform

import logging
from getconfig import getConfig
if getConfig('output', 'log') == 'True':
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.ERROR)

def run(companyname):
    try:
        InitVariable()
        InitDB()
        GetNewIpProxy()
        DanWeiGuid = Search(companyname)
        if DanWeiGuid is None:
            UpdateRunningInfo(companyname, '未搜索到该企业，或不存在')
            return
        qiyezizhi, Score, Score_old = GetScore(DanWeiGuid)
        ManagerList, ManagerInfo = GetManager(DanWeiGuid)
        AchievementList, jyzmInfo, ckIinfo, yszmInfo = GetAchievement(DanWeiGuid, companyname)
        SelfAchievementList, SelfckIinfo, SelfyszmInfo = GetSelfAchievement(DanWeiGuid, companyname)
    except Exception as e:
        errorInfo = '获取企业{0}信息失败返回, 异常信息：{1}'.format(companyname, traceback.format_exc())
        logging.warning(errorInfo)
        UpdateRunningInfo(companyname, errorInfo)
        return

    # 连接mysql
    conn = GetDBConn()
    cursor = GetDBCursor()
    date = GetDateTime()
    SQL_INSERT = """replace into CompanyPerformance (companyname, qiyezizhi, Score, Score_old, types, project_name, build_company, \
gczt, zbtime, jgtime, ystime, mianji, zbprice, manager, manager_status, zhicheng, shizheng_level, tujian_level, project_kind, \
manager_level, ocr_yszm, pic_yszm, update_time) \
values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    SQL_UPDATE = "update CompanyPerformance set qiyezizhi=%s, Score=%s, Score_old=%s, gczt=%s, mianji=%s, manager_status=%s, zhicheng=%s, shizheng_level=%s, tujian_level=%s, update_time=%s  where companyname=%s and project_name=%s and build_company=%s and manager=%s"
    Manager_SQL_INSERT = """replace into ProjectManager (companyname, manager, manager_status, manager_level, zhicheng) values (%s, %s, %s, %s, %s)"""


    # 循环场内项目业绩
    for Achievement in AchievementList:
        project_name = Achievement[1]
        build_company = Achievement[2]
        gczt = ckIinfo[Achievement[0]]
        zbtime = Achievement[3]
        mianji = jyzmInfo[Achievement[0]]
        zbprice = Achievement[4]
        manager = Achievement[5]
        jgrq = ''
        ysrq = ''
        ocr_ret = ''
        pic = ''
        manager_level = ''
        shizheng_level = ''
        tujian_level = ''
        manager_status = ''

        if Achievement[0] in yszmInfo:
            jgrq = yszmInfo[Achievement[0]][0]
            ysrq = yszmInfo[Achievement[0]][1]
            ocr_ret = yszmInfo[Achievement[0]][2]
            pic = yszmInfo[Achievement[0]][3]
        else:
            jgrq = ''
            ysrq = ''
            ocr_ret = ''
            pic = ''
        if manager not in ManagerList:
            manager_level = ''
            shizheng_level = ''
            tujian_level = ''
            manager_status = ''
        else:
            manager_level = ManagerList[manager][0]
            if '市政公用工程一级' in manager_level:
                shizheng_level = '一级'
            elif '市政公用工程二级' in manager_level:
                shizheng_level = '二级'
            if '建筑工程一级' in manager_level:
                tujian_level = '一级'
            elif '建筑工程二级' in manager_level:
                tujian_level = '二级'
            manager_status = ManagerList[manager][1]
            if int(manager_status) > 0:
                manager_status = '在建'
            else:
                manager_status = '已竣工'

        if manager not in ManagerInfo:
            zhicheng = ''
        else:
            zhicheng = ManagerInfo[manager]

        PARA = (companyname, qiyezizhi, Score, Score_old, '市平台', project_name, build_company,
                gczt, zbtime, jgrq, ysrq, mianji, zbprice, manager, manager_status,
                zhicheng, shizheng_level, tujian_level, '', manager_level, ocr_ret, pic, date)
        PARA_UPDATE = (qiyezizhi, Score, Score_old, gczt, mianji, manager_status, zhicheng, shizheng_level, tujian_level, date,
                       companyname, project_name, build_company, manager)
        try:
            if '已竣工' in gczt and ocr_ret == '' and CheckIfPerformanceExist(companyname, project_name, build_company, zbtime, zbprice, manager):
                cursor.execute(SQL_UPDATE, PARA_UPDATE)
            else:
                logging.info('执行replace操作，project_name = {0}, gczt = {1}, orc_ret = {2}'.format(project_name, gczt, ocr_ret))
                cursor.execute(SQL_INSERT, PARA)
            conn.commit()
        except:
            errorInfo = '{0} 场内业绩插入失败'.format(companyname)
            logging.warning(errorInfo)
            logging.warning(PARA)
            conn.rollback()
            UpdateRunningInfo(companyname, errorInfo)
            return

    # 循环自行增加业绩
    for SelfAchievement in SelfAchievementList:
        project_name = SelfAchievement[1]
        build_company = SelfAchievement[2]
        gczt = SelfckIinfo[SelfAchievement[0]]
        zbtime = SelfAchievement[3]
        mianji = ''
        zbprice = SelfAchievement[4]
        manager = SelfAchievement[5]
        jgrq = ''
        ysrq = ''
        ocr_ret = ''
        pic = ''
        manager_level = ''
        shizheng_level = ''
        tujian_level = ''
        manager_status = ''

        if SelfAchievement[0] in SelfyszmInfo:
            jgrq = SelfyszmInfo[SelfAchievement[0]][0]
            ysrq = SelfyszmInfo[SelfAchievement[0]][1]
            ocr_ret = SelfyszmInfo[SelfAchievement[0]][2]
            pic = SelfyszmInfo[SelfAchievement[0]][3]
        else:
            jgrq = ''
            ysrq = ''
            ocr_ret = ''
            pic = ''
        if manager not in ManagerList:
            manager_level = ''
            shizheng_level = ''
            tujian_level = ''
            manager_status = ''
        else:
            manager_level = ManagerList[manager][0]
            if '市政公用工程一级' in manager_level:
                shizheng_level = '一级'
            elif '市政公用工程二级' in manager_level:
                shizheng_level = '二级'
            if '建筑工程一级' in manager_level:
                tujian_level = '一级'
            elif '建筑工程二级' in manager_level:
                tujian_level = '二级'
            manager_status = ManagerList[manager][1]
            if int(manager_status) > 0:
                manager_status = '在建'
            else:
                manager_status = '已竣工'
        if manager not in ManagerInfo:
            zhicheng = ''
        else:
            zhicheng = ManagerInfo[manager]

        PARA = (companyname, qiyezizhi, Score, Score_old, '自备', project_name, build_company,
                gczt, zbtime, jgrq, ysrq, mianji, zbprice, manager, manager_status,
                zhicheng, shizheng_level, tujian_level, '', manager_level, ocr_ret, pic, date)
        PARA_UPDATE = (qiyezizhi, Score, Score_old, gczt, mianji, manager_status, zhicheng, shizheng_level, tujian_level, date,
                       companyname, project_name, build_company, manager)
        try:
            if '已竣工' in gczt and ocr_ret == '' and CheckIfPerformanceExist(companyname, project_name, build_company, zbtime, zbprice, manager):
                cursor.execute(SQL_UPDATE, PARA_UPDATE)
            else:
                logging.info('执行replace操作，project_name = {0}, gczt = {1}, orc_ret = {2}'.format(project_name, gczt, ocr_ret))
                cursor.execute(SQL_INSERT, PARA)
            conn.commit()
        except:
            errorInfo = '{0} 自行增加业绩插入失败'.format(companyname)
            logging.warning(errorInfo)
            logging.warning(PARA)
            conn.rollback()
            UpdateRunningInfo(companyname, errorInfo)
            return

    # 循环经理人
    for Manager, Minfo in ManagerList.items():
        PARA = (companyname, Manager, Minfo[1], Minfo[0], ManagerInfo[Manager])
        try:
            cursor.execute(Manager_SQL_INSERT, PARA)
            conn.commit()
        except:
            errorInfo = '{0} 经理信息插入失败'.format(companyname)
            logging.warning(errorInfo)
            logging.warning(PARA)
            conn.rollback()
            UpdateRunningInfo(companyname, errorInfo)
            return

    UpdateRunningInfo(companyname, '采集成功。', True)
    logging.info('%s 信息提交成功'%companyname)

def failed_retry():
    retry = 5
    while retry != 0:
        logging.info('第{0}次对采集信息失败的企业，进行重新采集...'.format(6 - retry))
        companys = GetFailedCompanys()
        if len(companys) > 0:
            pool = Pool(cpu_count())
            pool.map(run, companys)
            pool.close()
            pool.join()
            retry -= 1
        else:
            break
    logging.info('5次针对失败采集的企业，重新采集信息完成。')

def process():
    companys = GetCurrentAllCompanys()
    logging.info("Current comanys num: %d" % companys.__len__())
    logging.info("Current cpu num: %d" % cpu_count())
    pool = Pool(cpu_count())
    pool.map(run, companys)
    pool.close()
    pool.join()
    failed_retry()

def main():
    ImportDataFromFile()
    startTime = time.time()
    process()
    endTime = time.time()
    logging.info("并行执行时间：%d" % int(endTime - startTime))

def main_with_schedule():
    ImportDataFromFile()
    process()
    scheduler = BlockingScheduler()
    scheduler.add_job(func=process, trigger='cron', hour=17, minute=0)
    scheduler.start()

if __name__ == "__main__":
    sysstr = platform.system()
    if sysstr == 'Windows':
        freeze_support()
    main_with_schedule()
