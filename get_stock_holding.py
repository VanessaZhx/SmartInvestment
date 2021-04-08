import common_dict
from utils_fund_info import get_invest_position
from utils_stock_info import *


def get_stock_holding_zjh():
    """
    获取证监会分类下的持股信息
    """
    # 读入基金代码数据
    with open('src/fund_code.txt', 'r') as f:
        line = f.readline().strip()
        fundCodes = line.split(" ")

    # 遍历基金代码
    cnt = 0
    for fundCode in fundCodes:
        print(f'正在获取 {fundCode} 的持仓信息......')
        # 获取持仓股票代码，持仓比例
        invCodes, invPercentages = get_invest_position(fundCode)
        if not invCodes:
            cnt += 1
            print(f'基金 {fundCode} 暂无持仓信息......(进度{cnt}/{len(fundCodes)})\n')
            continue

        invCapStocks = []
        invIndustries = []
        # 获取股票股本，股票行业类别
        for incCode in invCodes:
            capStock = get_capital_stock(incCode)
            invCapStocks.append(capStock)
            industry = common_dict.zjhIndustryNameToCode[get_industry_zjh(incCode).split("-")[0]]
            invIndustries.append(industry)

        df = pd.DataFrame({
            'invCode': invCodes,
            'invPercentage': invPercentages,
            'invCapStock': invCapStocks,
            'invIndustry': invIndustries
        })
        # 添加到 csv 表格中
        cnt += 1
        df.to_csv(f'src/invest_info/invest_info_{fundCode}.csv', index=False, sep=',')
        print(f'{fundCode} 的持仓信息获取成功(进度{cnt}/{len(fundCodes)})\n')


def get_stock_holding_sw():
    """
    获取申万分类下的持股信息
    """
    # 读入基金代码数据
    with open('src/fund_code.txt', 'r') as f:
        line = f.readline().strip()
        fundCodes = line.split(" ")

    # 遍历基金代码
    cnt = 0
    for fundCode in fundCodes:
        print(f'正在获取 {fundCode} 的持仓信息......')
        # 获取持仓股票代码，持仓比例
        invCodes, invPercentages = get_invest_position(fundCode)
        if not invCodes:
            cnt += 1
            print(f'基金 {fundCode} 暂无持仓信息......(进度{cnt}/{len(fundCodes)})\n')
            continue

        invCapStocks = []
        invIndustries = []
        # 获取股票股本，股票行业类别
        for incCode in invCodes:
            capStock = get_capital_stock(incCode)
            invCapStocks.append(capStock)
            industry = get_industry_sw(incCode)
            invIndustries.append(industry)

        df = pd.DataFrame({
            'invCode': invCodes,
            'invPercentage': invPercentages,
            'invCapStock': invCapStocks,
            'invIndustry': invIndustries
        })
        # 添加到 csv 表格中
        cnt += 1
        df.to_csv(f'src/invest_info_sw/invest_info_{fundCode}.csv', index=False, sep=',')
        print(f'{fundCode} 的持仓信息获取成功(进度{cnt}/{len(fundCodes)})\n')


if __name__ == '__main__':
    get_stock_holding_sw()
