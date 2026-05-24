from Models.User import User
from Models.Baton import Baton
from Models.BatonQueue import BatonQueue
from Models.BatonRepository import BatonRepository
from extensions import socketio
from util.DB import DB
db_pool = DB.init_db_pool()

class baton_services:
    @classmethod
    def process_baton_relay(cls, sender_id, baton_data):
        conn = db_pool.get_conn()
        try:
            # ターゲット探索（自分または自分に送ってきた人を除外）
            # 新規の場合はpre_sender_id = 自分になる
            pre_sender_id = baton_data['pre_sender_id'] or sender_id
            
            # 次の送り先
            next_receiver_id = Baton.get_receiver(sender_id,pre_sender_id)
            print(f"次の人: {next_receiver_id}")
            
            # 継続の場合のみ完了にする
            if baton_data.get('baton_id'):
                BatonRepository.baton_update_status_success(baton_data['baton_id'], conn)

            # 空き枠あり
            if next_receiver_id:                          
                # 受け取りユーザー設定
                baton_data['receiver_id'] = next_receiver_id
                
                # バトン作成
                new_baton_id = BatonRepository.baton_create(sender_id
                                            ,baton_data
                                            ,conn)
                
                # コミット
                conn.commit()

                username = User.get_name_by_id(next_receiver_id)
                print("ユーザー名 " + username)                  
                
                # 受け取った人に通知
                socketio.emit('notification'
                    , {
                        'message': 'バトンが渡されました！\r\n確認してみよう！'
                        ,'baton_id':new_baton_id
                        ,'reload':True  
                       }
                    , room=str(next_receiver_id))  
                
                print("送った人に通知がいかないよおお  "+ str(sender_id))

                # 送った人に通知
                socketio.emit('notification'
                    , {
                        'message': f'{username}さんに、バトンを渡したよ！！'
                        ,'reload':True                        
                        }
                    , room=str(sender_id))                  
            
            # 空き枠なし
            else:
                # 予約リスト追加
                BatonRepository.baton_queues_create(sender_id
                                                    , baton_data
                                                    , conn)
                # コミット
                conn.commit()
                
                # 通知
                socketio.emit('notification'
                              , {'message': '送り先がいません。\r\n予約リストに入れました'
                                 ,'reload':True  
                                 }
                              , room=str(sender_id))

                # 自分がフリーになったので、待機中の「別のバトン」を誰かに割り当てる
                cls.assign_waiting_baton_if_possible(conn, exclude_user_id=sender_id )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            conn.rollback()
            raise e
        finally:
            db_pool.release(conn)


    @classmethod    
    # 予約バトンを誰かに割り当てる
    def assign_waiting_baton_if_possible(cls,conn,exclude_user_id = None):
        # キューから取得
        queue_data = BatonQueue.get_next()

        if queue_data:
            
            ex_id = exclude_user_id or queue_data['sender_id']
            pre_id = queue_data['sender_id']
            print(f"ex_id: {ex_id}, pre_id: {pre_id}")
            
            # 今フリーな人を探す
            free_user_id = Baton.get_receiver(ex_id,pre_id)

            print(free_user_id)
            
            if free_user_id:
                # 予約から正式なバトンを作成
                BatonRepository.baton_create_from_queue(queue_data, free_user_id , conn)
                
                # 予約から削除する
                BatonRepository.batonqueue_delete(queue_data['id'],conn)
                
                # 通知
                socketio.emit('notification', 
                            {'message': '待機バトンが回ってきました！'
                             ,'reload':True  
                             },
                            room=str(free_user_id))