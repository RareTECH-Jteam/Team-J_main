from Models.Baton import Baton
from Models.BatonQueue import BatonQueue
from extensions import socketio

class services:
    @classmethod    
    # 予約バトンを誰かに割り当てる
    def assign_waiting_baton_if_possible(exclude_user_id=0):
        # キューから取得
        queue_data = BatonQueue.get_next()
        if queue_data:
            # 今フリーな人を探す
            free_user_id = Baton.get_available_receiver(exclude_user_id)
            
            if free_user_id:
                # 予約から正式なバトンを作成
                Baton.create_from_queue(queue_data, free_user_id)
                BatonQueue.delete(queue_data['id'])
                # SocketIOで本人に通知
                socketio.emit('notification', 
                            {'message': '待機バトンが回ってきました！'},
                            room=str(free_user_id))