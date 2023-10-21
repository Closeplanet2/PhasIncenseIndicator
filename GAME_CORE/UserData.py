from CORES.MongoController import MongoController

class UserData:
    def __init__(self, url, db_name):
        self.MongoController = MongoController(url=url, db_name=db_name)

    def return_user_data(self, username, session_code, wipe_data=False):
        user_data = self.MongoController.find_one("UserSmudgeData", {"USERNAME": username})
        if user_data is None or wipe_data: return self.create_new_user_data(username=username, session_code=session_code)
        return user_data

    def save_user_data(self, username, user_data):
        found_data = self.MongoController.find_one("UserSmudgeData", {"USERNAME": username})
        if found_data: self.MongoController.update_documents("UserSmudgeData", {"USERNAME": username}, user_data)
        else: self.MongoController.insert_document("UserSmudgeData", user_data)

    def return_all_user_data(self):
        return self.MongoController.get_collection("UserSmudgeData").find()

    def create_new_user_data(self, username, session_code):
        user_data = {}
        user_data["USERNAME"] = username
        user_data['SMUDGED'] = False
        user_data["SESSION_CODE"] = session_code
        return user_data
