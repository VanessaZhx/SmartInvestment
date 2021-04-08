from fund_info_utils import *


def get_valid_code():
    print("开始数据筛选！")
    cnt, codes = get_all_equity_code()

    fundDateLim = datetime.datetime.now() - datetime.timedelta(days=365 * 2)

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


if __name__ == '__main__':
    get_valid_code()
