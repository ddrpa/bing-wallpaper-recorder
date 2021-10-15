import os
from typing import Optional
from datetime import datetime

filePath = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', 'README.md')

README_HEADER = '''# Bing Wallpaper

![]({url}&w=1000)

Today: [{copyright}]({url})

---

'''


def convertDateTime(dateTime):
    if dateTime is None:
        return ''
    else:
        return datetime.strptime(dateTime, "%Y%m%d%H%M").strftime("%Y-%m-%d")


def updateReadme(records=[]):
    if len(records) == 0:
        return
    records.reverse()
    with open(filePath, 'r+') as f:
        lines = f.readlines()
        lineIndex = 0
        for line in lines:
            lineIndex += 1
            if line.startswith('---'):
                break
        # --- 后面的空行一并删除
        lineIndex += 1
        newlines = [README_HEADER.format(
            url=records[0]['url'], copyright=records[0]['copyright'])]
        for record in records:
            newlines.append('{fullstartdate} | [{copyright}]({url})\n\n'
                            .format(fullstartdate=convertDateTime(record['fullstartdate']),
                                    copyright=record['copyright'],
                                    url=record['url']))
        f.seek(0)
        f.writelines(newlines + lines[lineIndex:])
