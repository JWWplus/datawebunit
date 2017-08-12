# coding=utf-8
# uwsgi --http :6234 --wsgi-file app.py  --callable app --processes 4
# --threads 1
"""
按照json格式返回的数据一定要是字符串   否则 AngularJs 解析出错
a=datawebunit.datainfo.aggregate([{'$match':{'appversion':"4.13"}},{"$group":{"_id":"$page",'sum':{'$sum':1}}}])
"""
from flask import Flask, request, send_file, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from pypinyin import lazy_pinyin
from flask.ext.basicauth import BasicAuth
import logging
import json
import sys
import os
from functools import wraps

reload(sys)
sys.setdefaultencoding('utf-8')

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '574326d5933ab8fb840fc177'
app.config['BASIC_AUTH_USERNAME'] = 'red_datateam'
app.config['BASIC_AUTH_PASSWORD'] = '56e171c77aa10f7bb1ace205'

# Create in-memory database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DTWEB_DBURL', 'mysql://root:@localhost/dt-web')
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

basic_auth = BasicAuth(app)


def api_auth(func):
    """
    定义装饰器用于验证访问api的权限
    这个装饰器必须要放在 @app.route 这个装饰器的下面
    """
    @wraps(func)
    def warpper(*args, **kwargs):
        if session.get('is_login'):
            if session['is_login']:
                return func(*args, **kwargs)
        else:
            return redirect(url_for('root'))
    return warpper


# 解决跨域问题在返回标头加上
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


class Appversion(db.Model):
    __tablename__ = 'sea_appversion'
    id = db.Column(db.Integer, primary_key=True, index=True)
    app_version = db.Column(db.Unicode(20))

    def __init__(self, appversion=''):
        self.app_version = appversion

    def __unicode__(self):
        return '%s' % self.app_version

    @property
    def serialize(self):
        return {
            'id': self.id,
            'app_version': self.app_version
        }


class PageInfo(db.Model):
    __tablename__ = 'sea_pageinfo'
    id = db.Column(db.Integer, primary_key=True, index=True)
    page = db.Column(db.Unicode(100), index=True)
    platform = db.Column(db.Unicode(100), index=True)
    event = db.Column(db.Unicode(100), index=True)
    object = db.Column(db.Unicode(100))
    pm = db.Column(db.Unicode(100))
    page_key = db.Column(db.Unicode(100))
    type = db.Column(db.Unicode(100))
    sub_type = db.Column(db.Unicode(100))
    note = db.Column(db.Unicode(300))
    se_category = db.Column(db.Unicode(200))
    se_action = db.Column(db.Unicode(200))

    appversion_id = db.Column(db.Integer, db.ForeignKey('sea_appversion.id'))
    appversion = db.relationship('Appversion', backref=db.backref('pageinfo', lazy='dynamic'))

    def __init__(self, page='', event='', objects='', appversion='', types='', sub_type='',
                 se_category='', se_action='', notes='', platform='', pm='', page_key=''):
        self.page = page
        self.platform = platform
        self.event = event
        self.object = objects
        self.pm = pm
        self.page_key = page_key
        self.type = types
        self.sub_type = sub_type
        self.note = notes
        self.se_action = se_action
        self.se_category = se_category
        self.appversion = appversion

    @property
    def serialize(self):
        return {
            'id': self.id,
            'page': self.page,
            'event': self.event,
            'object': self.object,
            'platform': self.platform,
            'page_key': self.page_key,
            'type': self.type,
            'sub_type': self.sub_type,
            'se_category': self.se_category,
            'se_action': self.se_action,
            'notes': self.note,
            'pm': self.pm,
            'appversion_id': self.appversion_id,
            'appversion': self.appversion.app_version,
        }

    @property
    def tounicode(self):
        return 'page: ' + self.page + ' ' + 'event: ' \
               + self.event + ' ' + 'object: ' + self.object + ' ' + 'platform: ' \
               + self.platform + ' ' + 'page_key: ' + self.page_key + ' ' + 'type: ' \
               + self.type + ' ' + 'sub_type: ' + self.sub_type + ' ' + 'se_category: ' \
               + self.se_category + ' ' + 'se_action: ' + self.se_action + ' ' \
               + 'notes: ' + self.note + ' ' + 'pm: ' + self.pm + ' ' + 'appversion: ' \
               + self.appversion.app_version


