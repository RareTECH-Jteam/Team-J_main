from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

#Batonクラス
class Baton:
    @classmethod
    def validate(cls, input):
        if not input or input.strip() == '':
            return 'タイトルを入力してください'

        return None

    @classmethod
    # 対象のバトン取得
    def find_by_id(cls, baton_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM Baton WHERE id = %s;"
                cur.execute(sql,(baton_id,))
                return cur.fetchone()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)
    

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
                            , Baton.baton_title
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
                            , Baton.baton_title
                            , sender.id AS sender_id 
                            , sender.name AS sender_name
                            , receiver.id AS receiver_id 
                            , receiver.name AS receiver_name
                            , Baton.task_id 
                            , Baton.content 
                            , Baton.chain_id
                            , Baton.relay_count
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
    def get_receiver(cls,user_id,chain_id):
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
                        AND users.id NOT IN (
                            SELECT sender_id FROM Baton WHERE chain_id = %s
                        )
                        ORDER BY RAND() LIMIT 1
                     """
                cur.execute(sql,(user_id,chain_id))
                user = cur.fetchone()
                if not user:
                    return None
                return user['id']
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
    # 通知フラグを「通知済み」に設定
    def mark_as_read(cls, baton_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """UPDATE  Baton SET batonpop = 1 
                         WHERE id = %s
                      """
                cur.execute(sql,(baton_id,))
                conn.commit()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)        
    
    @classmethod
    #バトンランキング取得
    def get_chain_ranking(cls):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """SELECT 
                           chain_id, 
                           MAX(relay_count) AS sum_count, 
                           baton_title 
                         FROM 
                           Baton 
                         WHERE 1 = 1 
                            AND status = 1
                            AND created_at >= DATE_FORMAT(NOW(), '%Y-%m-01') 
                            AND created_at <= LAST_DAY(NOW())
                         GROUP BY chain_id, baton_title 
                         ORDER BY MAX(relay_count) DESC;"""
                cur.execute(sql)
                return cur.fetchall()
            
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    # バトン総完了数を取得
    def get_total_completed_count(cls, user_id):
        conn = db_pool.get_conn() # 接続チケット取得
        conn.ping(reconnect=True) # 生存報告
        try:
            with conn.cursor() as cur: # 通常のカーソル取得
                sql = """
                    SELECT COUNT(*) as total_count
                    FROM Baton
                    WHERE status = 1 AND sender_id = %s
                """
                # Batonテーブルから、「statusが1（完了）」かつ「送信者が自分」の両方を満たすデータの行数を数えて、その結果に「total_count」というあだ名を付ける
                cur.execute(sql,(user_id,)) # 上のSQL文にこの情報をぶち込む
                result = cur.fetchone() # resultに上の文の結果をすべて入れる

                if isinstance(result,dict): # 返ってきた結果が辞書型(名前アリの箱)かどうか確認
                    return result["total_count"]
                return result[0] if result else 0 # 辞書じゃなく、タプル型(ただのリスト)だった場合は最初の0番目の数字を返す
        except pymysql.Error as e: # tryの中でエラーを起こした場合この中を発動
            print(f"バトン完了数カウントエラーが発生:{e}")
            abort(500)
        finally: # 上手くいこうが失敗しようが最後はここを実行
            db_pool.release(conn) # 接続チケットの変換


