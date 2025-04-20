import os
from flask import Flask, render_template, redirect, url_for, request, session, flash, Response, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Product, User, Cart, Order
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from models import HistorialCambios, FAQ, Favorite
from datetime import datetime, UTC
from sqlalchemy import func
from PIL import Image
import time
import pytz
import uuid

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)

chile_tz = pytz.timezone("America/Santiago")

ahora_utc = ahora_utc = datetime.now(UTC)
ahora_chile = ahora_utc.replace(tzinfo=pytz.utc).astimezone(chile_tz)

migrate = Migrate(app, db)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_IMAGE_SIZE'] = 2 * 1024 * 1024

app.config['SECRET_KEY'] = '2imcealfsyxh'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://losrocks_clubama:2imcealfsyxh@165.140.71.65/losrocks_agricultural_store'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def create_response(data=None, error=None, status=200):
    response = {}
    if data is not None:
        response['data'] = data
    if error is not None:
        response['error'] = error
    return jsonify(response), status

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def resize_image(image_path, max_size=(300, 300)):
    with Image.open(image_path) as img:
        img.thumbnail(max_size)
        img.save(image_path)

def get_current_user():
    if 'user_id' in session:
        return db.session.get(User, session['user_id'])
    return None

def update_cart_session():
    if 'user_id' not in session:
        return
    
    user_id = session['user_id']
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    
    session['cart_items'] = [{
        'id': item.id,
        'name': item.product.name,
        'price': item.product.price,
        'quantity': item.quantity,
        'image': item.product.image or 'default.jpg'
    } for item in cart_items]
    
    session['cart_total'] = sum(item.product.price * item.quantity for item in cart_items)

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/planes')
def view_planes():
    products = Product.query.filter_by(category='planes').all()
    return render_template('planes.html', products=products)

@app.route('/sustratos')
def view_sustratos():
    products = Product.query.filter_by(category='sustratos').all()
    return render_template('sustratos.html', products=products)

@app.route('/lombrices')
def view_lombrices():
    products = Product.query.filter_by(category='lombrices').all()
    return render_template('lombrices.html', products=products)