class user(db.Model):
    __tablename__ = 'sea_user'
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.Unicode(100))
    password = db.Column(db.Unicode(100))
    role = db.Column(db.Unicode(100))

    def __init__(self, username='', password='', role=''):
        self.username = username
        self.password = password
        self.role = role

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'role': self.role
        }


class log(db.Model):
    __tablename__ = 'sea_log'
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.Unicode(100))
    time = db.Column(db.Unicode(100))
    type = db.Column(db.Unicode(100))
    old_content = db.Column(db.Unicode(1000))
    new_content = db.Column(db.Unicode(1000))

    page_id = db.Column(db.Integer, db.ForeignKey('sea_pageinfo.id'))
    page_info = db.relationship('PageInfo', backref=db.backref('log', lazy='dynamic'))

    def __init__(self, username='', time='', type='', old_content='', new_content='', page_info=''):
        self.username = username
        self.time = time
        self.type = type
        self.old_content = old_content
        self.new_content = new_content
        self.page_info = page_info

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'time': self.time,
            'type': self.type,
            'old_content': self.old_content,
            'new_content': self.new_content,
            'page_id': self.page_id,
        }


"""
该api返回以下信息
GET方式: 获取单条id的信息  用在修改单条数据时获取信息
PUT方式: 修改此id在数据库中的信息
DELETE方式: 删除此id在数据库中的信息
"""


@app.route('/')
def root():
    return send_file("templates/index.html")


