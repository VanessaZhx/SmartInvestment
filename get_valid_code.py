import datetime
import requests
import execjs
import re


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


if __name__ == '__main__':
    print("开始数据筛选！")
    cnt, codes = get_all_equity_code()

    now = datetime.datetime.now()
    fundDateLim = datetime.datetime.now() - datetime.timedelta(days=365*2)

    for code in codes:
        # 获取基金最近公开持仓日期
        publicDates = get_public_dates(code)
        estabDate = get_establish_date(code)
        if len(publicDates) == 0:
            codes.remove(code)
        elif datetime.datetime.strptime(str(estabDate), '%Y-%m-%d') > fundDateLim:
            codes.remove(code)

    fund_code = open("fund_code.txt", 'w+')
    for i in fund_code:
        print(i, end=" ", file=fund_code)
    fund_code.close()
    print("数据筛选完毕！")
