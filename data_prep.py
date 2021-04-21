import datetime
import time

import pandas as pd
import common_dict
import os

from utils_fund_info import get_fund_equity_return


def get_files(root_dir):
    list_dirs = os.walk(root_dir)
    file_list = []
    for root, dirs, files in list_dirs:
        for f in files:
            file_list.append(f)
    return file_list


def set_fund_data(mode, source):
    """
    将基金信息汇总计算为聚类结构

    :param:
        mode: mode = 0, 获取百分比数据结构；mode = 1, 获取总股本数据结构
        source: source = 'ZJH'，分类来源证监会；source = ‘SW’分类来源申万

    :return:
        -
    """
    # 读入基金代码数据
    print("正在获取列表文件......")
    if source == 'ZJH':
        files = get_files('src/invest_info')
    else:
        files = get_files('src/invest_info_sw')

    print("文件列表获取成功，正在构建数据......")
    fundMap = []
    fundDataColumn = []
    for file in files:
        if source == 'ZJH':
            invData = pd.read_csv(f'src/invest_info/' + file)
            fundDataColumn = common_dict.fundDataColumnZJH
        else:
            invData = pd.read_csv(f'src/invest_info_sw/' + file)
            fundDataColumn = common_dict.fundDataColumnSW
        fundCode = file[12:18]
        row = []

        for col in fundDataColumn:
            if col == 'fund_code':
                row.append(str(fundCode))
            else:
                invests = invData[invData['invIndustry'] == int(col)]

                if invests.empty:
                    row.append(0)
                elif mode == 0:
                    s = invests['invPercentage'].sum()
                    row.append(s)
                else:
                    multi = invests.apply(lambda row: row['invPercentage'] * row['invCapStock'] / 100, axis=1)
                    multi = multi.sum()
                    row.append(multi)
        fundMap.append(row)
    print("构建成功，正在写入数据......")
    fundMap = pd.DataFrame(fundMap, columns=fundDataColumn)

    file_name = 'fund_map_' + str(mode) + '_' + source + '.csv'
    fundMap.to_csv(file_name, index=False, sep=',')

    print("数据已写入到 ", file_name, " 中，数据预览如下")
    print(fundMap)


def get_fund_data(file):
    """
    读取文件中的基金信息

    :return:
        基金信息结构
    """
    fund_data = pd.read_csv(file, dtype = {'fund_code': object})
    return fund_data


def set_fund_trend(source, start_date, end_date):
    # 读入基金代码数据
    print("正在获取列表文件......")
    if source == 'ZJH':
        files = get_files('src/invest_info')
    else:
        files = get_files('src/invest_info_sw')

    # 遍历文件，获取模型中用到数据近一年的净值信息
    trends = pd.DataFrame()
    cnt = 0
    for file in files:
        fundCode = file[12:18]
        daily_data = get_fund_equity_return_joinquant(fundCode, start_date, end_date)
        # daily_data = get_fund_equity_return(fundCode, start_date, end_date)
        trend = pd.DataFrame({'code': str(fundCode)}, index=[0])
        for data in daily_data:
            time_local = time.localtime(data[0] / 1000)
            dt = time.strftime("%Y-%m-%d", time_local)
            trend[dt] = data[1]
        if trends.empty:
            trends = trend
        else:
            trends = pd.concat([trends, trend], ignore_index=True)
        cnt += 1
        print(f'{fundCode} 的净值信息获取成功(进度{cnt}/{len(files)})')

    # 输出结果
    trends.to_csv(f'src/fund_trend_{source}.csv', index=False, sep=',')
    print(f"数据已写入到 src/fund_trend_{source}.csv' 中，数据预览如下")
    print(trends)


if __name__ == '__main__':
    now = datetime.datetime.now().timestamp()
    dateLim = (datetime.datetime.now() - datetime.timedelta(days=365)).timestamp()
    set_fund_trend('ZJH', dateLim, now)
    # set_fund_data(1, 'SW')
