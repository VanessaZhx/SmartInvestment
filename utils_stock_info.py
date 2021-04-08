from jqdatasdk import *
auth('13891981217','981217')


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


def get_industry_zjh(inv_code):
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
        industry = '非H股'
    else:
        url = 'http://f10.eastmoney.com/CompanySurvey/CompanySurveyAjax?code=%s' % code
        content = requests.get(url, timeout=50)
        industry = json.loads(content.text)['jbzl']['sszjhhy']
    return industry


def get_industry_sw(inv_code):
    """
    获取特定股票的行业信息

    :param:
        inv_code: 股票代码
    :return:
        特定股票行业信息（申万分类码）
    """
    # 若为港股，标记为非H股
    if inv_code[0] == '/':
        industry = '000000'
    else:
        code = normalize_code(inv_code)
        info = get_industry(code, date=None)
        industry = info[code]['sw_l1']['industry_code']
    return industry

