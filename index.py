# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from gethtml import Req_get, Req_post, Req_get_v2
from BaiduOcr import local_picture_ocr
from GlobalVar import GetDBCursor

import logging
from getconfig import getConfig
if getConfig('output', 'log') == 'True':
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.ERROR)


def InitVariable():
    # 采集存储变量
    global AchievementList, jyzmInfo, ckIinfo, yszmInfo
    global SelfAchievementList, SelfckIinfo, SelfyszmInfo
    global ManagerList, ManagerInfo
    AchievementList, jyzmInfo, ckIinfo, yszmInfo = [], {}, {}, {}
    SelfAchievementList, SelfckIinfo, SelfyszmInfo = [], {}, {}
    ManagerList, ManagerInfo = {}, {}

def Search(company):
    """
    搜索输入的公司名称
    :param company: 输入的公司名称
    :return:  返回公司唯一的 DanWeiGuid
    """
    logging.info('正在搜索 {0}'.format(company))
    index_url = 'http://gcjy.njzwfw.gov.cn/njxxnew/qyxx/xmdjdw/alldw.aspx'
    search_url = 'http://gcjy.njzwfw.gov.cn/njxxnew/qyxx/xmdjdw/alldw.aspx'
    result_html = Req_get(index_url)
    if result_html is None:
        raise Exception('获取搜索页面失败')
    soup = BeautifulSoup(result_html, 'lxml')
    event_argument = soup.find('input', {'id': '__EVENTARGUMENT'})
    if event_argument is None:
        raise Exception('查找搜索页面__EVENTARGUMENT参数输入值失败')
    data = {
        "__EVENTARGUMENT": event_argument['value'],
        "__VIEWSTATE": soup.find('input', {'id': '__VIEWSTATE'})['value'],
        "__CSRFTOKEN": soup.find('input', {'id': '__CSRFTOKEN'})['value'],
        "txtUnitName": company.encode('gbk'),
        "Button1": soup.find('input', {'id': 'Button1'})['value'].encode('gbk'),
        "__VIEWSTATEGENERATOR": soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value'],
        "__EVENTVALIDATION": soup.find('input', {'id': '__EVENTVALIDATION'})['value'],
        "__EVENTTARGET": soup.find('input', {'id': '__EVENTTARGET'})['value']
    }
    result = Req_post(search_url, data)
    if result is None:
        raise Exception('输入企业名称，搜索失败')
    result_soup = BeautifulSoup(result, 'lxml')
    a_find_result = result_soup.find('a', {'target': '_blank'})
    if a_find_result is None:
        raise Exception('在搜索结果页面内容，未找到属性为target:_blank，节点名为a 的节点')
    result_href = a_find_result['href']
    find_result = re.findall(r'DanWeiGuid=(.*?)&', result_href)
    if len(find_result) > 0:
        DanWeiGuid = find_result[0]
        logging.info('搜索到: {0}, DanWeiGuid为: {1}'.format(company, DanWeiGuid))
        return DanWeiGuid
    else:
        logging.warning('未搜索到该企业，或不存在')
        return None



def GetScore(DanWeiGuid):
    """
    获取公司的信用评分（新、旧）
    :param DanWeiGuid:
    :return: 评分
    """
    url = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd/ShiGongInfo/ShiGongInfo_Detail.aspx?'
    geturl = url + 'DanWeiGuid={0}&ViewType=2'.format(DanWeiGuid)
    logging.info('正在获取 企业资质、信用评分（新、旧）...')

    qiyezizhi, Score, Score_old = '', '', ''
    htmlText = Req_get(geturl)
    if htmlText is None:
        return qiyezizhi, Score, Score_old
    soup = BeautifulSoup(htmlText, 'lxml')
    try:
        Score = soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_CreditScore'}).text
        Score_old = soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_CreditScoreOld'}).text
        table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_Datagrid1'})
        if table is None:
            return qiyezizhi, Score, Score_old
        _tr = table.findAll('tr')[1:]
        qiyezizhi = ''
        for tr in _tr:
            _td = tr.findAll('td')
            zizhi = _td[2].text.strip()
            qiyezizhi += zizhi
    except:
        return qiyezizhi, Score, Score_old
    return qiyezizhi, Score, Score_old


def GetAchievementList(html):
    """
    获取 业绩列表
    :param html:
    :return: 业绩字段详情
    """
    ckurl_demo = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd/ShiGongYeJi/'
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_Datagrid2'})

    if table is None:
        raise Exception('获取业绩列表失败')
    _tr = table.findAll('tr')[1:]
    for tr in _tr:
        _td = tr.findAll('td')
        id = _td[0].text.strip()
        name = _td[1].text.strip()
        company = _td[2].text.strip()
        zbtime = _td[3].text.strip()
        zbprice = _td[4].text.strip()
        manager = _td[5].text.strip()
        if len(_td) == 8:
            try:
                jyzm = _td[7].input['onclick'].split('"')[1]
            except:
                jyzm = ''

        ckurl = ckurl_demo + _td[-1].input['onclick'].split("'")[1]
        AchievementList.append([id, name, company, zbtime, zbprice, manager, jyzm, ckurl])


def GetAchievementNextData(html):
    """
    拿到翻页需要用的验证信息
    :param html:
    :return: 下一页的请求body
    """
    soup = BeautifulSoup(html, 'lxml')
    data = {
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": soup.find('input', {'id': '__VIEWSTATE'})['value'],
        "ctl00$ContentPlaceHolder1$S_BiaoDuanName": "",
        "ctl00$ScriptManager1": "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$Pager_User",
        "ctl00$ContentPlaceHolder1$condition": "",
        "ctl00$ContentPlaceHolder1$S_BiaoDuanMoney_To": "",
        "ctl00$ContentPlaceHolder1$S_ShenQingBiaoNo": "",
        "ctl00$ContentPlaceHolder1$S_BiaoDuanMoney_From": "",
        "__VIEWSTATEGENERATOR": soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value'],
        "ctl00$ContentPlaceHolder1$HidState": "0",
        "__EVENTVALIDATION": soup.find('input', {'id': '__EVENTVALIDATION'})['value'],
        "__EVENTTARGET": "ctl00$ContentPlaceHolder1$Pager_User",
        "ctl00$ContentPlaceHolder1$S_BiaoDuanNo": "",
        "ctl00$ContentPlaceHolder1$S_PName": ""
    }
    return data


def GetjyzmInfo(id, url):
    """
    获取绿化面积
    :param id:
    :param url:
    :return:
    """
    if url.startswith('http'):
        html = Req_get(url)
        if html is None:
            jyzmInfo[id] = ''
            return
        mianji = re.findall(u'园林绿化面积：(.*?) m2', html)
        mianji = mianji[0] if mianji else ''
        jyzmInfo[id] = mianji
    else:
        jyzmInfo[id] = ''


def GetckInfo(id, url):
    if url.startswith('http'):
        html = Req_get(url)
        if html is None:
            ckIinfo[id] = ''
            return
        soup = BeautifulSoup(html, 'lxml')
        try:
            gczt = soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_lblIsZaiJian'}).text
        except:
            gczt = ''
        if '在建工程' in gczt:
            gczt = '在建'
        elif '撤出工程' in gczt:
            gczt = '已竣工'
        else:
            gczt = ''
        ckIinfo[id] = gczt
    else:
        ckIinfo[id] = ''

