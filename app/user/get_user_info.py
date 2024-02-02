from data.models import UserSession

class UserInfo:
    def __init__(self, user_info):
        self.user_info: UserSession = user_info    
    
    def get_user_info(self):
        return self.user_info