@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        flash('Por favor, inicie sesión para ver sus favoritos.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user_favorites = Favorite.query.filter_by(user_id=session['user_id']).all()
        return render_template('favorites.html', favorites=user_favorites)
    except Exception as e:
        flash('Error al cargar los favoritos', 'danger')
        return redirect(url_for('index'))

@app.route('/add_to_favorites/<int:product_id>', methods=['POST'])
def add_to_favorites(product_id):
    if 'user_id' not in session:
        return create_response(error='Usuario no autenticado', status=401)
    
    try:
        existing_favorite = Favorite.query.filter_by(
            user_id=session['user_id'],
            product_id=product_id
        ).first()
        
        if existing_favorite:
            db.session.delete(existing_favorite)
            db.session.commit()
            return create_response({'status': 'removed'})
        else:
            new_favorite = Favorite(user_id=session['user_id'], product_id=product_id)
            db.session.add(new_favorite)
            db.session.commit()
            return create_response({'status': 'added'})
    except Exception as e:
        return create_response(error='Error al procesar la solicitud', status=500)

@app.context_processor
def utility_processor():
    return {
        'current_year': datetime.now(UTC)
    }

@app.route('/update_cart/<int:cart_id>', methods=['POST'])
def update_cart(cart_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        quantity = int(data.get('quantity', 1))
        
        cart_item = Cart.query.get_or_404(cart_id)
        if cart_item.user_id != session['user_id']:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        cart_item.quantity = max(1, min(99, quantity))
        db.session.commit()
        
        update_cart_session()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash("Por favor, inicie sesión para agregar productos al carrito.")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    product = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
    
    db.session.commit()
    update_cart_session()
    
    flash("Producto agregado al carrito.", "success")
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash("Por favor, inicie sesión para ver su carrito.")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    if 'user_id' not in session:
        flash("Por favor, inicie sesión.", "warning")
        return redirect(url_for('login'))

    cart_item = Cart.query.get_or_404(cart_id)
    
    if cart_item.user_id != session['user_id']:
        flash("No autorizado", "danger")
        return redirect(url_for('cart'))

    db.session.delete(cart_item)
    db.session.commit()
    update_cart_session()  

    flash("Producto eliminado del carrito.", "success")
    return redirect(url_for('index'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        flash("Por favor, inicie sesión para proceder con la compra.")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)

    chile_tz = pytz.timezone("America/Santiago")
    ahora_utc = datetime.now(UTC)
    ahora_chile = ahora_utc.astimezone(chile_tz)

    order = Order(user_id=user_id, total=total, date=ahora_chile)
    db.session.add(order)

    for item in cart_items:
        db.session.delete(item)

    db.session.commit()
    flash("Compra realizada con éxito.", "success")
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash("El correo electrónico ya está registrado.")
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash("El nombre de usuario ya está en uso.")
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registro exitoso. Por favor, inicie sesión.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            chile_tz = pytz.timezone("America/Santiago")
            ahora_utc = datetime.now(UTC) 
            user.ultimo_login = ahora_utc.astimezone(chile_tz)

            db.session.commit()
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username
            session['user_image'] = user.profile_image or 'default.png'  
            
            flash(f"¡Bienvenido, {user.username}!", "success")
            return redirect(url_for('admin_dashboard') if user.role == 'admin' else url_for('index'))
        
        flash("Correo electrónico o contraseña incorrectos.", "danger")
    
    return render_template('login.html')

@app.route('/historial', methods=['GET'])
def historial():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tu historial', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('login'))
    
    pedidos = Order.query.filter_by(user_id=user_id).order_by(Order.date.desc()).all()
    return render_template('historial.html', pedidos=pedidos)

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tu perfil', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                resize_image(filepath)  
                user.profile_image = filename
        
        db.session.commit()
        flash('Perfil actualizado con éxito', 'success')
        return redirect(url_for('perfil'))
    
    return render_template('perfil.html', user=user)


@app.route('/perfil/editar', methods=['GET', 'POST'])
def editar_perfil():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    usuario = db.session.get(User, session['user_id'])
    if not usuario:
        return redirect(url_for('login'))

    cambios = []

    if request.method == 'POST':
        nombre_usuario = request.form.get('username')
        if nombre_usuario and nombre_usuario != usuario.username:
            usuario_existente = db.session.query(User).filter_by(username=nombre_usuario).first()
            if usuario_existente:
                flash('El nombre de usuario ya está en uso.', 'error')
                return redirect(url_for('editar_perfil'))
            cambios.append(f"Username: {usuario.username} -> {nombre_usuario}")
            usuario.username = nombre_usuario
        
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                if file.content_length > app.config['MAX_IMAGE_SIZE']:
                    flash('La imagen excede el tamaño máximo de 2MB.', 'error')
                    return redirect(url_for('editar_perfil'))
                
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                resize_image(filepath)
                
                if usuario.profile_image and usuario.profile_image != 'default.png':
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], usuario.profile_image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                cambios.append(f"Imagen de perfil actualizada.")
                usuario.profile_image = filename  
                session['user_image'] = filename

        if request.form.get('remove_image') == 'true':
            if usuario.profile_image and usuario.profile_image != 'default.png':
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], usuario.profile_image)
                if os.path.exists(image_path):
                    os.remove(image_path)
            cambios.append("Imagen de perfil eliminada.")
            usuario.profile_image = 'default.png'
            session['user_image'] = 'default.png'
        
        if cambios:
            chile_tz = pytz.timezone("America/Santiago")
            fecha = datetime.now(chile_tz)

            historial = HistorialCambios(
                usuario_id=usuario.id,
                username=usuario.username,
                email=usuario.email,
                accion="Edición de perfil",
                detalles="; ".join(cambios),
                fecha=fecha
            )
            db.session.add(historial)

        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('perfil'))
    
    return render_template('editar_perfil.html', usuario=usuario)


@app.route('/admin/stream')
def stream():
    if 'user_id' not in session or session.get('role') != 'admin':
        return "Unauthorized", 401

    def generate():
        previous_user_count = User.query.count()
        previous_order_count = Order.query.count()
        
        while True:
            current_user_count = User.query.count()
            current_order_count = Order.query.count()
            
            today_start = datetime.now(chile_tz).replace(hour=0, minute=0, second=0, microsecond=0)
            
            today_users = User.query.filter(
                func.date(User.fecha_creacion) == today_start.date()
            ).count()
            
            today_orders = Order.query.filter(
                func.date(Order.date) == today_start.date()
            ).count()

            if current_user_count != previous_user_count:
                new_user = User.query.order_by(User.id.desc()).first()
                user_data = {
                    'total': current_user_count,
                    'today_new': today_users,
                    'new_user': new_user.username if new_user else None
                }
                yield f"event: user_update\ndata: {json.dumps(user_data)}\n\n"
                previous_user_count = current_user_count
            
            if current_order_count != previous_order_count:
                new_order = Order.query.order_by(Order.id.desc()).first()
                order_data = {
                    'total': current_order_count,
                    'today_new': today_orders,
                    'new_order': new_order.id if new_order else None
                }
                yield f"event: order_update\ndata: {json.dumps(order_data)}\n\n"
                previous_order_count = current_order_count
            
            stats_data = {
                'users': {
                    'total': current_user_count,
                    'today_new': today_users
                },
                'orders': {
                    'total': current_order_count,
                    'today_new': today_orders
                }
            }
            yield f"event: stats_update\ndata: {json.dumps(stats_data)}\n\n"
            
            time.sleep(2)  

    return Response(generate(), mimetype="text/event-stream")

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Acceso denegado.", "danger")
        return redirect(url_for('index'))
    
    current_user = db.session.get(User, session['user_id'])
    
    total_users = User.query.count()
    total_orders = Order.query.count()
    
    today_start = datetime.now(chile_tz).replace(hour=0, minute=0, second=0, microsecond=0)
    
    today_users = User.query.filter(
        func.date(User.fecha_creacion) == today_start.date()
    ).count()
    
    today_orders = Order.query.filter(
        func.date(Order.date) == today_start.date()
    ).count()
    
    return render_template('admin.html', current_user=current_user,total_users=total_users,total_orders=total_orders,today_users=today_users,today_orders=today_orders)