def GetYszmInfo(id, url):
    logging.info('正在获取汇总图片信息html...')
    html = Req_get(url)
    if html is None:
        logging.info('获取汇总图片信息html失败')
        return
    begin_url = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd'
    end_rul = re.findall(r'OpenWindow\(\'..(.*?)\'', html)
    if len(end_rul) == 0:
        logging.info('未找到验收证明图片url')
        return
    end_rul = end_rul[0] if end_rul else ''
    hole_url = begin_url + end_rul
    pic_html = Req_get(hole_url)
    if pic_html is None:
        logging.info('get 图片html失败')
        return
    soup = BeautifulSoup(pic_html, 'lxml')
    event_argument = soup.find('input', {'id': '__EVENTARGUMENT'})
    if event_argument is None:
        raise Exception('查找__EVENTARGUMENT失败')
    data = {
        "ctl00$ScriptManager1": "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$rblType$2",
        "__EVENTARGUMENT": event_argument['value'],
        "__VIEWSTATE": soup.find('input', {'id': '__VIEWSTATE'})['value'],
        "ctl00$ContentPlaceHolder1$rblType": soup.find('input', {'id': 'ctl00_ContentPlaceHolder1_rblType_2'})['value'],
        "__VIEWSTATEGENERATOR": soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value'],
        "__EVENTVALIDATION": soup.find('input', {'id': '__EVENTVALIDATION'})['value'],
        "__EVENTTARGET": soup.find('input', {'id': '__EVENTTARGET'})['value'],
        "__LASTFOCUS": soup.find('input', {'id': '__LASTFOCUS'})['value']
    }
    next_page = Req_post(hole_url, data)
    if next_page is None:
        logging.info('get 验收证明图片html失败')
        return
    soup2 = BeautifulSoup(next_page, 'lxml')
    find_pic_request_url = soup2.find('a', {'target': '_blank'})
    if find_pic_request_url is None:
        logging.info('未找到下载图片url')
        return
    pic_request_url = find_pic_request_url['href']
    logging.info(pic_request_url)
    url_real_base = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd/ShiGongInfo/'
    total_url = url_real_base + pic_request_url
    logging.info('下载验收证明图片...')
    real = Req_get_v2(total_url)
    if real is None:
        return
    logging.info('正在文字识别...')
    ocr_ret = local_picture_ocr(real.content)
    if ocr_ret is None:
        logging.info('文字识别失败！')
        return
    logging.info(ocr_ret)
    findJunGongDate = u'竣工日期.*?(\d{4}).*?(\d{1,2}).*?(\d{1,2})'
    pattern = re.compile(findJunGongDate)
    results = pattern.findall(ocr_ret)
    jgrq = ''
    if len(results):
        if int(results[0][1]) >= 1 and \
                int(results[0][1]) <= 12 and \
                int(results[0][2]) >= 1 and \
                int(results[0][2]) <= 31 and \
                int(results[0][0]) <= 2050 and \
                int(results[0][0]) >= 2000:
            jgrq = '{0}-{1}-{2}'.format(results[0][0], results[0][1], results[0][2])
            logging.info(jgrq)
    findYanShouDate = u'验收日期.*?(\d{4}).*?(\d{1,2}).*?(\d{1,2})'
    patternYanShou = re.compile(findYanShouDate)
    resultsYanShou = patternYanShou.findall(ocr_ret)
    ysrq = ''
    if len(resultsYanShou):
        if int(resultsYanShou[0][1]) >= 1 and \
                int(resultsYanShou[0][1]) <= 12 and \
                int(resultsYanShou[0][2]) >= 1 and \
                int(resultsYanShou[0][2]) <= 31 and \
                int(resultsYanShou[0][0]) <= 2050 and \
                int(resultsYanShou[0][0]) >= 2000:
            ysrq = '{0}-{1}-{2}'.format(resultsYanShou[0][0], resultsYanShou[0][1], resultsYanShou[0][2])
            logging.info(ysrq)
    yszmInfo[id] = [jgrq, ysrq, ocr_ret, total_url]

