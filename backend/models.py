from mongoengine import Document, StringField, IntField

class User(Document):
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    

class Overlay(Document):
    user_id = StringField(required=True)
    content = StringField(required=True)
    x = IntField(required=True)
    y = IntField(required=True)
    width = IntField(required=True)
    height = IntField(required=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "content": self.content,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }
