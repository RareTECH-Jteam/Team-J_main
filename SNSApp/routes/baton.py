from flask import Blueprint, session, redirect, url_for,render_template, flash , abort , request
from Models.User import User
from Models.Post import Post
from Models.Comment import Comment
from Models.Baton import Baton
from util.SessionManager import SessionManager as SM
import random

baton = Blueprint('baton', __name__)

@baton.route('/baton', methods=['GET'])
#バトンページにGO
def baton_view():
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))
    return render_template('post/baton_detail.html')

#バトン送信
@baton.route('/baton/send', methods=['POST'])
def baton_send():
    if not SM.is_live_session():
        return redirect(url_for('auth.login_view'))
    
    sender_id = SM.get_user_id()
    task_id = request.form.get('task_id')
    content = request.form.get('content')

    #自分以外のユーザID取得
    users = Baton.get_receiver(sender_id)

    if not users:
        flash('バトンの送り先がありません。')
        #return redirect(url_for('baton.baton_view'))
    
    #ランダムに１人を選択
    receiver = random.choice(users)
    receiver_id = receiver['id']

    #バトン作成
    Baton.create(sender_id, receiver_id, task_id, content)
    return redirect(url_for('baton.baton_view'))
