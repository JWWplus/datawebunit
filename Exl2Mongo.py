# coding=utf-8
import logging
from pymongo import MongoClient
import pandas as pd

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

# dataWebUnit = MongoClient('localhost:27017').datawebunit
dataWebUnit = MongoClient('dataTask01:29017').test
df = pd.read_excel('分页面打点纪录点.xlsx', sheetname=['4.6', '4.7', '4.8', '4.9', '4.10'])
# df = pd.read_excel('分页面打点记录点 new.xlsx', sheetname=['4.11', '4.12', '4.13'])
sheetname = ['4.6', '4.7', '4.8', '4.9', '4.10']
# sheetname = ['4.11', '4.12', '4.13']


def exl2mongo():
    for sheet in sheetname:
        logging.info('start to insert data appversion:%s' % sheet)
        dataWebUnit.appversion.insert({
            "appversion": sheet,
        })
        df[sheet] = df[sheet].fillna('')
        for i in df[sheet].index:
            logging.info('start insert sheet %s line %d' % (sheet, i + 1))
            row = df[sheet].ix[i]
            # 如果页面没有直接跳过这一行
            if row[u'页面'] == '':
                continue

            if row['se_category'].lstrip() or row['se_action'].lstrip():
                dataWebUnit.datainfo.insert({
                    'appversion': sheet,
                    'page': row[u'页面'],
                    'platform': 'Android',
                    'pm': row.get(u'产品负责人', ''),
                    'event': row[u'事件'],
                    'object': row[u'对象'],
                    'page_key': row[u'page_key'],
                    'type': row[u'type'],
                    'sub_type': row[u'sub_type'],
                    'note': row[u'额外信息'] + ', ' + row['Android'],
                    'se_category': row[u'se_category'],
                    'se_action': row[u'se_action'],
                })

            if row['se_category.1'].lstrip() or row['se_action.1'].lstrip():
                dataWebUnit.datainfo.insert({
                    'appversion': sheet,
                    'page': row[u'页面'],
                    'platform': 'iOS',
                    'pm': row.get(u'产品负责人', ''),
                    'event': row[u'事件'],
                    'object': row[u'对象'],
                    'page_key': row[u'page_key'],
                    'type': row[u'type'],
                    'sub_type': row[u'sub_type'],
                    'note': row[u'额外信息'] + ', ' + row['iOS'],
                    'se_category': row[u'se_category.1'],
                    'se_action': row[u'se_action.1'],
                })

            if row['se_category.2'].lstrip() or row['se_action.2'].lstrip():
                dataWebUnit.datainfo.insert({
                    'appversion': sheet,
                    'page': row[u'页面'],
                    'platform': 'H5',
                    'pm': row.get(u'产品负责人', ''),
                    'event': row[u'事件'],
                    'object': row[u'对象'],
                    'page_key': row[u'page_key'],
                    'type': row[u'type'],
                    'sub_type': row[u'sub_type'],
                    'note': row[u'额外信息'] + ', ' + row['H5'],
                    'se_category': row[u'se_category.2'],
                    'se_action': row[u'se_action.2'],
                })


def add_default_user():
    dataWebUnit.user.insert({
        'user': 'admin',
        'password': 'admin',
        'role': 'admin'
    })


if __name__ == "__main__":
    # exl2mongo()
    add_default_user()
