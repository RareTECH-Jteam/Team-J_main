from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

class Reactions: #リアクションクラス    
    @classmethod # リアクション機能のメイン
    def get_reactions_by_id(cls, post_id): #clsには自分のクラス名が入る
        conn = db_pool.get_conn() # MySQLからコネクションを持ってくる
        conn.ping(reconnect=True) # 接続切れてないか確認
        try: # try文 この領域内でエラーをかましたらexceptに移動
            with conn.cursor(pymysql.cursors.DictCursor) as cur: # DBからのデータを自動的に辞書型に変えてくれる
                sql = """
                    SELECT emoji_type, COUNT(*) as count 
                    FROM post_reactions 
                    WHERE post_id = %s
                    GROUP BY emoji_type
                """                                 # SQL文 「post_reactionsテーブルから、指定された投稿ID（WHERE post_id = %s）に一致するデータを全部選んで（SELECT）ね」って意味
                cur.execute(sql, (post_id,)) # 上のSQL文をMySQLに発射するコマンド
                return cur.fetchall() # MySQlで該当したものすべてを呼び出し元に返す
        except pymysql.Error as e:
            print(f'リアクションにエラーが発生しています：{e}')
            abort(500) # 画面に500エラーを返す
        finally: # 上手くいってもいかなくても最後はこれを実行する
            db_pool.release(conn)  # DBのコネクションを片付ける


    @classmethod # リアクション機能の追加機能-保存(insert)
    def insert_reaction(cls, conn, post_id, user_id, emoji_type): #connを間借りする
        try: # try文 この領域内でエラーをかましたらexceptに移動
            with conn.cursor() as cur: # 保存するだけでOKなのでシンプルに
                sql = """
                    INSERT INTO post_reactions (post_id, user_id, emoji_type) 
                    VALUES (%s, %s, %s)
                """
                cur.execute(sql, (post_id, user_id, emoji_type)) # 上のSQL文をMySQLに発射するコマンド
                return True # 上手くいったらTrueを返す
        except pymysql.Error as e:
            print(f'リアクションにエラーが発生しています：{e}')
            raise e # エラーかましたら上位存在にパス


    @classmethod # リアクション機能の追加機能-削除(delete)
    def delete_reaction(cls, conn, post_id, user_id, emoji_type): #connを間借りする
        try: # try文 この領域内でエラーをかましたらexceptに移動
            with conn.cursor() as cur: # 保存するだけでOKなのでシンプルに
                sql = """
                    DELETE FROM post_reactions 
                    WHERE post_id = %s AND user_id = %s AND emoji_type = %s
                """
                cur.execute(sql, (post_id, user_id, emoji_type)) # 上のSQL文をMySQLに発射するコマンド
                return True # 上手くいったらTrueを返す
        except pymysql.Error as e:
            print(f'リアクションにエラーが発生しています：{e}')
            raise e # エラーかましたら上位存在にパス