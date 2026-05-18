from flask import Blueprint, redirect, url_for,render_template
from datetime import datetime
from Models.User import User
from Models.Post import Post
from Models.Comment import Comment
from Models.Baton import Baton
from util.SessionManager import SessionManager as SM

ranking = Blueprint('ranking', __name__)

@ranking.route('/ranking', methods=['GET'])
def ranking_view():
    # セッションが無効の場合
    if not SM.is_live_session():
        # ログインページ表示
        return redirect(url_for('auth.login_view'))
    
    user_id = SM.get_user_id() #ログイン者のID取得
    study_ranking = Post.get_study_ranking() #総勉強時間の取得
    baton_chain_ranking = Baton.get_chain_ranking() #バトンチェーンの取得
    current_month = datetime.now().month

    return render_template('ranking/ranking.html',
                           user_id = user_id, 
                           study_ranking = study_ranking,
                           month = current_month,
                           baton_chain_ranking = baton_chain_ranking) # ランキングの画面を見る       
                           
