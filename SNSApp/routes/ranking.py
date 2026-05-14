from flask import Blueprint, redirect, url_for,render_template
from Models.User import User
from Models.Post import Post
from Models.Comment import Comment
from util.SessionManager import SessionManager as SM

ranking = Blueprint('ranking', __name__)

@ranking.route('/ranking', methods=['GET'])
def ranking_view():
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))
    
    return render_template('ranking/ranking.html') # ランキングの画面を見る       

