import pandas as pd
import common_dict
import os


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
    files = get_files('invest_info')

    print("文件列表获取成功，正在构建数据......")
    fundMap = []

    for file in files:
        invData = pd.read_csv(f'invest_info/'+ file)
        fundCode = file[12:18]
        row = []
        for col in common_dict.fundDataColumn:
            if col == 'fund_code':
                row.append(str(fundCode))
            else:
                invests = invData[invData['invIndustry'] == col]

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
    fundMap = pd.DataFrame(fundMap, columns=common_dict.fundDataColumn)

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


if __name__ == '__main__':
    set_fund_data(0, 'ZJH')
