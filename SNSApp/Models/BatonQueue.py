from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

# BatonQueueクラス
class BatonQueue:    
    @classmethod
    def get_next(cls):
        """一番古い予約を1件取得する"""
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM baton_queues ORDER BY created_at ASC LIMIT 1;"
                cur.execute(sql)
                queue = cur.fetchone()
            return queue
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            raise Exception("予約が取得できませんでした") from e
        finally:
            db_pool.release(conn)  