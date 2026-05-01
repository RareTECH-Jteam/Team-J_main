from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

#Batonクラス
class Baton:
    @classmethod
    #バトン作成
    def create(cls, user_id, task_id, content): 
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        #conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql =  "INSERT INTO batons (user_id, task_id, content) VALUES (%s, %s, %s);"
                cur.execute(sql(user_id, task_id, content))
                conn.commit()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)
    
    @classmethod
    #全てのバトン取得
    def get_by_id(cls, user_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.corsor() as cur:
                sql = "SELECT * FROM baton WHERE user_id = %s ORDER BY get_at DESC;"
                cur.execute(sql(user_id,))
                return cur.fecthall()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)