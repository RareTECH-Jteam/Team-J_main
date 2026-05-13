from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

#Batonクラス
class Baton:
    @classmethod
    #バトン作成
    def create(cls, sender_id, receiver_id, task_id,): 
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql =  "INSERT INTO Baton (sender_id, receiver_id, task_id) VALUES (%s, %s, %s);"
                cur.execute(sql,(sender_id, receiver_id, task_id,))
                conn.commit()
                return cur.lastrowid
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
    

    @classmethod
    #完了、失敗バトン取得
    def get_completed_and_failed(cls, receiver_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """ SELECT 
                              sender.id AS sender_id 
                            , sender.name AS sender_name
                            , receiver.id AS receiver_id 
                            , receiver.name AS receiver_name
                            , Baton.task_id 
                            , Baton.content 
                            , Baton.status
                            , Baton.created_at
                           FROM Baton 
                             INNER JOIN  users sender
                               on Baton.sender_id = sender.id
                               INNER JOIN users receiver
                                on Baton.receiver_id = receiver.id
                           WHERE 1 = 1
                           AND Baton.status IN(1, 2) 
                           AND receiver_id = %s;
                """
                cur.execute(sql,(receiver_id,))
                return cur.fetchall()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    #未完バトン取得
    def get_by_incomplete_baton(cls, receiver_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """ SELECT 
                              Baton.id
                            , sender.id AS sender_id 
                            , sender.name AS sender_name
                            , receiver.id AS receiver_id 
                            , receiver.name AS receiver_name
                            , Baton.task_id 
                            , Baton.content 
                            , Baton.status
                            , Baton.created_at
                            , Baton.batonpop
                            , DATE_ADD(Baton.created_at ,  INTERVAL 1 DAY) AS time_limit
                           FROM Baton 
                             INNER JOIN  users sender
                               on Baton.sender_id = sender.id
                               INNER JOIN users receiver
                                on Baton.receiver_id = receiver.id
                           WHERE 1 = 1
                           AND  Baton.status = 0 
                           AND Baton.receiver_id = %s;
                """
                cur.execute(sql,(receiver_id,))
                return cur.fetchone()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)
    
    @classmethod
    #自分以外のバトン完了してる人を取得
    #バトンの送り先を選別するため
    def get_receiver(cls,user_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """SELECT users.id 
                         FROM users 
                           LEFT JOIN Baton 
                             ON users.id = Baton.receiver_id AND Baton.status = 0
                        WHERE users.id != %s
                        AND Baton.receiver_id IS NULL
                     """
                cur.execute(sql,(user_id,))
                return cur.fetchall()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)

    #24時間経ったもの取得する
    @classmethod
    def get_expired_batons(cls):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """SELECT
                           receiver_id
                         FROM
                             Baton
                         WHERE 1 = 1
                         AND TIMESTAMPDIFF(HOUR , created_at , NOW()) >= 24
                         AND status = 0;
                     """
                cur.execute(sql)
                return cur.fetchall()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)

    #24時間経ったものを失敗にする
    @classmethod
    def update_expired_status(cls):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """UPDATE Baton
                             SET status = 2
                         WHERE 1 = 1
                         AND TIMESTAMPDIFF(HOUR , created_at , NOW()) >= 24
                         AND status = 0;
                     """
                cur.execute(sql)
                conn.commit()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)

    # @classmethod
    # #未完、完了、失敗バトンまとめたもの
    # def get_by_status(cls, receiver_id):
    #     conn = db_pool.get_conn()
    #     conn.ping(reconnect=True)
    #     try:
    #         with conn.cursor() as cur:
    #             sql = """SELECT receiver_id, task_id, content, 
    #                      CASE 
    #                           WHEN status = 0 THEN '未完了'
    #                           WHEN status = 1 THEN '完了'
    #                          WHEN status = 2 THEN '失敗' 
    #                      END AS status_label
    #                      FROM Baton WHERE receiver_id = %s;"""
    #             cur.execute(sql,(receiver_id,))
    #             return cur.fetchall()
    #     except pymysql.Error as e:
    #         print(f"エラーが発生:{e}")
    #         abort(500)
    #     finally:
    #         db_pool.release(conn)

    @classmethod
    # バトンチェーンを取得
    def get_baton_chain(cls, receiver_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """WITH RECURSIVE Past AS (
                            -- ① アンカー：ログインユーザーが受け取った最新のバトンを起点にする
                            SELECT *
                            FROM Baton
                            WHERE receiver_id =%s
                            UNION ALL
                            -- ② 再帰：1個前の sender が誰から受け取ったかを辿っていく
                            SELECT bat.*
                            FROM Past p
                            JOIN Baton bat
                            ON p.sender_id = bat.receiver_id
                        )

                        -- 自分が渡した後のバトン履歴
                        , Future AS (
                        -- ① アンカー：ログインユーザーが受け取った最新のバトンを起点にする
                            SELECT *
                            FROM Baton
                            WHERE sender_id = %s
                            UNION ALL

                        -- ② 再帰：1個後の receiver が誰に送ったかを辿っていく
                            SELECT bat.*
                            FROM Future f
                            JOIN Baton bat
                            ON f.receiver_id = bat.sender_id
                        )
                        SELECT * 
                        FROM(
                            SELECT * FROM Past
                            UNION 
                            SELECT * FROM Future
                            ) AS Baton_logs
                        -- バトン作成（昇順）
                        ORDER BY created_at ASC"""
                
                cur.execute(sql,(receiver_id,receiver_id))
                return cur.fetchall()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    # バトンチェーンを取得
    def mark_as_read(cls, baton_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """UPDATE  Baton SET batonpop = 1 
                         WHERE id = %s
                      """
                cur.execute(sql,(baton_id,))
                cur.commit()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)        