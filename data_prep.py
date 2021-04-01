import pandas as pd
import common_dict


def set_fund_data():
    """
    将基金信息汇总计算为聚类结构

    :return:
        -
    """
    # 读入基金代码数据
    print("正在读入数据......")
    with open('fund_code.txt', 'r') as f:
        line = f.readline().strip()
        fundCodes = line.split(" ")

    print("读入成功，正在构建数据......")
    fundMap = []
    for fundCode in fundCodes:
        invData = pd.read_csv(f'invest_info/invest_info_{fundCode}.csv')

        row = []
        for col in common_dict.fundDataColumn:
            if col == 'fund_code':
                row.append(fundCode)
            else:
                invests = invData[invData['invIndustry'] == col]

                if invests.empty:
                    row.append(0)
                else:
                    multi = invests.apply(lambda row: row['invPercentage'] * row['invCapStock'] / 100, axis=1)
                    multi = multi.sum()
                    row.append(multi)
        fundMap.append(row)
    print("构建成功，正在写入数据......")
    fundMap = pd.DataFrame(fundMap, columns=common_dict.fundDataColumn)
    fundMap.to_csv(f'fund_map.csv', index=False, sep=',')

    print("数据已写入到 fund_map.csv 中，数据预览如下")
    print(fundMap)


def get_fund_data():
    """
    读取文件中的基金信息

    :return:
        基金信息结构
    """
    fund_data = pd.read_csv(f'fund_map.csv')
    return fund_data


if __name__ == '__main__':
    set_fund_data()
