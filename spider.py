from datetime import datetime
import json
import os
import re

from lxml import etree
import requests

import utils


BASE_URL = 'https://s.weibo.com'
JSON_DIR = './raw'
ARCHIVE_DIR = './archives'


def getHTML(url):
    ''' 获取网页 HTML 返回字符串

    Args:
        url: str, 网页网址
    Returns:
        HTML 字符串
    '''
    # Cookie 有效期至2023-02-10
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
        'Cookie': 'SUB=_2AkMVWDYUf8NxqwJRmP0Sz2_hZYt2zw_EieKjBMfPJRMxHRl-yj9jqkBStRB6PtgY-38i0AF7nDAv8HdY1ZwT3Rv8B5e5; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFencmWZyNhNlrzI6f0SiqP'
    }
    response = requests.get(url, headers=headers)
    if response.encoding == 'ISO-8859-1':
        response.encoding = response.apparent_encoding if response.apparent_encoding != 'ISO-8859-1' else 'utf-8'
    return response.text


# 使用 xpath 解析 HTML
def parseHTMLByXPath(content):
    ''' 使用 xpath 解析 HTML, 提取榜单信息

    Args:
        content: str, 待解析的 HTML 字符串
    Returns:
        榜单信息的字典 字典
    '''
    html = etree.HTML(content)

    titles = html.xpath(
        '//tr[position()>1]/td[@class="td-02"]/a[not(contains(@href, "javascript:void(0);"))]/text()')
    hrefs = html.xpath(
        '//tr[position()>1]/td[@class="td-02"]/a[not(contains(@href, "javascript:void(0);"))]/@href')
    hots = html.xpath(
        '//tr[position()>1]/td[@class="td-02"]/a[not(contains(@href, "javascript:void(0);"))]/../span/text()')
    titles = [title.strip() for title in titles]
    hrefs = [BASE_URL + href.strip() for href in hrefs]
    hots = [int(hot.strip().split(' ')[-1])
            for hot in hots]  # 该处除了热度还会返回大致分类，形如 `剧集 53412536`，前为分类，后为热度

    correntRank = {}
    for i, title in enumerate(titles):
        correntRank[title] = {'href': hrefs[i], 'hot': hots[i]}

    return correntRank


# 更新本日榜单
def updateJSON(correntRank):
    ''' 更新当天的 JSON 文件

    Args:
        correntRank: dict, 最新的榜单信息
    Returns:
        与当天历史榜单对比去重, 排序后的榜单信息字典
    '''
    filename = datetime.today().strftime('%Y%m%d') + '.json'
    filename = os.path.join(JSON_DIR, filename)

    # 文件不存在则创建
    if not os.path.exists(filename):
        utils.save(filename, {})

    historyRank = json.loads(utils.load(filename))
    for k, v in correntRank.items():
        # 若当前榜单和历史榜单有重复的，取热度数值(名称后面的数值)更大的一个
        if k in historyRank:
            historyRank[k]['hot'] = max(
                historyRank[k]['hot'], correntRank[k]['hot'])
        # 若没有，则添加
        else:
            historyRank[k] = v

    # 将榜单按 hot 值排序
    rank = {k: v for k, v in sorted(
        historyRank.items(), key=lambda item: item[1]['hot'], reverse=True)}

    # 更新当天榜单 json 文件
    utils.save(filename, rank)
    return rank


def updateReadme(rank):
    ''' 更新 README.md

    Args:
        rank: dict, 榜单信息
    Returns:
        None
    '''
    filename = './README.md'

    line = '1. [{title}]({href}) {hot}'
    lines = [line.format(title=k, hot=v['hot'], href=v['href'])
             for k, v in rank.items()]
    rank = '\n'.join(lines)

    rank = '最后更新时间 {}\n\n'.format(
        datetime.now().strftime('%Y-%m-%d %X')) + rank
    rank = '<!-- Rank Begin -->\n\n' + rank + '\n<!-- Rank End -->'

    content = re.sub(
        r'<!-- Rank Begin -->[\s\S]*<!-- Rank End -->', rank, utils.load(filename))
    utils.save(filename, content)


def main():
    url = '/top/summary'

    content = getHTML(BASE_URL + url)
    # with open('test.html', 'w', encoding='utf-8') as f:
    #     f.write(content)
    # print(content)
    correntRank = parseHTMLByXPath(content)
    rankJSON = updateJSON(correntRank)
    updateReadme(rankJSON)


if __name__ == '__main__':
    main()
