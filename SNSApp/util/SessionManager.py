from flask import session

class SessionManager:
    @staticmethod
    def get_user_id():
        return session.get('user_id')
    
    @staticmethod
    def is_live_session():
        if session.get('user_id') == None:
            return False
        return True
    
    @staticmethod
    def create_session(user_id):
        session['user_id'] = user_id
    
    @staticmethod
    def clear_session():
        session.clear()