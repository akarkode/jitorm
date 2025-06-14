from orm.models import Model
from orm.fields import IntegerField, StringField


class Users(Model):
    id = IntegerField(primary_key=True)
    username=StringField()
    password=StringField()
    name=StringField()
    address=StringField()
    email=StringField()
    job=StringField()
    birthdate=StringField()
    phone_number=StringField()

class Followers(Model):
    id = IntegerField(primary_key=True)
    user_id = IntegerField()
    follower_id = IntegerField()


class Posts(Model):
    id = IntegerField(primary_key=True)
    user_id = IntegerField()
    content = StringField()
    image_url = StringField()


class Likes(Model):
    id = IntegerField(primary_key=True)
    post_id = IntegerField()
    user_id = IntegerField()


class Comments(Model):
    id = IntegerField(primary_key=True)
    post_id = IntegerField()
    user_id = IntegerField()
    comment = StringField()
    