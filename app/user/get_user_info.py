from data.models import UserSession
from data.models import Profile
from settings.settings import Settings
from mongoengine import connect
settings = Settings()

class UserInfo:
    def __init__(self, user_id):
        self.user_profile = Profile.objects(user_id=user_id).first()
        self.default_info = '''
    Student status: Undergraduate \n
    housing status: On campus \n
    Interested in: student life, academic registration, financial aid 

'''   
    
    def get_user_info(self):
        if self.user_profile:
            return self.user_profile
        else:
            return self.default_info
        
if __name__ == "__main__":
    db_name = settings.MONGO_DB
    db_conn = settings.MONGO_CONN_STR
    _mongo_conn = connect(db=db_name, host=db_conn)
    print(f"Connected to mongo: {_mongo_conn}")
    user_info = UserSession.objects().first()
    user = UserInfo(user_info.user_id)
    print(user.get_user_info())