@app.route('/api/v1/getinfo/<id_number>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@api_auth
def getinfo_by_id(id_number):
    # 获取单条数据
    if request.method == 'GET':
        resp = PageInfo.query.filter_by(id=id_number).first()
        return jsonify(resp.serialize)

    # 更新单条数据,并将修前后的数据写入到log文件中
    elif request.method == 'PUT':
        data = json.loads(request.data)

        update_record = PageInfo.query.filter_by(id=id_number).first()
        log_record = log(username=data['username'], time=data['time'], type=data['logtype'],
                         old_content=update_record.tounicode, page_info=update_record)
        db.session.add(log_record)
        db.session.commit()

        update_record_appversion = Appversion.query.filter_by(app_version=data['appversion']).first()

        update_record.page = data['page']
        update_record.event = data['event']
        update_record.object = data['object']
        update_record.pm = data.get('pm', '')
        update_record.platform = data['platform']
        update_record.page_key = data['page_key']
        update_record.type = data['type']
        update_record.sub_type = data['sub_type']
        update_record.se_category = data['se_category']
        update_record.se_action = data['se_action']
        update_record.note = data.get('notes', '')
        update_record.appversion_id = update_record_appversion.id

        log_record.new_content = update_record.tounicode
        db.session.commit()

    # 删除单条数据
    elif request.method == 'DELETE':
        record = PageInfo.query.filter_by(id=id_number).first()
        db.session.delete(record)
        db.session.commit()
    return '1'


"""
该api返回以下信息
GET方法: 返回整个数据集的一些信息,目前只返回了所有app版本
POST方法: 用于往数据库中增加新的信息
"""


@app.route('/api/v1/getinfo', methods=['GET', 'POST'])
@api_auth
def getinfo():
    if request.method == 'GET':
        app_version = Appversion.query.all()
        result = [i.serialize for i in app_version]
        resp = {
            'appversion': result,
        }
        return jsonify(resp)

    elif request.method == 'POST':
        data = json.loads(request.data)
        if data:
            appver = Appversion.query.filter_by(app_version=data['appversion']).first()
            data_insert = PageInfo(data['page'], data['event'], data['object'], appver,
                                   data['type'], data['sub_type'], data['se_category'],
                                   data['se_action'], data.get('notes', ''), data['platform'],
                                   data.get('pm', ''), data['page_key'])

            log_record = log(data['username'], data['time'], data['logtype'], '',
                             data_insert.tounicode, data_insert)

            db.session.add(data_insert)
            db.session.add(log_record)
            db.session.commit()
        return '1'


"""
该api返回以下信息
Post方法: 返回对应分页时的记录  有版本选择等等筛选条件
"""


@app.route('/api/v1/getdata', methods=['POST', 'GET'])
@api_auth
def getdata():
    if request.method == 'POST':
        data = json.loads(request.data)
        currentPage = int(data['curPage'])
        numPerPage = int(data['numPerPage'])
        AppVersion = data['AppVersion']
        event = data['event']
        platform = data['platform']
        page = data['page']
        filter_text = data.get('filter_action_text', '')
        filter_cate = data.get('filter_cate_text', '')
        Datainfo = {}

        if not filter_text and not filter_cate:
            if not page:
                if AppVersion:
                    appversion = Appversion.query.filter_by(app_version=AppVersion).first()
                    page_type = db.session.query(PageInfo.page).filter_by(appversion_id=appversion.id).group_by(PageInfo.page).all()
                    page_type.sort(key=lambda char: lazy_pinyin(char)[0][0])
                    if platform:
                        if event:
                            count = PageInfo.query.filter_by(
                                appversion_id=appversion.id,
                                event=event,
                                platform=platform,
                            ).count()

                            resp = PageInfo.query.filter_by(
                                appversion_id=appversion.id,
                                event=event,
                                platform=platform,
                            ).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                                numPerPage).offset((currentPage - 1) * numPerPage)
                        else:
                            count = PageInfo.query.filter_by(
                                appversion_id=appversion.id,
                                platform=platform,
                            ).count()

                            resp = PageInfo.query.filter_by(
                                appversion_id=appversion.id,
                                platform=platform,
                            ).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                                numPerPage).offset((currentPage - 1) * numPerPage)
                    else:
                        count = PageInfo.query.filter_by(
                            appversion_id=appversion.id,
                        ).count()

                        resp = PageInfo.query.filter_by(
                            appversion_id=appversion.id,
                        ).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                            numPerPage).offset((currentPage - 1) * numPerPage)
                elif not AppVersion and platform:
                    page_type = db.session.query(PageInfo.page).filter_by(platform=platform).group_by(PageInfo.page).all()
                    page_type.sort(key=lambda char: lazy_pinyin(char)[0][0])

                    count = PageInfo.query.filter_by(
                        platform=platform,
                    ).count()

                    resp = PageInfo.query.filter_by(
                        platform=platform,
                    ).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                        numPerPage).offset((currentPage - 1) * numPerPage)

                else:
                    count = PageInfo.query.count()

                    resp = PageInfo.query.order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                        numPerPage).offset((currentPage - 1) * numPerPage)

                    page_type = {}

            else:
                if AppVersion:
                    appversion = Appversion.query.filter_by(app_version=AppVersion).first()
                    page_type = db.session.query(PageInfo.page).filter_by(appversion_id=appversion.id).group_by(PageInfo.page).all()
                    page_type.sort(key=lambda char: lazy_pinyin(char)[0][0])
                    if platform:
                        if event:
                            count = PageInfo.query.filter_by(
                                appversion_id=appversion.id,
                                event=event,
                                platform=platform,
                                page=page,
                            ).count()

                            resp = PageInfo.query.filter_by(
                                appversion_id=appversion.id,
                                event=event,
                                platform=platform,
                                page=page,
                            ).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                                numPerPage).offset((currentPage - 1) * numPerPage)
                        else:
                            count = PageInfo.query.filter_by(
                                appversion_id=appversion.id,
                                platform=platform,
                                page=page,
                            ).count()

                            resp = PageInfo.query.filter_by(
                                appversion_id=appversion.id,
                                platform=platform,
                                page=page,
                            ).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                                numPerPage).offset((currentPage - 1) * numPerPage)
                    else:
                        count = PageInfo.query.filter_by(
                            appversion_id=appversion.id,
                            page=page,
                        ).count()

                        resp = PageInfo.query.filter_by(
                            appversion_id=appversion.id,
                            page=page,
                        ).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                            numPerPage).offset((currentPage - 1) * numPerPage)

                elif not AppVersion and platform:
                    page_type = db.session.query(PageInfo.page).filter_by(platform=platform).group_by(PageInfo.page).all()
                    page_type.sort(key=lambda char: lazy_pinyin(char)[0][0])

                    count = PageInfo.query.filter_by(
                        platform=platform,
                        page=page,
                    ).count()

                    resp = PageInfo.query.filter_by(
                        platform=platform,
                        page=page,
                    ).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                        numPerPage).offset((currentPage - 1) * numPerPage)

                else:
                    count = PageInfo.query.count()

                    resp = PageInfo.query.order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                        numPerPage).offset((currentPage - 1) * numPerPage)

                    page_type = {}

        elif filter_text:
            if not page:
                if AppVersion:
                    appversion = Appversion.query.filter_by(app_version=AppVersion).first()
                    page_type = db.session.query(PageInfo.page).filter_by(appversion_id=appversion.id).group_by(PageInfo.page).all()
                    page_type.sort(key=lambda char: lazy_pinyin(char)[0][0])
                    if platform:
                        if event:
                            count = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.event == event,
                                PageInfo.platform == platform,
                                PageInfo.se_action.like('%%%s%%' % filter_text)
                            )).count()

                            resp = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.event == event,
                                PageInfo.platform == platform,
                                PageInfo.se_action.like('%%%s%%' % filter_text)
                            )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                                numPerPage).offset((currentPage - 1) * numPerPage)
                        else:
                            count = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.platform == platform,
                                PageInfo.se_action.like('%%%s%%' % filter_text),
                            )).count()

                            resp = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.platform == platform,
                                PageInfo.se_action.like('%%%s%%' % filter_text),
                            )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                                numPerPage).offset((currentPage - 1) * numPerPage)
                    else:
                        count = PageInfo.query.filter(and_(
                            PageInfo.appversion_id == appversion.id,
                            PageInfo.se_action.like('%%%s%%' % filter_text),
                        )).count()

                        resp = PageInfo.query.filter(and_(
                            PageInfo.appversion_id == appversion.id,
                            PageInfo.se_action.like('%%%s%%' % filter_text),
                        )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                            numPerPage).offset((currentPage - 1) * numPerPage)
                elif not AppVersion and platform:
                    page_type = db.session.query(PageInfo.page).filter_by(platform=platform).group_by(PageInfo.page).all()
                    page_type.sort(key=lambda char: lazy_pinyin(char)[0][0])

                    count = PageInfo.query.filter(and_(
                        PageInfo.platform == platform,
                        PageInfo.se_action.like('%%%s%%' % filter_text),
                    )).count()

                    resp = PageInfo.query.filter(and_(
                        PageInfo.platform == platform,
                        PageInfo.se_action.like('%%%s%%' % filter_text),
                    )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                        numPerPage).offset((currentPage - 1) * numPerPage)

                else:
                    count = PageInfo.query.filter(and_(
                        PageInfo.se_action.like('%%%s%%' % filter_text)
                    )).count()

                    resp = PageInfo.query.filter(and_(
                        PageInfo.se_action.like('%%%s%%' % filter_text)
                    )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                        numPerPage).offset((currentPage - 1) * numPerPage)

                    page_type = {}

            else:
                if AppVersion:
                    appversion = Appversion.query.filter_by(app_version=AppVersion).first()
                    page_type = db.session.query(PageInfo.page).filter_by(appversion_id=appversion.id).group_by(PageInfo.page).all()
                    page_type.sort(key=lambda char: lazy_pinyin(char)[0][0])
                    if platform:
                        if event:
                            count = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.event == event,
                                PageInfo.platform == platform,
                                PageInfo.se_action.like('%%%s%%' % filter_text),
                                PageInfo.page == page,
                            )).count()

                            resp = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.event == event,
                                PageInfo.platform == platform,
                                PageInfo.se_action.like('%%%s%%' % filter_text),
                                PageInfo.page == page,
                            )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                                numPerPage).offset((currentPage - 1) * numPerPage)
                        else:
                            count = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.platform == platform,
                                PageInfo.se_action.like('%%%s%%' % filter_text),
                                PageInfo.page == page,
                            )).count()

                            resp = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.platform == platform,
                                PageInfo.se_action.like('%%%s%%' % filter_text),
                                PageInfo.page == page,
                            )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                                numPerPage).offset((currentPage - 1) * numPerPage)
                    else:
                        count = PageInfo.query.filter(and_(
                            PageInfo.appversion_id == appversion.id,
                            PageInfo.se_action.like('%%%s%%' % filter_text),
                            PageInfo.page == page,
                        )).count()

                        resp = PageInfo.query.filter(and_(
                            PageInfo.appversion_id == appversion.id,
                            PageInfo.se_action.like('%%%s%%' % filter_text),
                            PageInfo.page == page,
                        )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                            numPerPage).offset((currentPage - 1) * numPerPage)

                elif not AppVersion and platform:
                    page_type = db.session.query(PageInfo.page).filter_by(platform=platform).group_by(PageInfo.page).all()
                    page_type.sort(key=lambda char: lazy_pinyin(char)[0][0])

                    count = PageInfo.query.filter(and_(
                        PageInfo.platform == platform,
                        PageInfo.se_action.like('%%%s%%' % filter_text),
                        PageInfo.page == page,
                    )).count()

                    resp = PageInfo.query.filter(and_(
                        PageInfo.platform == platform,
                        PageInfo.se_action.like('%%%s%%' % filter_text),
                        PageInfo.page == page,
                    )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                        numPerPage).offset((currentPage - 1) * numPerPage)

                else:
                    count = PageInfo.query.filter(and_(
                        PageInfo.se_action.like('%%%s%%' % filter_text)
                    )).count()

                    resp = PageInfo.query.filter(and_(
                        PageInfo.se_action.like('%%%s%%' % filter_text)
                    )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                        numPerPage).offset((currentPage - 1) * numPerPage)
                    page_type = {}

        elif filter_cate:
            if not page:
                if AppVersion:
                    appversion = Appversion.query.filter_by(app_version=AppVersion).first()
                    page_type = db.session.query(PageInfo.page).filter_by(appversion_id=appversion.id).group_by(PageInfo.page).all()
                    page_type.sort(key=lambda char: lazy_pinyin(char)[0][0])
                    if platform:
                        if event:
                            count = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.event == event,
                                PageInfo.platform == platform,
                                PageInfo.se_category.like('%%%s%%' % filter_cate)
                            )).count()

                            resp = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.event == event,
                                PageInfo.platform == platform,
                                PageInfo.se_category.like('%%%s%%' % filter_cate)
                            )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                                numPerPage).offset((currentPage - 1) * numPerPage)
                        else:
                            count = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.platform == platform,
                                PageInfo.se_category.like('%%%s%%' % filter_cate),
                            )).count()

                            resp = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.platform == platform,
                                PageInfo.se_category.like('%%%s%%' % filter_cate),
                            )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                                numPerPage).offset((currentPage - 1) * numPerPage)
                    else:
                        count = PageInfo.query.filter(and_(
                            PageInfo.appversion_id == appversion.id,
                            PageInfo.se_category.like('%%%s%%' % filter_cate),
                        )).count()

                        resp = PageInfo.query.filter(and_(
                            PageInfo.appversion_id == appversion.id,
                            PageInfo.se_category.like('%%%s%%' % filter_cate),
                        )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                            numPerPage).offset((currentPage - 1) * numPerPage)
                elif not AppVersion and platform:
                    page_type = db.session.query(PageInfo.page).filter_by(platform=platform).group_by(PageInfo.page).all()
                    page_type.sort(key=lambda char: lazy_pinyin(char)[0][0])

                    count = PageInfo.query.filter(and_(
                        PageInfo.platform == platform,
                        PageInfo.se_category.like('%%%s%%' % filter_cate),
                    )).count()

                    resp = PageInfo.query.filter(and_(
                        PageInfo.platform == platform,
                        PageInfo.se_category.like('%%%s%%' % filter_cate),
                    )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                        numPerPage).offset((currentPage - 1) * numPerPage)

                else:
                    count = PageInfo.query.filter(and_(
                        PageInfo.se_category.like('%%%s%%' % filter_cate)
                    )).count()

                    resp = PageInfo.query.filter(and_(
                        PageInfo.se_category.like('%%%s%%' % filter_cate)
                    )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                        numPerPage).offset((currentPage - 1) * numPerPage)

                    page_type = {}

            else:
                if AppVersion:
                    appversion = Appversion.query.filter_by(app_version=AppVersion).first()
                    page_type = db.session.query(PageInfo.page).filter_by(appversion_id=appversion.id).group_by(PageInfo.page).all()
                    page_type.sort(key=lambda char: lazy_pinyin(char)[0][0])
                    if platform:
                        if event:
                            count = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.event == event,
                                PageInfo.platform == platform,
                                PageInfo.se_category.like('%%%s%%' % filter_cate),
                                PageInfo.page == page,
                            )).count()

                            resp = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.event == event,
                                PageInfo.platform == platform,
                                PageInfo.se_category.like('%%%s%%' % filter_cate),
                                PageInfo.page == page,
                            )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                                numPerPage).offset((currentPage - 1) * numPerPage)
                        else:
                            count = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.platform == platform,
                                PageInfo.se_category.like('%%%s%%' % filter_cate),
                                PageInfo.page == page,
                            )).count()

                            resp = PageInfo.query.filter(and_(
                                PageInfo.appversion_id == appversion.id,
                                PageInfo.platform == platform,
                                PageInfo.se_category.like('%%%s%%' % filter_cate),
                                PageInfo.page == page,
                            )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                                numPerPage).offset((currentPage - 1) * numPerPage)
                    else:
                        count = PageInfo.query.filter(and_(
                            PageInfo.appversion_id == appversion.id,
                            PageInfo.se_category.like('%%%s%%' % filter_cate),
                            PageInfo.page == page,
                        )).count()

                        resp = PageInfo.query.filter(and_(
                            PageInfo.appversion_id == appversion.id,
                            PageInfo.se_category.like('%%%s%%' % filter_cate),
                            PageInfo.page == page,
                        )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                            numPerPage).offset((currentPage - 1) * numPerPage)

                elif not AppVersion and platform:
                    page_type = db.session.query(PageInfo.page).filter_by(platform=platform).group_by(PageInfo.page).all()
                    page_type.sort(key=lambda char: lazy_pinyin(char)[0][0])

                    count = PageInfo.query.filter(and_(
                        PageInfo.platform == platform,
                        PageInfo.se_category.like('%%%s%%' % filter_cate),
                        PageInfo.page == page,
                    )).count()

                    resp = PageInfo.query.filter(and_(
                        PageInfo.platform == platform,
                        PageInfo.se_category.like('%%%s%%' % filter_cate),
                        PageInfo.page == page,
                    )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                        numPerPage).offset((currentPage - 1) * numPerPage)

                else:
                    count = PageInfo.query.filter(and_(
                        PageInfo.se_category.like('%%%s%%' % filter_cate)
                    )).count()

                    resp = PageInfo.query.filter(and_(
                        PageInfo.se_category.like('%%%s%%' % filter_cate)
                    )).order_by(PageInfo.page_key, PageInfo.sub_type).limit(
                        numPerPage).offset((currentPage - 1) * numPerPage)
                    page_type = {}

        Datainfo = {
            'resp': [i.serialize for i in resp],
            'count': count,
            'page_type': page_type,
        }

        return jsonify(Datainfo)


