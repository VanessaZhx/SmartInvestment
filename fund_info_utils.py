import json
import re
import requests


def get_fund_name(found_id):
    """
    获取特定基金基金名

    :param:
        code: 基金代码
    :return:
        str 特定基金基金名
    """

    url = 'http://fundgz.1234567.com.cn/js/'+ found_id +'.js'
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


if __name__ == '__main__':
    print(get_fund_name('001186'))