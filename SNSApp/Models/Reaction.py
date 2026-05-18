from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

class Reactions: #リアクションクラス    
    @classmethod # リアクション機能のメイン
    def get_reactions_by_id(cls, post_id): #clsには自分のクラス名が入る
        conn = db_pool.get_conn() # コネクションチケット受け取り
        conn.ping(reconnect=True) # 生存報告
       
        try: # try文 この領域内でエラーをかましたらexceptに移動
            with conn.cursor() as cur: # 通常カーソル
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
            raise e # 画面に500エラーを返す
        finally:
            db_pool.release(conn) # 借りたら返す


    @classmethod # リアクション機能の追加機能-保存(insert)
    def insert_reaction(cls, conn, post_id, user_id, emoji_type): 
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
            raise e


    @classmethod # リアクション機能の追加機能-削除(delete)
    def delete_reaction(cls, conn, post_id, user_id):                 
        try: # try文 この領域内でエラーをかましたらexceptに移動
            with conn.cursor() as cur: # 削除するだけでOKなのでシンプルに
                sql = """
                    DELETE FROM post_reactions 
                    WHERE post_id = %s AND user_id = %s
                """     # post_reactionsテーブルから投稿ID、ユーザーID 全部消してねって文
                cur.execute(sql, (post_id, user_id)) # 上のSQL文をMySQLに発射するコマンド
                return True # 上手くいったらTrueを返す
        except pymysql.Error as e:
            print(f'リアクションにエラーが発生しています：{e}')
            raise e # エラーかましたら上位存在にパス

    @classmethod
    def validate(cls, emoji_type): # 絵文字が正しいものか検証ゾーン
        errors = [] # エラーメッセージを溜める箱
        if not emoji_type or emoji_type.strip() == "": # もし絵文字データがなかったり、空白スペースだったら
            errors.append("リアクションが空です") # 「空だよ」とエラー文を投げる
        return errors # ゴミ箱をルーティングに返す
    
    @classmethod
    def is_already_reaction(cls, conn, post_id, user_id): # ユーザーが絵文字をすでに押しているか判断ゾーン
            try: # try文 この領域内でエラーをかましたらexceptに移動
                with conn.cursor(pymysql.cursors.DictCursor) as cur: # 絵文字の列名でアクセスしたいので DictCursor を部分的に使う
                    sql = """
                        SELECT emoji_type FROM post_reactions 
                        WHERE post_id = %s AND user_id = %s
                    """     # COUNT(*)は「指定のテーブルの中に欲しい情報はいくつあるの」っていうのを数える
                    cur.execute(sql, (post_id, user_id)) # 上のSQL文をMySQLに発射するコマンド
                    result = cur.fetchone() # 結果を1つだけ入れる
                    return result
            except pymysql.Error as e:
                print(f'リアクションが重複しています：{e}')
                raise e # 500エラーを画面に返す
