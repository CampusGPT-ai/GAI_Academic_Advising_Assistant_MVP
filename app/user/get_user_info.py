from data.models import UserSession

class UserInfo:
    def __init__(self, user_info):
        self.user_info: UserSession = user_info 

        self.default_info = '''
    Student status: Undergraduate \n
    housing status: On campus \n
    Interested in: student life, academic registration, financial aid 

'''   
    
    def get_user_info(self):
        return self.default_info