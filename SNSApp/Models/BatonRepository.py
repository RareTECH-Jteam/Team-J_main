from flask import abort
import pymysql


#トランザクションクラス
class BatonRepository:
    @classmethod
    def baton_queues_create(cls, sender_id ,baton_data,conn):
        """相手がいない時に予約を入れる"""
        try:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO baton_queues (baton_title, sender_id, chain_id,relay_count) 
                VALUES (%s, %s, %s, %s);"""
                cur.execute(sql,(
                            baton_data['baton_title']
                          , sender_id
                          , baton_data['chain_id']
                          , baton_data['relay_count']
                            ))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            # abort(500)
            raise Exception("バトンの予約に失敗しました")

    @classmethod
    def baton_create_from_queue(cls, queue_data, receiver_id , conn):
        """予約データ(BatonQueueの結果)を元に正式なバトンを作る"""
        try:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO batons (baton_title, sender_id, receiver_id, chain_id, relay_count, status)
                VALUES (%s, %s, %s, %s, %s, 0)
                """                
                cur.execute(sql,(
                    queue_data['baton_title'],
                    queue_data['sender_id'],
                    receiver_id,
                    queue_data['chain_id'],
                    queue_data['relay_count']
                    ))

        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            # abort(500)
            raise Exception("予約リストからのバトン生成に失敗しました。")
    
    @classmethod
    def batonqueue_delete(cls, queue_id,conn):
        """昇格し終わった予約を消す"""
        try:
            with conn.cursor() as cur:
                sql = "DELETE FROM baton_queues WHERE id =%s ;"
                cur.execute(sql,(queue_id,))
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            # abort(500)  
            raise Exception("バトン予約の削除に失敗しました")

    @classmethod
    def baton_create(cls, sender_id, baton_data,conn):
        """バトンを作成"""
        try:
            with conn.cursor() as cur:
                sql =  """INSERT INTO Baton(
                            baton_title
                           , sender_id
                           , receiver_id
                           , task_id
                           , content
                           , chain_id
                           , relay_count 
                           , get_at) 
                           VALUES 
                           (%s
                          , %s
                          , %s
                          , %s
                          , %s
                          , %s
                          , %s
                          , NOW()
                          );"""
                
                cur.execute(sql,(
                            baton_data['baton_title']
                          , sender_id
                          , baton_data['receiver_id']
                          , baton_data['task_id']
                          , baton_data['content']
                          , baton_data['chain_id']
                          , baton_data['relay_count']
                            ))
                return cur.lastrowid
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            # abort(500)
            raise Exception("バトンの作成に失敗しました")

    @classmethod
    def baton_update_status_success(cls,baton_id,conn):
        """バトンを完了にする"""
        try:
            with conn.cursor() as cur:
                sql =  """Update Baton 
                            SET status = 1
                             ,  release_at = NOW()
                            WHERE 1 = 1
                            AND id = %s;
                        """
                
                cur.execute(sql,(baton_id,))
                # return cur.lastrowid
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            # abort(500)
            raise Exception("バトンが完了できませんでした")

    #24時間経ったものを失敗にする
    @classmethod
    def update_expired_status(cls,conn):
        try:
            with conn.cursor() as cur:
                sql = """UPDATE Baton
                                SET status = 2
                            WHERE 1 = 1
                            AND TIMESTAMPDIFF(HOUR , created_at , NOW()) >= 24
                            AND status = 0;
                        """
                cur.execute(sql)
        except pymysql.Error as e:
            print(f"エラーが発生:{e}")
            abort(500)