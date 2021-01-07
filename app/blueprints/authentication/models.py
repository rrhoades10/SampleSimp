from app import db
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
from app.blueprints.blog.models import BlogPost 
from flask_login import UserMixin




followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(100), index=True)
    email = db.Column(db.String(100), unique=True, index=True)
    password = db.Column(db.String(200))
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    posts = db.relationship('BlogPost', cascade='all, delete-orphan', backref='user', lazy=True)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
        )

    

    def followed_posts(self):
        followed = BlogPost.query.join(
            followers, 
            (followers.c.followed_id == BlogPost.user_id)).filter(followers.c.follower_id == self.id)
        my_posts = BlogPost.query.filter_by(user_id=self.id)
        return followed.union(my_posts).order_by(BlogPost.created_on.desc())

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<User: {self.id} | {self.email}>'

    def hash_password(self, original_password):
        self.password = generate_password_hash(original_password)

    def check_hashed_password(self, original_password):
        return check_password_hash(self.password, original_password)

    def from_dict(self, data):
        for field in ['first_name', 'last_name', 'email']:
            if field in data:
                setattr(self, field, data[field])

@login.user_loader
def load_user(id):
    return User.query.get(int(id))