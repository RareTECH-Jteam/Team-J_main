from flask import json
from Models.Reaction import Reactions
from extensions import socketio
from util.DB import DB
db_pool = DB.init_db_pool()

class reaction_services:
    @classmethod
    def send_reaction(cls, post_id, user_id,emoji_native):
         
        conn = db_pool.get_conn() # タイムアウト対策
        conn.ping(reconnect=True) #生存確認の一文(切れてたらreconnect)
        
        # 投稿されたリアクションがテーブルにあるか確認
        is_already = Reactions.is_already_reaction(conn, post_id, user_id)
        should_insert = True

        try:
            if is_already: #すでに押した(リアクション済み)の場合
                    Reactions.delete_reaction(conn, post_id, user_id) # 既にあるものをもう一度押した→取り消しの処理

                    if is_already['emoji_type'] == emoji_native: # 過去に押したものと同じなら
                        should_insert = False # 登録はしない
            if should_insert:
                    Reactions.insert_reaction(conn, post_id, user_id, emoji_native) # 新しくリアクションを登録する

            conn.commit() # 全部うまくいったらコミット
            
            # 現在の最新のリアクション情報を再取得してフロントに返す
            reactions = []
            current_reactions_info = Reactions.get_reactions_by_id(post_id)

            # JSONで返却するために形を整える
            for reaction in current_reactions_info:
                reactions.append({
                    'emoji': reaction['emoji_type'],
                    'count': reaction['count']
                })

            # jsonでお返し
            return reactions
           
        except Exception as e: # もし失敗したら
            import traceback
            traceback.print_exc()
            conn.rollback()
            raise e
        
        finally:
            db_pool.release(conn)        