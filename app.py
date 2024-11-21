import os
from flask import Flask, render_template
from user import user_routes
from game import game_routes
from models import db


app = Flask(__name__)

# 設定資料庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.secret_key = os.urandom(24)
# 建立資料庫
with app.app_context():
    db.create_all()

# 註冊藍圖
app.register_blueprint(user_routes)
app.register_blueprint(game_routes)

# 主頁面
@app.route('/')
def index():
    return render_template('home.html')  # 可以自定義一個首頁

if __name__ == '__main__':
    app.run(debug=True)