@app.route('/api/v1/add_version', methods=['POST', 'GET'])
@api_auth
def add_version():
    if request.method == 'POST':
        Data = json.loads(request.data)
        last_version = Appversion.query.order_by('id desc').first()

        new_appver = Appversion(appversion=Data['appversion'])
        log_for_appversion = PageInfo(appversion=new_appver)
        log_record = log(Data['username'], Data['time'], Data['logtype'], '', Data['appversion'], log_for_appversion)
        db.session.add(new_appver)
        db.session.add(log_record)
        db.session.commit()
        db.session.delete(log_for_appversion)
        db.session.commit()

        for data in last_version.pageinfo:
            data_insert = PageInfo(data.page, data.event, data.object, new_appver,
                                   data.type, data.sub_type, data.se_category,
                                   data.se_action, data.note, data.platform,
                                   data.pm, data.page_key)
            db.session.add(data_insert)
        db.session.commit()

        return '1'


@app.route('/api/v1/login', methods=['POST', 'GET'])
def check_passwd():
    if request.method == 'POST':
        data = json.loads(request.data)
        username = data['username']
        passwd = data['password']
        check_from_db = user.query.filter_by(username=username, password=passwd).first()
        if check_from_db:
            result = {
                'status': 1,
                'role': check_from_db.role
            }
            session['is_login'] = True
            session['user'] = username
            session['role'] = check_from_db.role
        else:
            result = {
                'status': -1,
            }
        return jsonify(result)