def GetAchievement(DanWeiGuid, companyName):
    """
    获取业绩信息
    :param DanWeiGuid:
    :return:
    """
    logging.info('正在获取 场内项目的业绩..')
    url = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd/ShiGongYeJi/ShiGongYeJi_List.aspx?'
    geturl = url + 'ViewType=2&UnitType=5&DanWeiGuid={0}'.format(DanWeiGuid)
    html = Req_get(geturl)
    if html is None:
        return AchievementList, jyzmInfo, ckIinfo, yszmInfo
    allpage = re.findall(u'总页数：<font color="blue"><b>(.*?)</b>', html)[0]
    logging.info('本公司共有 {0} 页场内项目的业绩信息'.format(allpage))
    logging.info('正在获取第 {0} 页场内项目的业绩信息'.format(1))
    GetAchievementList(html)
    data = GetAchievementNextData(html)
    posturl = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd/ShiGongYeJi/ShiGongYeJi_List.aspx?'
    run_posturl = posturl + 'ViewType=2&UnitType=5&DanWeiGuid={0}'.format(DanWeiGuid)
    for p in range(2, int(allpage) + 1):
        # for p in xrange(2, 3):
        logging.info('正在获取第 {0} 页场内项目的业绩'.format(p))
        data['__EVENTARGUMENT'] = str(p)
        next_html = Req_post(run_posturl, data=data)
        if next_html is None:
            raise Exception('获取第 {0} 页场内项目的业绩失败'.format(p))
        GetAchievementList(next_html)
        data = GetAchievementNextData(next_html)
    logging.info('共计找到了 {0} 个业绩'.format(len(AchievementList)))
    for row in AchievementList:
        rowid, jyzm, ckurl = row[0], row[-2], row[-1]
        logging.info('正在获取第 {0} 个业绩的详细信息'.format(rowid))
        GetjyzmInfo(rowid, jyzm)
        GetckInfo(rowid, ckurl)
        if '已竣工' in ckIinfo[rowid] and CheckIfNeedGetYszmInfo(companyName, row[1], row[2], row[3], row[4], row[5]):
            GetYszmInfo(rowid, ckurl)
        else:
            logging.info('已存在ocr信息')
    return AchievementList, jyzmInfo, ckIinfo, yszmInfo

def CheckIfNeedGetYszmInfo(companyName, projectName, buildCompany, zbtime, zbprice, manager):
    cursor = GetDBCursor()
    QUERY_SQL = "select ocr_yszm from CompanyPerformance where companyname = %s and project_name = %s and build_company = %s and zbtime = %s and zbprice = %s and manager = %s"
    PARA = (companyName, projectName, buildCompany, zbtime, zbprice, manager)
    cursor.execute(QUERY_SQL, PARA)
    results = cursor.fetchall()
    ocr_result = ''
    for row in results:
        ocr_result = row[0]
        break
    if ocr_result:
        logging.info('发现该业绩的ocr信息')
        return False
    else:
        logging.info('未发现该业绩的ocr信息')
        return True

def CheckIfPerformanceExist(companyName, projectName, buildCompany, zbtime, zbprice, manager):
    cursor = GetDBCursor()
    QUERY_SQL = "select count(*) from CompanyPerformance where companyname = %s and project_name = %s and build_company = %s  and zbtime = %s and zbprice = %s and manager = %s"
    PARA = (companyName, projectName, buildCompany, zbtime, zbprice, manager)
    cursor.execute(QUERY_SQL, PARA)
    results = cursor.fetchall()
    result = ''
    for row in results:
        result = row[0]
        break
    if result > 0:
        logging.info('业绩存在,执行update')
        return True
    else:
        logging.info('业绩不存在，执行replace')
        return False


def GetSelfAchievementList(html):
    """
    获取 业绩列表
    :param html:
    :return: 业绩字段详情
    """
    ckurl_demo = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd/ShiGongYeJi/'
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_Datagrid1'})
    _tr = table.findAll('tr')[1:]
    for tr in _tr:
        _td = tr.findAll('td')
        id = _td[0].text.strip()
        name = _td[1].text.strip()
        company = _td[2].text.strip()
        zbtime = _td[3].text.strip()
        zbprice = _td[4].text.strip()
        manager = _td[5].text.strip()
        try:
            ckurl = ckurl_demo + _td[7].input['onclick'].split("'")[1]
        except:
            ckurl = ''
        SelfAchievementList.append([id, name, company, zbtime, zbprice, manager, ckurl])


