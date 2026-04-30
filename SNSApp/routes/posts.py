from flask import Blueprint, session, redirect, url_for,render_template, flash , abort , request
from Models.User import User
from Models.Post import Post
from Models.Comment import Comment
from util.SessionManager import SessionManager as SM

posts = Blueprint('posts', __name__)

# 投稿一覧ページの表示
@posts.route('/posts', methods=['GET'])
def posts_view():
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))

    # ユーザーID設定
    user_id = SM.get_user_id()

    all_posts = Post.get_all()
    for post in all_posts:
        post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M')
        post['user_name'] = User.get_name_by_id(post['user_id'])

    return render_template('post/posts.html', posts=all_posts, user_id=user_id)


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
    if content == '':
        flash('投稿内容が空です','error')
        return redirect(url_for('posts.posts_view'))
    
    # 投稿情報作成
    Post.create(user_id, content)
    flash('投稿が完了しました','success')
    return redirect(url_for('posts.posts_view'))


# 投稿削除処理
@posts.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
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

    # 自分以外の投稿を削除しようとした場合
    if post['user_id'] != user_id:
        flash('この投稿を削除することはできません', 'error')
        return redirect(url_for('posts.posts_view'))

    # 投稿削除
    Post.delete(post_id)
    flash('投稿が削除されました','success')
    return redirect(url_for('posts.posts_view'))


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

    # 投稿に対するコメント取得
    comments = Comment.get_by_post_id(post_id)
    for comment in comments:
        comment['created_at'] = comment['created_at'].strftime('%Y-%m-%d %H:%M')
        comment['user_name'] = User.get_name_by_id(comment['user_id'])

    return render_template('post/post_detail.html', post=post, comments = comments, user_id=user_id)


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

