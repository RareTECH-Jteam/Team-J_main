from flask import abort
import pymysql
from util.DB import DB
from datetime import datetime

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

# Postsクラス
class Post:
    @staticmethod
    # 分 → 00:00:00の形式に変換
    def minutes_to_time(minutes):
        minutes = int(minutes)
        h = minutes // 60
        m = minutes % 60

        return f"{h:02}:{m:02}:00"

    @staticmethod
    # 00:00:00の形式 → 分に変換
    def time_to_minutes(study_time):
        total_seconds = int(study_time.total_seconds())
        return total_seconds // 60

    @staticmethod
    def validate_content(content):
        # 空白かどうか
        if not content or content.strip() == '':
            return '投稿内容を入力してください'

        return None

    @staticmethod
    def validate_minutes(minutes):
        if not minutes or minutes.strip() == '':
            return '勉強時間を入力してください'

        minutes = minutes.strip()  # ← ここで strip した値に更新

        # 数値チェック
        if not minutes.isnumeric():
            return '勉強時間は数値または、0以上で入力してください'

        # int に変換してから比較
        if int(minutes) > 999:
            return '勉強時間は3桁以下で入力してください'
        
        return None

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
            raise
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
                sql = "UPDATE posts SET content = %s, study_time = %s ,  updated_at = SYSDATE(6) WHERE id = %s;"
                cur.execute(sql, (content ,study_time,post_id ))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            # abort(500)
            raise
        finally:
            db_pool.release(conn)

    #総勉強時間取得
    @classmethod
    def get_total_study_time(cls, user_id):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """SELECT SUM(TIME_TO_SEC(study_time)) DIV 3600 AS hours,
                                SUM(TIME_TO_SEC(study_time)) MOD 3600 DIV 60 AS minutes
                                FROM posts WHERE user_id = %s AND deleted_at IS NULL;"""
                cur.execute(sql, (user_id,))
                all_study = cur.fetchone()
            return all_study
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)
    
    #全ユーザーの勉強時間多い順に取得
    @classmethod
    def get_study_ranking(cls):
        conn = db_pool.get_conn()
        conn.ping(reconnect=True)
        try:
            with conn.cursor() as cur:
                sql = """SELECT SUM(TIME_TO_SEC(study_time)) DIV 3600 AS hours,
                                SUM(TIME_TO_SEC(study_time)) MOD 3600 DIV 60 AS minutes
                                FROM posts 
                                JOIN users ON posts.user_id = users.id
                                WHERE posts.deleted_at IS NULL
                                GROUP BY posts.user_id, users.name
                                ORDER BY SUM(TIME_TO_SEC(study_time)) DESC;"""
                cur.execute(sql)
                return cur.fetchall()
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)
        finally:
            db_pool.release(conn)