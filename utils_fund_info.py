import datetime
import json
import re
import execjs
import requests
import pandas as pd


def get_all_equity_code():
    """
    获取全部股票型基金的基金代码

    :param:
        None
    :return:
        count: 股票型基金总数
        allCode: 股票型基金代码列表
    """
    url = 'http://fund.eastmoney.com/js/fundcode_search.js'
    content = requests.get(url)
    jsContent = execjs.compile(content.text)
    rawData = jsContent.eval('r')
    allCode = []
    count = 0
    for data in rawData:
        if data[3] == '股票型':
            allCode.append(data[0])
            count = count + 1
    return count, allCode


def get_establish_date(found_id):
    """
    获取特定基金成立日期

    :param:
        code: 基金代码
    :return:
        str 特定基金成立日期
    """

    url = 'http://fund.eastmoney.com/' + found_id + '.html?spm=search'
    response = requests.get(url)
    text = response.content.decode('utf-8')

    start_date = re.findall('<td><span class="letterSpace01">成 立 日</span>：(.*?)</td>', text)
    if not start_date:
        start_date = ['N/A']
    return start_date[0]


def get_public_dates(fund_code: str):
    """
    获取基金持仓的公开日期

    :param:
        code: 基金代码
    :return:
        公开持仓的日期列表
    """
    headers = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
        'Accept': '*/*',
        'Referer': 'http://fund.eastmoney.com/data/fundranking.html',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    }
    params = (
        ('FCODE', fund_code),
        ('MobileKey', '3EA024C2-7F22-408B-95E4-383D38160FB3'),
        ('OSVersion', '14.3'),
        ('appVersion', '6.3.8'),
        ('cToken', 'a6hdhrfejje88ruaeduau1rdufna1e--.6'),
        ('deviceid', '3EA024C2-7F22-408B-95E4-383D38160FB3'),
        ('passportid', '3061335960830820'),
        ('plat', 'Iphone'),
        ('product', 'EFund'),
        ('serverVersion', '6.3.6'),
        ('version', '6.3.8'),
    )

    json_response = requests.get(
        'https://fundmobapi.eastmoney.com/FundMNewApi/FundMNIVInfoMultiple', headers=headers, params=params).json()
    if json_response['Datas'] is None:
        return []
    return json_response['Datas']


def get_fund_name(fund_id):
    """
    获取特定基金基金名

    :param:
        code: 基金代码
    :return:
        str 特定基金基金名
    """

    url = 'http://fundgz.1234567.com.cn/js/'+ fund_id +'.js'
    response = requests.get(url)
    content = response.text

    # 正则表达式匹配
    pattern = r'^jsonpgz\((.*)\)'
    # 查找结果
    search = re.findall(pattern, content)
    # 遍历结果
    for i in search:
        data = json.loads(i)
        return data['name']
    return ''


def get_fund_equity_return(fund_code, start_date, end_date):
    """
    获取特定基金在时间范围内的基金净值

    :param:
        fund_code:   基金代码
        start_date:  起始时间
        end_date：   终止时间
    :return:
         list(dict{x:毫秒时间戳, y:基金净值})
    """
    url = 'http://fund.eastmoney.com/pingzhongdata/' + fund_code + '.js'
    content = requests.get(url).text
    jsContent = execjs.compile(content)
    trend_data = jsContent.eval('Data_netWorthTrend')

    trend = []
    for data in trend_data:
        if int(start_date) <= data['x'] / 1000 <= int(end_date):
            info = [data['x'], data['y']]
            # info = pd.DataFrame(info)
            trend.append(info)

    return trend


def get_invest_position(fund_code):
    """
    获取特定基金的持仓股票代码与持仓占比

    :param:
       fund_code: 基金代码
    :return:
       持仓股票代码列表 持仓占比列表
    """
    # 爬取持仓股票列表
    url = 'http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code=%s&year=2020&month=12' % fund_code
    content = requests.get(url, timeout=50)
    text = content.content.decode('utf-8')
    invest_code = re.findall(r"股吧</a><a href='//quote.eastmoney.com/..(.*?).html' >行情", text)
    percentages = re.findall(r"style='display:none'>档案</a></td><td class='tor'>(.*?)%</td>", text)
    percentages = list(map(float, percentages))

    # 排除占比过少的股票（小于0.0%）
    i = len(percentages)
    for percentage in enumerate(percentages):
        if percentage[1] == 0:
            i = percentage[0]
            break
    invest_code = invest_code[0:i]
    percentages = percentages[0:i]

    return invest_code, percentages


if __name__ == '__main__':
    now = datetime.datetime.now().timestamp()
    dateLim = (datetime.datetime.now() - datetime.timedelta(days=365)).timestamp()
    print(get_fund_equity_return('001028', dateLim, now))