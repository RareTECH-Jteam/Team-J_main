# 【重要】サーバーが「一度にたくさんの仕事」を並行してこなせるようにする魔法の設定
# これがないと、1人の処理中に他の人の通信が止まって（ロックして）しまいます
from gevent import monkey
monkey.patch_all()

from flask import Flask, request, redirect, render_template, session, url_for
from flask_socketio import join_room,emit
from extensions import socketio
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from routes.auth import auth
from routes.posts import posts
from routes.baton import baton
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

# リアルタイム通知
socketio.init_app(app)

# -- ルーティング登録 --
# 認証系（ログイン・ログアウト・登録）
app.register_blueprint(auth)

# 投稿系（投稿一覧・作成・削除）
app.register_blueprint(posts)

#バトン系
app.register_blueprint(baton)

# ルートページのリダイレクト処理
@app.route('/', methods=['GET'])
def index():
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))

    # 投稿一覧ページ    
    return redirect(url_for('posts.mypage_view'))


# クライアントが接続したとき、ユーザーIDのroomに参加する
@socketio.on('connect')
def on_connect():
    if not SM.is_live_session():
        return    
    user_id = SM.get_user_id()
    join_room(str(user_id))

    # クライアントにお知らせを投げ返す
    emit('notification'
        , {'message': 'バトンが渡されました！\r\n確認してみよう！'}
        , room=str(user_id))    


# クライアントから「未読確認（check_unread）」がリクエストされた場合
# @socketio.on('check_unread')
# def check_unread():
#     # 下記テスト用 最終的にはBatonのbatonappを見て、自分に届いたバトンで未通知のものを取得するようにする
    
#     """
#     クライアントからの未読確認リクエストを処理
#     1. セッションから現在のユーザーIDを取得
#     2. 対象ユーザー専用のルーム（Room）に対して通知を送信
#     """

#     # ログイン中のユーザーIDを取得
#     user_id = SM.get_user_id()
    
#     # クライアントにお知らせを投げ返す
#     socketio.emit('notification'
#                   , {'message': 'バトンが渡されました！\r\n確認してみよう！'}
#                   , room=str(user_id))


# -- 通知が届いた場合、Batonを通知済みにする --
# @socketio.on('notification_received')
# def notification_received(data):
#     baton_idが本当にユーザーIDのものなのか、チェックすること
#     baton_id = data.get('batonid')
#     if baton_id:
        # Baton.mark_as_read(data['batonid'])




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
    # app.run(host="0.0.0.0", debug=True)
     socketio.run(app, host="0.0.0.0", debug=True)
