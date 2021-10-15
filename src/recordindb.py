import os
import sqlite3
from typing import Optional
from datetime import datetime

dbPath = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', 'data', 'info.db')


def getLastUpdateDateTime() -> Optional[datetime]:
    # 获取最近一次保存的日期
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute('''
        create table if not exists images (
            id integer primary key autoincrement,
            title text,
            copyright text,
            fullstartdate text,
            createtime timestamp default CURRENT_TIMESTAMP,
            url text
            )
        ''')
    cursor.execute(
        'select fullstartdate from images order by createtime, fullstartdate desc limit 1'
    )
    lastDate = cursor.fetchone()
    cursor.close()
    conn.close()
    if lastDate is None:
        return None
    else:
        return lastDate[0]


def saveRecords(records=[]) -> None:
    def _convert2Tuple(record):
        return (record['title'], record['copyright'], record['fullstartdate'], record['url'])

    if len(records) == 0:
        return
    # 保存记录
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.executemany(
        'insert into images (title, copyright, fullstartdate, url) values (?, ?, ?, ?)',
        list(map(_convert2Tuple, records))
    )
    conn.commit()
    cursor.close()
    conn.close()
