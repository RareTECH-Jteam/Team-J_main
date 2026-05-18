import json
from flask import Blueprint, session, redirect, url_for,render_template, flash , abort , request
from Models.User import User
from Models.Post import Post
from Models.Comment import Comment
from Models.Reaction import Reactions
from util.SessionManager import SessionManager as SM
from services.reaction_services import reaction_services

posts = Blueprint('posts', __name__)

# 投稿一覧ページの表示
@posts.route('/posts', methods=['GET'])
def mypage_view():
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))

    # ユーザーID設定
    user_id = SM.get_user_id()

    # ユーザー名取得
    username = User.get_name_by_id(user_id)

    # 総勉強時間取得
    total_study_time = Post.get_total_study_time(user_id)

    total_hours = total_study_time['hours'] or 0
    total_minutes = total_study_time['minutes'] or 0

    # 投稿一覧
    all_posts = Post.get_all()
    for post in all_posts:
        post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M')
        post['user_name'] = User.get_name_by_id(post['user_id'])
        study_time = Post. time_to_minutes(post['study_time'])
        post['hours'] =   study_time // 60
        post['minutes'] = study_time % 60

        # post_time = post['study_time'].total_seconds() # 入力された勉強時間を秒数にする
        # post_hours = int(post_time // 3600) #時間に直す
        # post_minutes = int((post_time % 3600) // 60) #余ったものを分にする
        # post['hours'] = post_hours # hoursに時間を
        # post['minutes'] = post_minutes # minutesに分を

    return render_template('post/mypage.html',
                            user_name=username, 
                            total_hours=total_hours,
                            total_minutes=total_minutes,
                            posts=all_posts
    )       


# 投稿処理
@posts.route('/posts', methods=['POST'])
def create_post():
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))

    # ユーザーID設定
    user_id = SM.get_user_id()
    
    #投稿内容取得 
    content = request.form.get('content', '').strip()
    
    # 投稿内容が空の場合
    errors = Post.validate_content(content)
    if errors:
        flash(errors,'error')
        return redirect(url_for('posts.mypage_view'))
    
    #勉強時間取得
    req_study_time = request.form.get('study_time','')

    # 勉強時間が不正の場合
    errors = Post.validate_minutes(req_study_time)
    if errors:
        flash(errors,'error')   
        return redirect(url_for('posts.mypage_view'))
    
    study_time = Post.minutes_to_time(req_study_time)

    # 投稿情報作成
    Post.create(user_id, content, study_time)
    flash('投稿が完了しました','success')
    return redirect(url_for('posts.mypage_view'))


# 投稿編集機能
@posts.route('/posts/<int:post_id>/update', methods=['POST'])
def update_post(post_id):
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))

    # JSON取得
    data = request.get_json()
    print(data) 
    # 投稿内容
    content = data.get('content', '')
    
    # 投稿内容が空の場合
    errors = Post.validate_content(content)
    if errors:        
        # JSにレスポンス
        return {'message': 'error', 'text': errors}, 400

    # 勉強時間
    minutes = data.get('study_time', '')
    print(minutes);
    # 勉強時間が不正の場合
    errors = Post.validate_minutes(minutes)
    if errors:
        # flash(errors,'error')
        # JSにレスポンス
        return {'message': 'error', 'text': errors}, 400
   
    # 分をTIME型の書式に合わせる
    study_time = Post.minutes_to_time(minutes)
    
    # 編集 
    try:
        Post.update(post_id,content,study_time)
    except Exception:
        return {'message': 'error', 'text': '編集に失敗しました'}, 500
        
    return {'message' : 'success'} , 200


# 投稿削除処理
@posts.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))
    
    # ユーザーID設定
    user_id = SM.get_user_id()

    # 投稿内容取得
    post = Post.find_by_id(post_id)
    
    # 該当の投稿が無い場合
    if post is None:
        abort(404)

    # 自分以外の投稿を削除しようとした場合
    if post['user_id'] != user_id:
        return {'message': 'error', 'text': 'この投稿を削除することはできません'}, 400

    # 投稿削除
    try:
        Post.delete(post_id)
    except Exception:
        return {'message': 'error', 'text': '削除に失敗しました'}, 500
    
    flash('投稿が削除されました', 'success')
    
    # JS側にレスポンス
    return {'message': 'success'}, 200


# 投稿詳細ページの表示
@posts.route('/posts/<int:post_id>', methods=['GET'])
def post_detail_view(post_id):
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))

    user_id = SM.get_user_id()
    
    # 投稿内容取得
    post = Post.find_by_id(post_id)

    # 該当の投稿が無い場合
    if post is None:
        abort(404)
    
    post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M')
    post['user_name'] = User.get_name_by_id(post['user_id'])

    #分に換算
    study_minutes =  Post.time_to_minutes(post['study_time']) 
    hours = study_minutes // 60
    minutes = study_minutes % 60

    # 投稿に対するコメント取得
    comments = Comment.get_by_post_id(post_id)
    for comment in comments:
        comment['created_at'] = comment['created_at'].strftime('%Y-%m-%d %H:%M')
        comment['user_name'] = User.get_name_by_id(comment['user_id'])

    # リアクションの取得
    reactions = []
    
    try :
        current_reactions_info = Reactions.get_reactions_by_id(post_id)

        # 整形
        for reaction in current_reactions_info:
            reactions.append({
                'emoji': reaction['emoji_type'],  # emoji_type
                'count': reaction['count'] ,  # count
                'users':reaction['name'].split(',') # user.name
            })
    except Exception as e:
        abort(500)

    # jsonという文字列にする
    reactions_json = json.dumps(reactions, ensure_ascii=False)

    return render_template('post/post_detail.html'
                        , post=post
                        , comments=comments
                        , user_id=user_id
                        , hours=hours
                        , minutes=minutes
                        , reactions=reactions_json) # jsonで渡す形に変更


# コメント処理
@posts.route('/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))

    user_id = SM.get_user_id()
    
    # コメント内容取得
    content = request.form.get('content', '').strip()
    
    # コメントが空の場合
    if content == '':
        flash('コメント内容が空です','error')
        return redirect(url_for('posts.post_detail_view', post_id=post_id))
    
    # コメント情報作成
    Comment.create(user_id, post_id, content)
    flash('コメントの投稿が完了しました','success')
    return redirect(url_for('posts.post_detail_view', post_id=post_id))

#リアクション登録・削除
@posts.route('/posts/<int:post_id>/reactions', methods=['POST'])
def reaction_post(post_id):

    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))
    
    # ユーザーID設定
    user_id = SM.get_user_id()

    # JSONデータ取得
    data = request.get_json()
    emoji_native = data['emoji']

    #空っぽチェック
    errors = Reactions.validate(emoji_native)
    if errors:
        return{'message':'error','text':errors},400 # 絵文字が空っぽの場合は400エラーを出して終わり
    
    try:
        # jsonでお返し
        reactions = reaction_services.send_reaction(post_id, user_id, emoji_native)

        return {'message': 'success', 'reactions': reactions}, 200 # 成功時は200で返す

    except Exception as e: # もし失敗したら
        return{'message':'error','text':str(e)},500 # 500エラーを返す