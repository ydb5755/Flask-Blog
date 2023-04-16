import datetime
# from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flaskblog import db, login_manager
from flask import current_app
from flask_login import UserMixin
import jwt

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(20), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg') 
    password   = db.Column(db.String(60), nullable=False)
    posts      = db.relationship('Post', backref='author', lazy=True)

    # def get_reset_token(self, expires_sec=1800):
    #     s = Serializer(app.config['SECRET_KEY'], 
    #                    expires_sec
    #                    )
    #     return s.dumps({'user_id': self.id}).decode('utf-8')
    
    def get_reset_token(self, expiration=600):
        reset_token = jwt.encode(
            {
                "confirm": self.id,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                       + datetime.timedelta(seconds=expiration)
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return reset_token

    # @staticmethod
    # def verify_reset_token(token):
    #     s = Serializer(app.config['SECRET_KEY'])
    #     try:
    #         user_id = s.loads(token)['user_id']
    #     except:
    #         return None
    #     return User.query.get(user_id)



# Ok a bit of a description here, I removed the self property from verify_reset_token and changed up the code to have
# it return None for a bad token and return the User instance if it exists and token is good




    @staticmethod
    def verify_reset_token(token):
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                leeway=datetime.timedelta(seconds=10),
                algorithms=["HS256"]
            )
        except:
            return None
        if not User.query.get(data.get('confirm')):
            return None
        # self.confirmed = True
        # db.session.add(self)
        return User.query.get(data.get('confirm'))
    

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}' )"

    

# import jwt
# import datetime

# class SampleCode:
#     def generate_confirmation_token(self, expiration=600):
#         reset_token = jwt.encode(
#             {
#                 "confirm": self.id,
#                 "exp": datetime.datetime.now(tz=datetime.timezone.utc)
#                        + datetime.timedelta(seconds=expiration)
#             },
#             current_app.config['SECRET_KEY'],
#             algorithm="HS256"
#         )
#         return reset_token

#     def confirm(self, token):
#         try:
#             data = jwt.decode(
#                 token,
#                 current_app.config['SECRET_KEY'],
#                 leeway=datetime.timedelta(seconds=10),
#                 algorithms=["HS256"]
#             )
#         except:
#             return False
#         if data.get('confirm') != self.id:
#             return False
#         self.confirmed = True
#         db.session.add(self)
#         return True

class Post(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    content     = db.Column(db.Text, nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"