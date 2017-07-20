# coding=utf-8
# create database tlog character set utf8mb4;
import logging
import pandas as pd
from app import Appversion, PageInfo, db, user

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

df = pd.read_excel('分页面打点纪录点4.6-4.9.xlsx', sheetname=['4.6', '4.7', '4.8', '4.9', '4.10'])
sheetname = ['4.6', '4.7', '4.8', '4.9', '4.10']


def exl2mysqlforH5():
    for sheet in sheetname:
        df[sheet] = df[sheet].fillna('')
        H5 = Appversion.query.filter_by(app_version='H5').first()
        if not H5:
            appversion = Appversion('H5')
            db.session.add(appversion)
            db.session.commit()
            app_id = appversion.id
        else:
            appversion = H5
            app_id = H5.id
        for i in df[sheet].index:
            logging.info('start to push line %d appversion: %s' % (i + 1, sheet))
            row = df[sheet].ix[i]
            if not row[u'页面'].strip():
                logging.error(u'该页面字段为空,跳过! appversion:%s, line: %d' % (sheet, i + 1))
                continue

            if row.get('se_category.2', '').strip() or row.get('se_action.2', '').strip():
                if PageInfo.query.filter_by(platform='all', se_action=row[u'se_action.2'],
                                            se_category=row[u'se_category.2'], object=row[u'对象']).first():
                    logging.info(u'该条打点纪录存在！ 跳过')
                    continue
                else:
                    pageinfo_h5 = PageInfo(page=row[u'页面'], event=row[u'事件'], objects=row[u'对象'],
                                           appversion=appversion, types=row['type'], sub_type=row['sub_type'],
                                           pm=row.get(u'产品负责人', ''), page_key=row['page_key'], se_action=row[u'se_action.2'],
                                           se_category=row[u'se_category.2'], platform='all',
                                           notes=str(row[u'额外信息']) + ', ' + row['H5'])
                    db.session.add(pageinfo_h5)
        db.session.commit()


def exl2mysqlforAndr_Ios():
    for sheet in sheetname:
        df[sheet] = df[sheet].fillna('')
        app = Appversion.query.filter_by(app_version=sheet).first()
        if not app:
            appversion = Appversion(sheet)
            db.session.add(appversion)
            db.session.commit()
            app_id = appversion.id
        else:
            appversion = app
            app_id = app.id
        for i in df[sheet].index:
            logging.info('start to push line %d appversion: %s' % (i + 1, sheet))
            row = df[sheet].ix[i]
            if not row[u'页面'].strip():
                logging.error(u'该页面字段为空,跳过! appversion:%s, line: %d' % (sheet, i + 1))
                continue

            if row['se_category'].strip() or row['se_action'].strip():
                pageinfo_and = PageInfo(page=row[u'页面'], event=row[u'事件'], objects=row[u'对象'],
                                        appversion=appversion, types=row['type'], sub_type=row['sub_type'],
                                        pm=row.get(u'产品负责人', ''), page_key=row['page_key'], se_action=row[u'se_action'],
                                        se_category=row[u'se_category'], platform='Android',
                                        notes=str(row[u'额外信息']) + ', ' + row['Android'])
                db.session.add(pageinfo_and)

            if row['se_category.1'].strip() or row['se_action.1'].strip():
                pageinfo_ios = PageInfo(page=row[u'页面'], event=row[u'事件'], objects=row[u'对象'],
                                        appversion=appversion, types=row['type'], sub_type=row['sub_type'],
                                        pm=row.get(u'产品负责人', ''), page_key=row['page_key'],
                                        se_action=row[u'se_action.1'],
                                        se_category=row[u'se_category.1'], platform='iOS',
                                        notes=str(row[u'额外信息']) + ', ' + row['iOS'])
                db.session.add(pageinfo_ios)
        db.session.commit()


def init():
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    init()

    df = pd.read_excel('分页面打点纪录点4.6-4.9.xlsx', sheetname=['4.6', '4.7', '4.8', '4.9', '4.10'])
    sheetname = ['4.6', '4.7', '4.8', '4.9', '4.10']
    exl2mysqlforH5()
    exl2mysqlforAndr_Ios()

    df = pd.read_excel('分页面打点记录点4.11-4.14.xlsx', sheetname=['4.11', '4.12', '4.13', '4.14'])
    sheetname = ['4.11', '4.12', '4.13', '4.14']
    exl2mysqlforH5()
    exl2mysqlforAndr_Ios()

    df = pd.read_excel('分页面打点记录点4.15.xlsx', sheetname=['4.15'])
    sheetname = ['4.15']
    exl2mysqlforH5()
    exl2mysqlforAndr_Ios()
