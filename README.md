## 增加新用户指引

1. cd 到datawebunit文件夹下
2. 利用ipython 导入`from app import db, user`
3. 实例化user对象,user对象的__init__()函数如下:

    ```python
    def __init__(self, username='', password='', role=''):
            self.username = username
            self.password = password
            self.role = role
    
    ```
    如 `user1 = user('jiangweiwei', 'jiangweiwei', 'editor')`
    三个参数分别对应于 用户名  密码  用户角色
    用户角色请设置为  admin   editor  anonymous 中的一个

4. 将对象加入到db会话中,并提交

    ```python
    db.session.add(user1)
    db.session.commit()
    ```


