from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

# Chainクラス
class Chain:
    @classmethod
    def create(cls):
        """新しいバトンリレーの「Chain（繋がり）」を管理するIDを新規発行する"""
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO chain (created_at)  VALUES (NOW());
                """
                cur.execute(sql)
                conn.commit()
                return cur.lastrowid
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    
   