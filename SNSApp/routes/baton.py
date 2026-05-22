from flask import Blueprint, session, redirect, url_for,render_template, flash , abort , request, jsonify
from Models.Baton import Baton
from Models.Task import Task #Models/Taskから「Task」と名の付くクラスを引っ張ってくる
from Models.Chain import Chain
from util.SessionManager import SessionManager as SM
from services.baton_services import baton_services

baton = Blueprint('baton', __name__)

@baton.route('/baton', methods=['GET'])
def baton_view():
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))
    
    user_id = SM.get_user_id() #自分のIDを入手

    tasks = Task.get_all() #Taskの内容をすべて拾ってくる
    incomplete_baton = Baton.get_by_incomplete_baton(user_id) #未完了バトンの確認
    history_tasks = Baton.get_completed_and_failed(user_id) #過去の履歴確認
    total_completed_count = Baton.get_total_completed_count(user_id) # バトンの総完了数取得


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
        fail_tasks=fail_tasks, #失敗バトン履歴
        page_id ="baton",
        total_completed_count=total_completed_count # バトン総完了数
    )


#バトン送信
@baton.route('/baton/send', methods=['POST'])
def baton_send():
    if not SM.is_live_session():
        return redirect(url_for('auth.login_view'))
    
    sender_id = SM.get_user_id()

    task_id = request.form.get('select-task')

    errors = Task.validate(task_id)

    # エラー時
    if errors:
        return jsonify({'message': 'error', 'text': errors}), 400    
        
    #task_idからcontent取得
    task = Task.find_by_id(task_id) 
    content = task['content']
    
    # 共通の箱を作る
    baton_data = {}
    baton_id = request.form.get('baton_id')

    # 自分のバトンがあるかチェック
    my_baton = Baton.get_by_incomplete_baton(sender_id)

    # バトンが渡された場合
    if my_baton:
        # バトン情報を取得
        # current_baton = Baton.find_by_id(my_baton['id'])
        
        baton_data['baton_id'] = my_baton['id']
        baton_data['baton_title'] = my_baton['baton_title']
        baton_data['sender_id'] = sender_id
        baton_data['chain_id'] = my_baton['chain_id']
        baton_data['relay_count'] = int(my_baton['relay_count']) + 1
        baton_data['task_id'] = task_id
        baton_data['content'] = content

        try:
            baton_services.process_baton_relay(sender_id,baton_data)
        except Exception as e:
            return {'message': 'error', 'text': str(e)}, 500         
         
        return {'message': 'success','text': '成功'}, 200   

    # 新規
    chain_id = Chain.create()

    # タイトル取得
    baton_title = request.form.get('task_title')

    errors = Baton.validate(baton_title)

    if errors:
        return {'message': 'error', 'text': errors}, 400    
    
    # バトンタイトル重複チェック
    existing_baton = Baton.find_by_title(baton_title) # 入力されたタイトルをModelの関数に渡す
    if existing_baton: # もしタイトルが既にあったら
        return {"message" : "error","text":["そのタイトルは使われています"]},400 # 400エラーを返す


    baton_data['baton_id'] = None
    baton_data['baton_title'] = baton_title
    baton_data['sender_id'] = sender_id
    baton_data['chain_id'] = chain_id
    baton_data['relay_count'] = 1
    baton_data['task_id'] = task_id
    baton_data['content'] = content

    print(f"baton_data: {baton_data}")

    try:
        baton_services.process_baton_relay(sender_id,baton_data)
    except Exception as e:
        return {'message': 'error', 'text': str(e)}, 500 

    return {'message': 'success','text': '成功'}, 200   