def GetSelfAchievementNextData(html):
    """
    拿到翻页需要用的验证信息
    :param html:
    :return: 下一页的请求body
    """
    soup = BeautifulSoup(html, 'lxml')
    data = {
        "__EVENTARGUMENT": "2",
        "__VIEWSTATE": soup.find('input', {'id': '__VIEWSTATE'})['value'],
        "ctl00$ContentPlaceHolder1$S_BiaoDuanName": "",
        "ctl00$ScriptManager1": "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$Pager",
        "ctl00$ContentPlaceHolder1$condition": "",
        "ctl00$ContentPlaceHolder1$S_BiaoDuanMoney_To": "",
        "ctl00$ContentPlaceHolder1$S_ShenQingBiaoNo": "",
        "ctl00$ContentPlaceHolder1$S_BiaoDuanMoney_From": "",
        "__VIEWSTATEGENERATOR": soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value'],
        "ctl00$ContentPlaceHolder1$HidState": "0",
        "__EVENTVALIDATION": soup.find('input', {'id': '__EVENTVALIDATION'})['value'],
        "__EVENTTARGET": "ctl00$ContentPlaceHolder1$Pager",
        "ctl00$ContentPlaceHolder1$S_BiaoDuanNo": "",
        "ctl00$ContentPlaceHolder1$S_PName": ""
    }
    return data


def GetSelfckInfo(id, url):
    """获取工程状态"""
    if url.startswith('http'):
        html = Req_get(url)
        if html is None:
            SelfckIinfo[id] = ''
            return
        soup = BeautifulSoup(html, 'lxml')
        findResult = soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_lblIsZaiJian'})
        if findResult is None:
            SelfckIinfo[id] = ''
            return
        gczt = findResult.text
        if '在建工程' in gczt:
            gczt = '在建'
        elif '撤出工程' in gczt:
            gczt = '已竣工'
        else:
            gczt = ''
        SelfckIinfo[id] = gczt
    else:
        SelfckIinfo[id] = ''

def GetSelfYszmInfo(id, url):
    logging.info('获取自备汇总图片html')
    html = Req_get(url)
    if html is None:
        logging.info('获取自备汇总图片url')
        return
    begin_url = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd'
    end_rul = re.findall(r'OpenWindow\(\'..(.*?)\'', html)
    if len(end_rul) == 0:
        logging.info('未找到验收证明图片url')
        return
    end_rul = end_rul[0] if end_rul else ''
    hole_url = begin_url + end_rul
    pic_html = Req_get(hole_url)
    if pic_html is None:
        logging.info('获取验收证明图片html失败')
        return
    soup = BeautifulSoup(pic_html, 'lxml')
    data = {
        "ctl00$ScriptManager1": "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$rblType$2",
        "__EVENTARGUMENT": soup.find('input', {'id': '__EVENTARGUMENT'})['value'],
        "__VIEWSTATE": soup.find('input', {'id': '__VIEWSTATE'})['value'],
        "ctl00$ContentPlaceHolder1$rblType": soup.find('input', {'id': 'ctl00_ContentPlaceHolder1_rblType_2'})['value'],
        "__VIEWSTATEGENERATOR": soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value'],
        "__EVENTVALIDATION": soup.find('input', {'id': '__EVENTVALIDATION'})['value'],
        "__EVENTTARGET": soup.find('input', {'id': '__EVENTTARGET'})['value'],
        "__LASTFOCUS": soup.find('input', {'id': '__LASTFOCUS'})['value']
    }
    next_page = Req_post(hole_url, data)
    if next_page is None:
        logging.info('获取验收证明图片url失败')
        return
    soup2 = BeautifulSoup(next_page, 'lxml')
    find_pic_request_url = soup2.find('a', {'target': '_blank'})
    if find_pic_request_url is None:
        logging.info('查找图片url失败')
        return
    pic_request_url = find_pic_request_url['href']
    logging.info(pic_request_url)
    url_real_base = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd/ShiGongInfo/'
    total_url = url_real_base + pic_request_url
    logging.info('下载验收证明图片...')
    real = Req_get_v2(total_url)
    if real is None:
        logging.info('下载验收证明图片失败')
        return
    logging.info('开始文字识别...')
    ocr_ret = local_picture_ocr(real.content)
    if ocr_ret is None:
        logging.info('文字识别失败！')
        return
    logging.info(ocr_ret)
    findJunGongDate = u'竣工日期.*?(\d{4}).*?(\d{1,2}).*?(\d{1,2})'
    pattern = re.compile(findJunGongDate)
    results = pattern.findall(ocr_ret)
    jgrq = ''
    logging.info('搜索竣工日期')
    if len(results):
        logging.info(results[0])
        if int(results[0][1]) <= 12 and \
                int(results[0][1]) >= 1 and \
                int(results[0][2]) >= 1 and \
                int(results[0][2]) <= 31 and \
                int(results[0][0]) <= 2050 and \
                int(results[0][0]) >= 2000:
            jgrq = '{0}-{1}-{2}'.format(results[0][0], results[0][1], results[0][2])
            logging.info(jgrq)
    findYanShouDate = u'验收日期.*?(\d{4}).*?(\d{1,2}).*?(\d{1,2})'
    patternYanShou = re.compile(findYanShouDate)
    resultsYanShou = patternYanShou.findall(ocr_ret)
    ysrq = ''
    logging.info('搜索验收日期')
    if len(resultsYanShou):
        logging.info(resultsYanShou[0])
        if int(resultsYanShou[0][1]) >= 1 and \
                int(resultsYanShou[0][1]) <= 12 and \
                int(resultsYanShou[0][2]) >= 1 and \
                int(resultsYanShou[0][2]) <= 31 and \
                int(resultsYanShou[0][0]) <= 2050 and \
                int(resultsYanShou[0][0]) >= 2000:
            ysrq = '{0}-{1}-{2}'.format(resultsYanShou[0][0], resultsYanShou[0][1], resultsYanShou[0][2])
            logging.info(ysrq)
    SelfyszmInfo[id] = [jgrq, ysrq, ocr_ret, total_url]

