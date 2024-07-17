from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, default="")
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, default=True)
    profile = db.relationship('Profile', backref="user", uselist=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "active": self.active
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit() 


class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    biography = db.Column(db.Text, default="")
    github = db.Column(db.String, default="")
    linkedin = db.Column(db.String, default="")
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "biography": self.biography,
            "github": self.github,
            "linkedin": self.linkedin
        }
    
    def serialize_full_info(self):
        return {
            "name": self.user.name,
            "username": self.user.username,
            "active": self.user.active,
            "biography": self.biography,
            "github": self.github,
            "linkedin": self.linkedin
        }
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

