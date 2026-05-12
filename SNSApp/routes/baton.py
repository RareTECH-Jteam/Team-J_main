from flask import Blueprint, session, redirect, url_for,render_template, flash , abort , request
from Models.User import User
from Models.Post import Post
from Models.Comment import Comment
from Models.Baton import Baton
from Models.Task import Task #Models/Taskから「Task」と名の付くクラスを引っ張ってくる
from util.SessionManager import SessionManager as SM
import random

baton = Blueprint('baton', __name__)

@baton.route('/baton', methods=['GET'])
def baton_view():
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))
    
    tasks = Task.get_all() #Taskの内容をすべて拾ってくる
    my_user_id = session.get('user_id') #今ログインしているIDを取得
    incomplete_baton = Baton.get_by_incomplete_baton(my_user_id) #未完了バトンの確認

    if incomplete_baton: #未完了課題があれば
        current_task = incomplete_baton[0] #新しい未完バトンを引き出す

        return render_template(
            'post/baton_detail.html',
            task = current_task, #HTMLの{task.content}にぶち込む
            tasks = tasks,
            baton=current_task, #HTMLの{% if baton %}をTrueにする
            task_id=current_task['task_id'], #完了ボタンのID
            sender_name=current_task['sender_name'], #sender_nameの取得
            created_at=current_task['created_at']  #.strftime('%Y-%m-%d %H:%M') #届いた時間を入れる
        )
    else: #課題がないなら
        return render_template('post/baton_detail.html',baton=False,tasks=tasks)


#バトン送信
@baton.route('/baton/send', methods=['POST'])
def baton_send():
    if not SM.is_live_session():
        return redirect(url_for('auth.login_view'))
    
    sender_id = SM.get_user_id()
    task_id = request.form.get('task_id')

    #自分以外のユーザID取得
    users = Baton.get_receiver(sender_id)

    if not users:
        flash('バトンの送り先がありません。')
        return '', 204  # 何も返さない（画面遷移なし）
    
    #ランダムに１人を選択
    receiver = random.choice(users)
    receiver_id = receiver['id']

    #バトン作成
    baton_id = Baton.create(sender_id, receiver_id, task_id,)
    return '', 204  # 何も返さない（画面遷移なし）