def GetSelfAchievement(DanWeiGuid, companyName):
    """
    获取业绩信息
    :param DanWeiGuid:
    :return:
    """
    logging.info('正在获取场 自行增加的业绩..')
    url = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd/ShiGongYeJi/ShiGongYeJi_List.aspx?'
    geturl = url + 'ViewType=2&UnitType=5&DanWeiGuid={0}'.format(DanWeiGuid)
    html = Req_get(geturl)
    if html is None:
        return SelfAchievementList, SelfckIinfo, SelfyszmInfo
    allpage = re.findall(u'总页数：<font color="blue"><b>(.*?)</b>', html)[1]
    logging.info('本公司共有 {0} 页自行增加的业绩信息'.format(allpage))
    logging.info('正在获取第 {0} 页自行增加的业绩信息'.format(1))
    GetSelfAchievementList(html)
    data = GetSelfAchievementNextData(html)
    posturl = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd/ShiGongYeJi/ShiGongYeJi_List.aspx?'
    run_posturl = posturl + 'ViewType=2&UnitType=5&DanWeiGuid={0}'.format(DanWeiGuid)

    for p in range(2, int(allpage) + 1):
        logging.info('正在获取第 {0} 页自行增加的业绩信息'.format(p))
        data['__EVENTARGUMENT'] = str(p)
        next_html = Req_post(run_posturl, data)
        if next_html is None:
            raise Exception('获取第 {0} 页自行增加的业绩失败'.format(p))
        GetSelfAchievementList(next_html)
        data = GetSelfAchievementNextData(next_html)
    logging.info('共计找到了 {0} 个业绩'.format(len(SelfAchievementList)))

    for row in SelfAchievementList:
        rowid, ckurl = row[0], row[-1]
        logging.info('正在获取第 {0} 个自行增加的业绩的详细信息'.format(rowid))
        GetSelfckInfo(rowid, ckurl)
        if '已竣工' in SelfckIinfo[rowid] and CheckIfNeedGetYszmInfo(companyName, row[1], row[2], row[3], row[4], row[5]):
            GetSelfYszmInfo(rowid, ckurl)
        else:
            logging.info('已存在ocr信息')

    return SelfAchievementList, SelfckIinfo, SelfyszmInfo


