from flask import abort
import pymysql
from util.DB import DB
from datetime import datetime

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

class Task:
    @classmethod
    def get_all(cls):
        conn = db_pool.get_conn() #データベースから一つ借りてくる
        conn.ping(reconnect=True) #生存確認の一文(切れてたらreconnect)
        try: #まずはここを実行
            with conn.cursor() as cur: #cursorはSQLを実行するっていう宣言 (with文なのでこの空間だけcurを召喚)
                sql = "SELECT * FROM tasks;" #SQL文で実行するよ
                cur.execute(sql) #curにsqlを渡して実行してもらう
                tasks = cur.fetchall() #実行結果を全部(fetchallの効果)tasksに入れる
            return tasks #tasksを呼び出し元にお返し
        
        except pymysql.Error as e: #エラーが出たらここに来る
            print(f'エラーが発生しています：{e}')
            abort(500) # サーバーエラー(500)として中断命令

        finally: #何があっても最後に実行する
            db_pool.release(conn) #借りたものをプールに返却


    @classmethod
    #未完バトン取得
    def get_content_by_id(cls, task_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """ SELECT  content 
                          FROM tasks
                          WHERE 1 = 1
                          AND id = %s;
                """
                cur.execute(sql, (task_id,))
                task = cur.fetchone()
                return task['content']
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)