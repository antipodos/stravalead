from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, id):
        self.id = id

        self.authenticated = False
        self.firstname = ""

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False
