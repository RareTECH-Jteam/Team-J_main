from flask import Blueprint, session, redirect, url_for,render_template, flash , abort , request
from Models.User import User
from Models.Post import Post
from Models.Comment import Comment
from Models.Baton import Baton
from util.SessionManager import SessionManager as SM

baton = Blueprint('baton', __name__)

@baton.route('/baton', methods=['GET'])
def baton_view():
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))
    return render_template('post/baton_detail.html')