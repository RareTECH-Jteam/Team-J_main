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

    if tasks: #課題があれば
        current_task = tasks[0] #最新の課題(taskの0番目)を引き出す

        return render_template(
            'post/baton_detail.html',
            task = current_task, #HTMLの{task.content}にぶち込む
            tasks = tasks,
            baton=True, #HTMLの{% if baton %}をTrueにする
            task_id=current_task['id'], #完了ボタンのID
            sender_name="TestA", #一旦送り主をTestAと置きます… カミングスーン
            created_at=current_task['created_at'] #届いた時間を入れる
        )
    else: #課題がないなら
        return render_template('post/baton_detail.html',baton=False)


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
    Baton.create(sender_id, receiver_id, task_id,)
    return '', 204  # 何も返さない（画面遷移なし）