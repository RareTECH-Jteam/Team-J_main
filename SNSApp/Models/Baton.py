from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

#Batonクラス
class Baton:
    @classmethod
    #バトン作成
    def create(cls, sender_id, receiver_id, task_id, content): 
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql =  "INSERT INTO Batons (sender_id, receiver_id, task_id, content) VALUES (%s, %s, %s, %s);"
                cur.execute(sql(sender_id, receiver_id, task_id, content))
                conn.commit()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)
    
    
    # @classmethod
    # #完了バトン取得
    # def get_by_complete_baton(cls, receiver_id):
    #     conn = db_pool.get_conn()
    #     conn.ping(reconnect=True)
    #     try:
    #         with conn.cursor() as cur:
    #             sql = "SELECT receiver_id, task_id, content FROM Baton WHERE status = 1 AND receiver_id = %s;"
    #             cur.execute(sql,(receiver_id,))
    #             return cur.fetchall()
    #     except pymysql.Error as e:
    #         print(f"エラーが発生:{e}")
    #         abort(500)
    #     finally:
    #         db_pool.release(conn)
    
    # @classmethod
    # #失敗バトン取得
    # def get_by_failure_baton(cls, receiver_id):
    #     conn = db_pool.get_conn()
    #     conn.ping(reconnect=True)
    #     try:
    #         with conn.cursor() as cur:
    #             sql = "SELECT receiver_id, task_id, content FROM Baton WHERE status = 2 AND receiver_id = %s;"
    #             cur.execute(sql,(receiver_id,))
    #             return cur.fetchall()
    #     except pymysql.Error as e:
    #         print(f"エラーが発生:{e}")
    #         abort(500)
    #     finally:
    #         db_pool.release(conn)
    
    # @classmethod
    # #未完バトン取得
    # def get_by_incomplete_baton(cls, receiver_id):
    #     conn = db_pool.get_conn()
    #     conn.ping(reconnect=True)
    #     try:
    #         with conn.cursor() as cur:
    #             sql = "SELECT receiver_id, task_id, content FROM Baton WHERE status = 0 AND receiver_id = %s;"
    #             cur.execute(sql,(receiver_id,))
    #             return cur.fetchall()
    #     except pymysql.Error as e:
    #         print(f"エラーが発生:{e}")
    #         abort(500)
    #     finally:
    #         db_pool.release(conn)
    
    @classmethod
    #未完、完了、失敗バトンまとめたもの
    def get_by_status(cls, receiver_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """SELECT receiver_id, task_id, content, 
                         CASE 
                              WHEN status = 0 THEN '未完了'
                              WHEN status = 1 THEN '完了'
                             WHEN status = 2 THEN '失敗' 
                         END AS status_label
                         FROM Baton WHERE receiver_id = %s;"""
                cur.execute(sql,(receiver_id,))
                return cur.fetchall()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)