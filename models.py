from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 定義使用者模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False,)
    password = db.Column(db.String(120), nullable=False)
    game_data = db.Column(db.Text, nullable=True)  # 儲存遊戲數據

    def __repr__(self):
        return f'<User {self.username}>'
