from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

# BatonQueueクラス
class BatonQueue:
    @classmethod
    def create(cls, title, sender_id, chain_id, relay_count):
        """相手がいない時に予約を入れる"""
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO baton_queues (title, sender_id, chain_id,relay_count) 
                VALUES (%s, %s, %s, %s);"""
                cur.execute(sql, (title, sender_id, chain_id, relay_count))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)
    
    @classmethod
    def get_next(cls):
        """一番古い予約を1件取得する"""
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM baton_queues ORDER BY created_at ASK LIMIT;"
                cur.execute(sql)
                queue = cur.fetchone()
            return queue
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def delete(cls, queue_id):
        """昇格し終わった予約を消す"""
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = "DELETE FROM baton_queues WHERE id =%s ;"
                cur.execute(sql,(queue_id,))
                queue = cur.fetchone()
            return queue
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)            