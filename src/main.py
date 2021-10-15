#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import readmeedit
import recordindb

from datetime import datetime
import requests
import sys
import os


Headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.40 Safari/537.36',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6'
}
BING_WALLPAPER_API_MAX_REQUEST_COUNT = 8


def imagePath(filename):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data', 'images', filename)


def getNumberRequiredWhenRequest(nullableLastDate):
    now = datetime.now()
    if nullableLastDate is None:
        return BING_WALLPAPER_API_MAX_REQUEST_COUNT
    else:
        lastSaveDate = datetime.strptime(nullableLastDate, "%Y%m%d%H%M")
        return (now - lastSaveDate).days


def requestMeataData(count=1):
    # 请求 bing 壁纸的 API 接口获取壁纸详情
    urlTemplate = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n={count}&uhd=1&mkt=en-US'
    response = requests.get(urlTemplate.format(count=count), headers=Headers)
    return extractMetaDataList(response.json()['images'])


def extractMetaDataList(images=[]):
    def _extract(metaData):
        return {
            'copyright': metaData['copyright'],
            # 通过大陆 IP 请求或 Cokkie 中未传递地区信息时 title 字段为空
            'title': metaData['title'],
            'fullstartdate': metaData['fullstartdate'],
            'url': 'https://cn.bing.com' + metaData['url'].split('&')[0]
        }
    return list(map(_extract, images))


def save(metaDataList, lastUpdateDateTime):
    if len(metaDataList) > 1:
        metaDataList.reverse()
    records = []

    if lastUpdateDateTime is not None:
        # pass image which is already saved
        def _metaDataFilter(metaData):
            return metaData['fullstartdate'] > lastUpdateDateTime
        metaDataList = list(filter(_metaDataFilter, metaDataList))

    for metaData in metaDataList:
        saveImageAsFile(metaData)
        records.append(metaData)

    return records


def saveImageAsFile(metaData):
    # 保存为文件，用日期命名
    response = requests.get(metaData['url'], stream=True, headers=Headers)
    with open(imagePath(metaData['fullstartdate'] + '.jpg'), 'wb') as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(chunk)


def Main():
    lastUpdateDateTime = recordindb.getLastUpdateDateTime()
    imageNumberRequired = getNumberRequiredWhenRequest(lastUpdateDateTime)
    if imageNumberRequired < 1:
        sys.exit(0)
    metaDataList = requestMeataData(imageNumberRequired)
    records = save(metaDataList, lastUpdateDateTime)
    readmeedit.updateReadme(records)
    recordindb.saveRecords(records)
    sys.exit(0)


if __name__ == '__main__':
    Main()
