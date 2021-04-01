import json
import re
import pandas as pd
import requests
import common_dict


def stand_inv_code(inv_code):
    """
    将股票代码转换为标准格式（交易所+标号，如SH000001）

    :param:
        inv_code: 股票代码
    :return:
        标准格式股票代码
    """
    if inv_code[0] == '6':              # 若股票代码以6开头，则为上交所股票
        s_code = 'SH' + inv_code
    elif inv_code[0] == '/':            # 若以/开头，则为港交所股票
        s_code = inv_code[1:]
    else:                               # 否则为深交所股票
        s_code = 'SZ' + inv_code
    return s_code


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


def get_capital_stock(inv_code):
    """
    获取特定股票的信息

    :param:
        inv_code: 股票代码
    :return:
        特定股票股本(万股)
    """
    code = stand_inv_code(inv_code)

    # 若为港股，需要单独抓取处理
    if len(code) == 5:
        url = 'http://emweb.securities.eastmoney.com/PC_HKF10/CapitalStructure/PageAjax?code=%s' % code
        content = requests.get(url, timeout=50)
        jsContent = json.loads(content.text)
        capital_stock = jsContent['gbjg']['yfxptg']
        capital_stock = float(capital_stock.replace(',', '')) / 10000
    else:
        url = 'http://f10.eastmoney.com/CapitalStockStructure/CapitalStockStructureAjax?code=%s' % code
        content = requests.get(url, timeout=50)
        jsContent = json.loads(content.text)
        if not jsContent['ShareChangeList']:
            capital_stock = 0
        else:
            capital_stock = jsContent['ShareChangeList'][1]['changeList'][0]
            capital_stock = float(capital_stock.replace(',', ''))
    return capital_stock


def get_industry(inv_code):
    """
    获取特定股票的行业信息

    :param:
        inv_code: 股票代码
    :return:
        特定股票行业信息（证监会分类码）
    """
    code = stand_inv_code(inv_code)

    # 若为港股，标记为非H股
    if len(code) == 5:
        capital_stock = '非H股'
    else:
        url = 'http://f10.eastmoney.com/CompanySurvey/CompanySurveyAjax?code=%s' % code
        content = requests.get(url, timeout=50)
        capital_stock = json.loads(content.text)['jbzl']['sszjhhy']
    return capital_stock


if __name__ == '__main__':
    # 读入基金代码数据
    with open('fund_code.txt', 'r') as f:
        line = f.readline().strip()
        fundCodes = line.split(" ")

    # 遍历基金代码
    cnt = 0
    for fundCode in fundCodes:
        print(f'正在获取 {fundCode} 的持仓信息......')
        # 获取持仓股票代码，持仓比例
        invCodes, invPercentages = get_invest_position(fundCode)
        invCapStocks = []
        invIndustries = []
        # 获取股票股本，股票行业类别
        for incCode in invCodes:
            capStock = get_capital_stock(incCode)
            invCapStocks.append(capStock)
            industry = common_dict.zjhIndustryNameToCode[get_industry(incCode).split("-")[0]]
            invIndustries.append(industry)

        df = pd.DataFrame({
            'invCode': invCodes,
            'invPercentage': invPercentages,
            'invCapStock': invCapStocks,
            'invIndustry': invIndustries
        })
        # 添加到 csv 表格中
        cnt += 1
        df.to_csv(f'invest_info/invest_info_{fundCode}.csv', index=False, sep=',')
        print(f'{fundCode} 的持仓信息获取成功(进度{cnt}/{len(fundCodes)})\n')