def GetManagerList(html):
    """
    获取经理列表
    :param html:
    :return: 经理人属性
    """
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_Datagrid1'})
    if table is None:
        raise Exception('获取当前页，项目经理表失败')
    _tr = table.findAll('tr')[1:]
    for tr in _tr:
        _td = tr.findAll('td')
        name = _td[1].text.strip()
        level = _td[4].text.strip()
        number = _td[5].text.strip()
        try:
            PMGuid = _td[6].input['onclick'].split("'")[1].split('PMGuid=')[1].split('&')[0]
        except:
            PMGuid = ''
        ManagerList[name] = [level, number, PMGuid]


def GetManagerNextData(html):
    """
    拿到翻页需要用的验证信息
    :param html:
    :return: 下一页的请求body
    """
    soup = BeautifulSoup(html, 'lxml')
    data = {
        "__EVENTARGUMENT": "2",
        "__VIEWSTATE": soup.find('input', {'id': '__VIEWSTATE'})['value'],
        "ctl00$ContentPlaceHolder1$S_PMName": "",
        "ctl00$ScriptManager1": "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$Pager",
        "__VIEWSTATEGENERATOR": soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value'],
        "ctl00$ContentPlaceHolder1$HidState": "0",
        "__EVENTVALIDATION": soup.find('input', {'id': '__EVENTVALIDATION'})['value'],
        "__EVENTTARGET": "ctl00$ContentPlaceHolder1$Pager"
    }
    return data


def GetManagerInfo(name, url):
    """
    获取经理的职称
    :param name:
    :param url:
    :return:
    """
    html = Req_get(url)
    if html is None:
        ManagerInfo[name] = ''
        return
    soup = BeautifulSoup(html, 'lxml')
    try:
        zhicheng = soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_ZhiCheng_1895'}).text
    except:
        zhicheng = ''
    ManagerInfo[name] = zhicheng


def GetManager(DanWeiGuid):
    """
    获取经理
    :param DanWeiGuid:
    :return:
    """
    logging.info('正在获取经理列表..')
    url = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd/PMInfo/PM_List.aspx?'
    geturl = url + 'ViewType=2&UnitType=5&DanWeiGuid={0}'.format(DanWeiGuid)
    html = Req_get(geturl)
    if html is None:
        return ManagerList, ManagerInfo
    find_result = re.findall(u'总页数：<font color="blue"><b>(.*?)</b>', html)
    if len(find_result) == 0:
        raise Exception('获取经理信息总页数失败')
    allpage = find_result[0]
    logging.info('本公司共有 {0} 页经理信息'.format(allpage))
    logging.info('正在获取第 {0} 页业绩信息'.format(1))
    GetManagerList(html)
    data = GetManagerNextData(html)
    posturl = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd/PMInfo/PM_List.aspx?'
    runpost_url = posturl + 'ViewType=2&UnitType=5&DanWeiGuid={0}'.format(DanWeiGuid)

    for p in range(2, int(allpage) + 1):
        logging.info('正在获取第 {0} 页经理信息'.format(p))
        data['__EVENTARGUMENT'] = str(p)
        next_html = Req_post(runpost_url, data=data)
        if next_html is None:
            raise Exception('获取第 {0} 页经理信息失败'.format(p))
        GetManagerList(next_html)
        data = GetManagerNextData(next_html)

    logging.info('共计找到了 {0} 个经理'.format(len(ManagerList)))

    for name, info in ManagerList.items():
        PMurl_demo = 'http://gcjy.njzwfw.gov.cn/HuiYuan/BackEnd/PMInfo/PM_Detail.aspx?'
        PM_runurl = PMurl_demo + 'ViewType=2&PMGuid={0}&DanWeiGuid={1}'.format(info[2], DanWeiGuid)
        logging.info('正在获取 {0} 的信息'.format(name))
        GetManagerInfo(name, PM_runurl)

    return ManagerList, ManagerInfo