@app.route('/admin/usuarios')
def admin_usuarios():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    search = request.args.get('search', '', type=str)
    role_filter = request.args.get('role', '', type=str)
    sort_by = request.args.get('sort_by', 'id', type=str)  
    order = request.args.get('order', 'asc', type=str)  

    query = User.query
    
    if search:
        query = query.filter(User.username.ilike(f'%{search}%'))

    if role_filter:
        query = query.filter(User.role == role_filter)

    if order == 'asc':
        query = query.order_by(getattr(User, sort_by).asc())
    else:
        query = query.order_by(getattr(User, sort_by).desc())

    usuarios = query.paginate(page=page, per_page=per_page, error_out=False)

    total_usuarios = query.count()

    return render_template('admin_usuarios.html', usuarios=usuarios, search=search, role_filter=role_filter, sort_by=sort_by, order=order, total_usuarios=total_usuarios)


@app.route('/admin/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    usuario = User.query.get_or_404(id)
    
    if request.method == 'POST':
        admin_id = session.get('user_id')

        admin_user = User.query.get(admin_id)
        if admin_user and admin_user.role != 'admin':
            admin_id = None

        cambios = []

        if 'username' in request.form and usuario.username != request.form['username']:
            cambios.append(f"Username: {usuario.username} -> {request.form['username']}")
            usuario.username = request.form['username']

        if 'email' in request.form and usuario.email != request.form['email']:
            cambios.append(f"Email: {usuario.email} -> {request.form['email']}")
            usuario.email = request.form['email']

        if 'role' in request.form and usuario.role != request.form['role']:
            cambios.append(f"Rol: {usuario.role} -> {request.form['role']}")
            usuario.role = request.form['role']

        db.session.commit()

        if cambios:
            historial = HistorialCambios(
            usuario_id=usuario.id,
            username=usuario.username,
            email=usuario.email,
            accion="Edición",
            detalles="; ".join(cambios),
            admin_id=admin_id
        )
        db.session.add(historial)
        db.session.commit()

        flash("Cambios guardados exitosamente.", "success") 

        if admin_id and admin_user.role == 'admin':  
            return redirect(url_for('admin_usuarios'))
        else:
            return redirect(url_for('perfil', id=usuario.id))
    
    return render_template('admin_usuarios.html', usuario=usuario)

@app.route('/admin/eliminar_usuario/<int:id>')
def eliminar_usuario(id):
    usuario = User.query.get_or_404(id)
    admin_id = session.get('user_id')

    historial = HistorialCambios(
        usuario_id=usuario.id,
        username=usuario.username,
        email=usuario.email,
        accion="Eliminación",
        detalles=f"Usuario eliminado: {usuario.username} ({usuario.email})",
        admin_id=admin_id
    )

    db.session.add(historial)
    db.session.delete(usuario)
    db.session.commit()

    return redirect(url_for('admin_usuarios'))

@app.route('/admin/historial')
def ver_historial():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('index'))

    historial = HistorialCambios.query.order_by(HistorialCambios.fecha.desc()).all()
    return render_template('historial_cambios.html', historial=historial)

@app.route('/admin/products', methods=['GET', 'POST'])
def admin_products():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Acceso denegado.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        category = request.form['category']
        admin_id = session['user_id']

        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
        else:
            image_path = None  

        product = Product(name=name, description=description, price=price, stock=stock, category=category, created_by=admin_id, image=image_path)
        db.session.add(product)
        db.session.commit()
        flash("Producto agregado con éxito.", "success")
        return redirect(url_for('admin_products')) 

    products = Product.query.all()
    return render_template('admin_products.html', products=products)

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Acceso denegado.", "danger")
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.stock = int(request.form['stock'])
        product.category = request.form['category']
        
        if request.form.get('remove_image'):
            if product.image:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
                if os.path.exists(image_path):
                    os.remove(image_path)
                product.image = None 
        
        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            product.image = filename
        
        db.session.commit()
        flash("Producto actualizado con éxito.", "success")
        return redirect(url_for('admin_products'))
    
    return render_template('edit_product.html', product=product)

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Acceso denegado.", "danger")
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Producto eliminado con éxito.", "success")
    
    return redirect(url_for('admin_products'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for('index'))

def format_text(text, width=40):
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return ''.join(lines)

app.jinja_env.filters['format_text'] = format_text

if __name__ == '__main__':
    app.run(debug=True)