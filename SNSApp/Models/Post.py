from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

# Postsクラス
class Post:
    @classmethod
    def get_all(cls):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM posts WHERE  deleted_at IS NULL ORDER BY created_at DESC;"
                cur.execute(sql)
                posts = cur.fetchall()
            return posts
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    #投稿&勉強時間投稿
    def create(cls, user_id, content, study_time):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO posts (user_id, content, study_time) VALUES (%s, %s, %s);"
                cur.execute(sql, (user_id, content, study_time))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def delete(cls, post_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = "UPDATE posts SET deleted_at = NOW() WHERE id = %s;"
                cur.execute(sql, (post_id,))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_id(cls, post_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM posts WHERE id=%s AND deleted_at IS NULL;"
                cur.execute(sql, (post_id,))
                post = cur.fetchone()
            return post
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)
    
    #投稿編集
    @classmethod
    def update(cls, post_id, content, study_time):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = "UPDATE posts SET content = %s, study_time = %s, WHERE id = %s;"
                cur.execute(sql, (post_id, content, study_time))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)


    #総勉強時間取得
    @classmethod
    def get_total_study_time(cls, user_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = "SELECT SEC_TO_TIME(SUM(TIME_TO_SEC(study_time))) AS all_study FROM posts WHERE user_id = %s;"
                cur.execute(sql, (user_id,))
                all_study = cur.fetchone()
            return all_study
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)