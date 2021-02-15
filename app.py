import os
import pymysql
from flask import Flask
import traceback
from flask import Flask, render_template, redirect, request, url_for, flash, session
from functools import wraps

# 创建连接
#conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', port=3306,
                       #db='bookrecommend')
# 创建游标
#cur = conn.cursor()

users = [
    {
        'username': 'root',
        'password': 'root'
    },
    {
        'username': 'wy',
        'password': '123456'
    }
]

app = Flask(__name__)
# 设置secret值，保护信息不被泄露
app.config['SECRET_KEY'] = 'aasswde'


def is_login(f):
    """用来判断用户是否登录成功"""

    # 保证函数在加了装饰器之后返回的不是wrapper函数名，而是原函数名
    @wraps(f)
    def wrapper(*args, **kwargs):
        # 判断session对象中是否有seesion['user'],
        # 如果包含信息， 则登录成功， 可以访问主页；
        # 如果不包含信息， 则未登录成功， 跳转到登录界面;
        #user_info = request.form.to_dict()
        #print(user_info.get('identype'))
        #if user_info.get('identype') == 'student':
        if session.get('user', None):
            return f(*args, **kwargs)
        else:
            flash('用户必须登陆才能访问%s' % f.__name__)
        return redirect(url_for('login'))

    return wrapper


def is_admin(f):
    """用来判断管理员是否登录成功"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        # 判断session对象中是否有seesion['user']等于root,
        # 如果包含信息， 则登录成功， 可以访问主页；
        # 如果不包含信息， 则未登录成功， 跳转到登录界面;；
        #user_info = request.form.to_dict()
        #print(user_info.get('identype'))
        #if user_info.get('identype') == 'admin':
        if session.get('user', None) == 'root':
            return f(*args, **kwargs)
        else:
            flash('只有管理员root才能访问%s' % f.__name__)
            return redirect(url_for('login'))

    return wrapper


@app.route('/')
@is_login
def user():
    return render_template('index.html')

@app.route('/')
@is_admin
def index():
    return render_template('index.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        # 当所有的信息遍历结束， 都没有发现注册的用户存在， 则将注册的用户添加到服务器， 并跳转登录界面;
        for user in users:
            if user['username'] == username:
                return render_template('register.html', messages='用户%s已经存在' % username)
        else:
            users.append(dict(username=username, password=password))
            # 出现一个闪现信息;
            flash('用户%s已经注册成功，请登陆.....' % username, category='info')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        for user in users:
            if user['username'] == username and user['password'] == password:
                #  将用户登录的信息存储到session中;
                session['user'] = username
                return redirect(url_for('user'))
            if user['username'] == username and user['password'] != password:
                # 出现一个闪现信息;
                flash('%s用户密码错误，请重新登陆....' % (username))
                return redirect(url_for('login'))
        else:
            flash('没有%s用户，请重新登陆...' % username)
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/list/')
@is_admin
@is_login
def list():
    return render_template('list.html', users=users)


@app.route('/logout/')
def logout():
    #  将用户存储到session中的信息删除;
    session.pop('user')
    flash('注销成功....')
    return render_template('login.html')


@app.route('/delete/<string:username>/')
def delete(username):
    for user in users:
        # 用户存在， 则删除;
        if username == user['username']:
            users.remove(user)
            flash('删除%s用户成功' % username)
    # else:
    #     flash('用户%s不存在'%username)

    # 删除成功， 跳转到/list/路由中.....
    return redirect(url_for('list'))


@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # 获取用户上传的文件对象,html中定义的对象名
        f = request.files['Imgobj']

        # 获取上传文件的文件名
        # print(f.filename)

        # 获取当前项目的目录位置;
        basepath = os.path.dirname(__file__)
        # 两种查询的区别
        # -查询到文件名
        # print(__file__)       # /root/PycharmProjects/day34/app.py
        # -查询到文件所在目录
        # print(basepath)       # /root/PycharmProjects/day34

        # 拼接路径， 保存到本地的位置;
        filepath=os.path.join(basepath,'static','img',f.filename)

        # 保存文件
        f.save(filepath)
        flash('上传文件%s成功'%f.filename)
        return redirect(url_for('upload'))
    else:
        return render_template('upload.html')


if __name__ == '__main__':
    app.run()

