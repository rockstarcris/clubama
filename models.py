from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import pytz 

db = SQLAlchemy()

chile_tz = pytz.timezone('America/Santiago')

class ProductRating(db.Model):
    __tablename__ = 'product_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(chile_tz))
    image = db.Column(db.String(255))  
    
    product = db.relationship('Product', backref=db.backref('ratings', lazy=True))
    user = db.relationship('User', backref=db.backref('ratings', lazy=True))

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(chile_tz))
    
    user = db.relationship('User', backref=db.backref('favorites', lazy=True))
    product = db.relationship('Product', backref=db.backref('favorites', lazy=True))

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(chile_tz))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50))
    slug = db.Column(db.String(200), unique=True)
    
    author = db.relationship('User', backref=db.backref('blog_posts', lazy=True))

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(chile_tz))
    approved = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref=db.backref('testimonials', lazy=True))

class FAQ(db.Model):
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    order = db.Column(db.Integer)

class StoreLocation(db.Model):
    __tablename__ = 'store_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    opening_hours = db.Column(db.JSON)
    image = db.Column(db.String(255))

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(700), nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    admin = db.relationship('User', backref=db.backref('products', lazy=True))
    
    additional_images = db.Column(db.JSON)  
    featured = db.Column(db.Boolean, default=False)  
    average_rating = db.Column(db.Float, default=0) 
    total_ratings = db.Column(db.Integer, default=0)  
    views = db.Column(db.Integer, default=0)  
    tags = db.Column(db.JSON)  
    specifications = db.Column(db.JSON)  
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(chile_tz))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.datetime.now(chile_tz))

    def update_rating_stats(self):
        ratings = ProductRating.query.filter_by(product_id=self.id).all()
        if ratings:
            self.average_rating = sum(r.rating for r in ratings) / len(ratings)
            self.total_ratings = len(ratings)
        else:
            self.average_rating = 0
            self.total_ratings = 0

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default='user') #LOLLLLLL user o admin
    ultimo_login = db.Column(db.DateTime, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.datetime.now(chile_tz))
    profile_image = db.Column(db.String(200), nullable=True, default='default.png')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin' 

class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref=db.backref('carts', lazy=True))
    product = db.relationship('Product', backref=db.backref('carts', lazy=True))

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

class HistorialCambios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    username = db.Column(db.String(100))
    email = db.Column(db.String(150))
    accion = db.Column(db.String(50), nullable=False)
    detalles = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=lambda: datetime.datetime.now(chile_tz))
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)