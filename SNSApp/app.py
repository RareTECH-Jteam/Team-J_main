from flask import Flask, request, redirect, render_template, session, url_for
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from routes.auth import auth
from routes.posts import posts
from util.SessionManager import SessionManager as SM
import uuid
import os

# 定数定義
SESSION_DAYS = 30

app = Flask(__name__)

# アプリのシークレットキー
app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)

# セッションの有効期限を設定
app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)

# CSRF対策
csrf = CSRFProtect(app)

# -- ルーティング登録 --
# 認証系（ログイン・ログアウト・登録）
app.register_blueprint(auth)

# 投稿系（投稿一覧・作成・削除）
app.register_blueprint(posts)

# ルートページのリダイレクト処理
@app.route('/', methods=['GET'])
def index():
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))

    # 投稿一覧ページ    
    return redirect(url_for('posts.posts_view'))

@app.errorhandler(400)
def bad_request(error):
    return render_template('error/400.html'), 400

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'),404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error/500.html'),500

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
