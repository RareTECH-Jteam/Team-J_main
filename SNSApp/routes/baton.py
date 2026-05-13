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
    
    user_id = SM.get_user_id() #自分のIDを入手
    Baton.update_expired_status() #バトンの期限切れチェック

    tasks = Task.get_all() #Taskの内容をすべて拾ってくる
    incomplete_baton = Baton.get_by_incomplete_baton(user_id) #未完了バトンの確認
    history_tasks = Baton.get_completed_and_failed(user_id) #過去の履歴確認

    #history_tasksの箱からstatusが1なら成功、2なら失敗のリストを作成する
    complete_tasks = [t for t in history_tasks if t['status'] ==1]
    fail_tasks = [t for t in history_tasks if t['status'] ==2]

    if incomplete_baton: #未完了課題があれば
        incomplete_baton['formatted_date'] = incomplete_baton['created_at'].strftime('%Y-%m-%d %H:%M') #日付作成

    return render_template(
        'post/baton_detail.html',
        tasks=tasks, #HTMLの{task.content}にぶち込む
        baton_incomplete=incomplete_baton, #HTMLの{% if baton %}をTrueにする
        complete_tasks=complete_tasks, #成功バトン履歴
        fail_tasks=fail_tasks #失敗バトン履歴
    )   



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