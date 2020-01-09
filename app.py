from flask import Flask, render_template, request, redirect, url_for, g, send_from_directory, flash
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_sqlalchemy import    SQLAlchemy # pip3 install flask-sqlalchemy
from werkzeug.urls import url_parse
from datetime import datetime
# librerias para crear las categorias
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '\xd5\xeb\xb16\x1e79\xd6[\xcb\x9fBX\xc0x\xa3K~d\x9d\x02\xdc\xc2FX\x9a\xe5)\xc4\n\x97Q\xef\xba\x07\x82n\x0b\x1a\xa7'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://kevinguzman:kevinguzman@127.0.0.1:3306/subir_archivos"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
login_manager.login_view = 'index'

db = SQLAlchemy(app)

from models import *

EXTENSIONES_PERMITIDAS = set(["png", "jpg", "gif", "jpeg"])

def extensiones_permitidas(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in EXTENSIONES_PERMITIDAS

@app.before_request
def before_request_for_user():
	g.usuario = current_user

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template("index.html", categorias=Categoria.obtener_categorias(current_user.id))
    else:
        return render_template("index.html")

@app.route('/inicio-sesion/', methods=['GET', 'POST'])
def inicio_sesion():
    if current_user.is_authenticated:
        return redirect(url_for('crear_categoria'))
    if request.method == "POST":
        usuario = Usuario.get_by_email(request.form.get("correo"))
        print("paso el post")
        if usuario is not None and usuario.check_password(request.form.get("contraseña")):
            
            login_user(usuario, remember=True)

            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                categorias = Categoria.obtener_categorias(current_user.id) # no se usa...
                next_page = url_for("crear_categoria")
            # print("Bienvenido ", usuario.nombre_usuario)
            flash("Bienvenido " + usuario.nombre_usuario)
            return redirect(next_page)
        flash("Usuario inválido.")
        print("usuario: " + str(usuario))
    return render_template("inicio_sesion.html")

@app.route('/registro/', methods=['GET', 'POST'])
def registro():
    if request.method == "POST":
        usuario = Usuario.get_by_email(request.form.get("correo"))
        if usuario is not None:
            flash("Ya existe una cuenta asociada a este correo.")
        else:
            nombre = request.form.get("nom-usuario")
            correo = request.form.get("correo")
            contrasenia = request.form.get("contraseña")

            try:
                usuario = Usuario(nombre_usuario=nombre, correo=correo, id_rol=None)
                usuario.set_password(contrasenia)
                usuario.save()
                next_page = request.args.get('next', None)
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('inicio_sesion')
                    flash("el usuario ha sido creado con exito.")
                return redirect(next_page)
            except:
                flash("Error en el servidor, intentelo más tarde.")
    if current_user.is_authenticated:
        return render_template("registro.html", categorias=Categoria.obtener_categorias(current_user.id))
    else:
        return render_template("registro.html")

@app.route('/crear-categoria/', methods=['GET', 'POST'])
def crear_categoria():
    if request.method == "POST":
        if request.form.get("nombre_categoria"):
            nom_categoria = request.form.get("nombre_categoria").upper()
            nombre_categoria = secure_filename(nom_categoria)
            print(nombre_categoria)
            # Crear la carpeta de la categoria:
            if not os.path.exists("./static/images/" + nombre_categoria):
                try:
                    categoria = Categoria.verificar_categoria(nombre_categoria)
                    if categoria is not None:
                        flash("Ya tienes una categoria con el mismo nombre.")
                    else:
                        categoria = Categoria(nombre=nombre_categoria.upper(), id_usuario=current_user.id)
                        categoria.save()
                        os.mkdir("./static/images/" + nombre_categoria)
                        categorias = Categoria.obtener_categorias(current_user.id)
                        flash("Categoria creada con exito.")
                        # return redirec(url_for("subir_archivo"))
                        return render_template("crear_categoria.html", categorias=Categoria.obtener_categorias(current_user.id))

                except:
                    flash("Ha habido un error 500 en el servidor, vuelva e intentarlo más tarde.")
            else:
                categoria = Categoria.verificar_categoria(nombre_categoria)
                if categoria is not None:
                    flash("Ya tienes una categoria con el mismo nombre.")
                else:
                    categoria = Categoria(nombre=nombre_categoria.upper(), id_usuario=current_user.id)
                    categoria.save()
                    flash("Categoria creada con exito.")
        else:
            flash("Ingrese nombre de la categoria.")
    return render_template("crear_categoria.html", categorias=Categoria.obtener_categorias(current_user.id))

@app.route('/subir-archivos/', methods=['GET', 'POST'])
def subir_archivo():
    # categorias = Categoria.obtener_categorias(current_user.id)
    if request.method == "POST":
        nombre_categoria = request.form.get("opciones")
        # if Categoria.query.filter_by(nombre=nombre_categoria).first():
        categoria = Categoria.query.filter_by(nombre=nombre_categoria, id_usuario=current_user.id).first()
        print(categoria.nombre)
        UPLOAD_FOLDER = os.path.abspath("./static/images/" + nombre_categoria)
        app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
        if "cargar_archivo" not in request.files:
            flash("El formulario no tiene la parte que corresponde al archivo.")
        f = request.files["cargar_archivo"]
        if f.filename == "":
            flash("No ha seleccionado un archivo.")
        """
        LAS IMAGENES YA ESTAN GUARDADAS EN LA CARPETA DE SU CATEGORIA CORRESPONDIENTE,
        HACE FALTA GUARDARLAS EN LA CATEGORIA CORRESPONDIENTE EN LA BASE DE DATOS.
        """
        if f and extensiones_permitidas(f.filename):
            filename = secure_filename(f.filename)

            if request.form.get("renombrar_archivo"):
                filename = request.form.get("renombrar_archivo")
                filename = secure_filename(filename)

            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            flash("archivo guardado correctamente en la categoria: " + nombre_categoria)
            
            fecha = datetime.now()
            fecha = fecha.strftime("%Y-%m-%d")
            imagen = Imagen(nombre=filename, descripcion=request.form.get("descripcion_imagen"), \
                     fecha=fecha, id_categoria=categoria.id)
            imagen.save()
            flash("archivo guardado correctamente")
            return render_template("subir_archivo.html", categorias=Categoria.obtener_categorias(current_user.id))
        else:
            flash("El archivo tiene una extensión no permitida.")
    return render_template("subir_archivo.html", categorias=Categoria.obtener_categorias(current_user.id))

# @app.route('/mis-archivos/')
@app.route('/mis-archivos/<categoria>/')
def mis_archivos(categoria=None):
    if categoria:
        print("antes categoria")
        categoria = Categoria.query.filter_by(nombre=categoria, id_usuario=current_user.id).first()
        # categoria = db.session.query(Categoria).filter(Categoria.nombre==categoria, Categoria.id_usuario==current_user.id).first()
        # categoria = Categoria.query.filter_by(nombre=categoria).filter(Categoria.id_usuario==current_user.id)


        print(categoria)

        # categorias = Categoria.obtener_categorias(current_user.id).join(imagen, imagen.id_categoria==categoria.id).all()
        categoria_imagen = db.session.query(Imagen).join(Categoria).join(Usuario).filter(Usuario.id==current_user.id). \
                    filter(Imagen.id_categoria==categoria.id)
        lista_imagenes = []
        for cat in categoria_imagen:
            lista_imagenes.append(cat)
        
        for l in lista_imagenes:
            print(l)
            print(l.nombre)
            print(l.fecha)


        context = {"categorias": Categoria.obtener_categorias(current_user.id),
                    "categoria": categoria.nombre,
                    "imagenes": lista_imagenes}

        return render_template("mis_archivos.html", **context)
        # return render_template("mis_archivos.html", categorias=Categoria.obtener_categorias(current_user.id))
        

        # imagenes = Imagen.query.join(categoria).join(usuario).add_columns(usuario.id, usuario.nombre_usuario, categoria.id, categoria.nombre, 
        # imagen.id, imagen.nombre).filter_by(usuario.id=current_user.id).filter_by(categoria.id=categoria.id).paginate(page, 1, False)
        # imagenes = Post.query.join(followers, (followers.c.followed_id == Post.user_id))
        # imagenes = Imagen.query.join(categoria, (Imagen.id_categoria == categoria.id))
        # imagenes = Imagen.query.join(categoria).join(usuario).filter_by(categoria.id=categoria.id, usuario.id=current_user.id).all()
        # game = Game.query.join(Round).join(League, Round.league_id == League.id).filter(Game.utc_time < datetime.utcnow(),League.id == league.id \
        #         ).order_by(Game.utc_time.desc()).first()    
        # imagenes = Imagen.query.join(Categoria).join(Usuario).filter(Imagen.id_categoria==Categoria.id, Categoria.id_usuario == current_user.id \
        #         ).all()
        # return imagenes
    return render_template("mis_archivos.html", categorias=Categoria.obtener_categorias(current_user.id))

@app.route('/mis-archivos/<categoria>/<nombre_archivo>/')
def ver_imagen(categoria, nombre_archivo):
    UPLOAD_FOLDER = os.path.abspath("./static/images/" + categoria)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    return send_from_directory(app.config["UPLOAD_FOLDER"], nombre_archivo)

@app.route('/<categoria>/<imagen_nombre>/')
def borrar_imagen(categoria, imagen_nombre):
    print(categoria + " " + imagen_nombre)
    categoria = Categoria.query.filter_by(nombre=categoria, id_usuario=current_user.id).first()
    # print(str(categoria.id))
    nombre_imagen = Imagen.query.filter_by(nombre=imagen_nombre, id_categoria=categoria.id).first()
    print(str(nombre_imagen.id))
    db.session.delete(nombre_imagen)
    db.session.commit()
    return redirect(url_for('mis_archivos', categoria=categoria.nombre))

# CARGAR AL USUARIO:
@login_manager.user_loader
def load_user(user_id):
	return Usuario.get_by_id(int(user_id))
# ---

# LOGOUT:
@app.route("/salir")
@login_required
def salir():
	usuario = current_user.nombre_usuario
	logout_user()
	# flash("Come back soon, " + user)
	print("Vuelve pronto, " + usuario)
	return redirect(url_for('index'))
# ---
