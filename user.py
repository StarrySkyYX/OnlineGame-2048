from flask import Blueprint, Flask, jsonify, request, render_template, redirect, session, url_for, flash
from models import db, User

user_routes = Blueprint('user', __name__,url_prefix='/user')


@user_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required!')
            return redirect(url_for('user.register'))

        # 檢查使用者是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('User already exists!')
            return redirect(url_for('user.register'))

        # 新增使用者
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully!')
        return redirect(url_for('user.login'))

    return render_template('register.html')

# 使用者登入功能
@user_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required!')
            return redirect(url_for('user.login'))

        # 檢查使用者是否存在
        user = User.query.filter_by(username=username).first()
        if not user or user.password != password:
            flash('Invalid username or password!')
            return redirect(url_for('user.login'))
        
        session['user_id'] = user.id  # 儲存用戶ID到session
        return redirect(url_for('game.index'))  # 重定向到遊戲頁面
        
    return render_template('login.html')


# 使用者登出功能
@user_routes.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    user_routes.run(debug=True)
