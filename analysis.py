import json
import os

import pandas as pd

import utils

# 所有json合成一个csv，包含 title, url, hot, date
# pandas 分析
# matlabplot 成图
# 词云


def mergeJsonIntoCsv(srcPath):
    pond = []
    for dirname, subdirs, files in os.walk(srcPath):
        pond.extend(files)

    df = pd.DataFrame()
    for file in pond:
        filepath = os.path.join(srcPath, file)
        subDf = pd.read_json(filepath)
        subDf = pd.DataFrame(subDf.values.T, index=subDf.columns, columns=subDf.index)

        subDf = subDf.rename_axis('title')
        subDf = subDf.rename(columns={'href': 'url'})
        subDf['date'] = file.split('.', 1)[0]
        print(filepath, len(subDf))

        df = df.append(subDf)

    df = df.reset_index()

    resname = df['date'].values[0] + '-' + df['date'].values[-1] + '.csv'
    df.to_csv(resname, index=False, sep=',', encoding='utf-8-sig')
    print(df)


def mergeJson(srcPath):
    pond = []
    total = {}
    for dirname, subdirs, files in os.walk(srcPath):
        pond.extend(files)
    for file in pond:
        filepath = os.path.join(srcPath, file)
        basename = file.split('.')[0]
        total[basename] = json.loads(utils.load(filepath))

    utils.save('archives/2021.json', total)


def analysis(df):
    pass


def main():
    srcPath = './raw'
    # mergeJsonIntoCsv(srcPath)
    mergeJson(srcPath)
    # datafile = '20210301-20210910.csv'
    # df = pd.read_csv(datafile, usecols=['title', 'hot', 'date'])
    # df = df['title']
    # print(df['date'].values[0], df['date'].values[-1])




if __name__ == '__main__':
    main()