# 用户刷新或者切换页面时的监听函数
@app.route('/api/v1/status')
def check_status():
    if session.get('is_login'):
        if session['is_login']:
            return jsonify({
                'is_login': True,
                'username': session['user'],
                'role': session['role']
            })
    else:
        return jsonify({
            'is_login': False
        })


# 用户退出登录函数
@app.route('/api/v1/logout')
@api_auth
def logout():
    session.pop('is_login', None)
    session.pop('user', None)
    session.pop('role', None)
    return jsonify({
        'result': True
    })


# 像数据库插入log记录
@app.route('/api/v1/log_server/<logtype>', methods=['POST', 'GET'])
@api_auth
def LogService(logtype):
    Data = json.loads(request.data)
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        if logtype == 'AddVersion':
            pass
        elif logtype == 'Edit':
            pass
        elif logtype == 'AddData':
            pass
        elif logtype == 'Delete':
            delete_info = PageInfo.query.filter_by(id=Data['id']).first()
            log_delele_forginekey = PageInfo(appversion=PageInfo.query.filter_by(id=Data['id']).first().appversion)
            log_record = log(Data['username'], Data['time'], Data['logtype'],
                             delete_info.tounicode, '', log_delele_forginekey)
            db.session.add(log_record)
            db.session.commit()
            db.session.delete(log_delele_forginekey)
            db.session.commit()
        return '1'


# 查询当前页下的改动记录
@app.route('/api/v1/log_server/check_for_current_page', methods=['POST', 'GET'])
@api_auth
def check_for_current_page():
    if request.method == 'POST':
        loginfo = []
        Data = json.loads(request.data)
        for oid in Data['oid']:
            result = PageInfo.query.filter_by(id=oid).first()

            if result:
                for i in result.log:
                    if i.type == u'编辑单条数据':
                        loginfo.append(i.serialize)

        resp = {
            'loginfo': loginfo,
        }
        return jsonify(resp)


# 读取log每页的数据
@app.route('/api/v1/log_server/<pagenumber>/<numPerPage>', methods=['POST', 'GET'])
@api_auth
def get_loginfo_by_page(pagenumber, numPerPage):
    if request.method == 'GET':
        count = log.query.count()
        resp = log.query.order_by('time desc').limit(
            int(numPerPage)).offset((int(pagenumber) - 1) * int(numPerPage))
        result = {
            'resp': [i.serialize for i in resp],
            'count': count,
        }
        return jsonify(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6234, debug=True)
