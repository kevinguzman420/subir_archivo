from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Usuario(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	nombre_usuario = db.Column(db.String(64), nullable=False)
	correo = db.Column(db.String(128), nullable=True, unique=True, default="hola@hotmail.com")
	contrasenia = db.Column(db.String(94), nullable=False)
	id_rol = db.Column(db.Integer, db.ForeignKey('rol.id'), default=1, nullable=False)
	categoria = db.relationship('Categoria', backref='usuario')

	# Encriptar la contraseña:
	def set_password(self, contrasenia):
		self.contrasenia = generate_password_hash(contrasenia)

	# A la hora de logueo, se llama a esta función para verificar
	# si las contraseñas son válidas:
	def check_password(self, contrasenia):
		return check_password_hash(self.contrasenia, contrasenia)

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

	@staticmethod
	def get_by_id(id):
		return Usuario.query.get(id)

	@staticmethod
	def get_by_email(correo):
		return Usuario.query.filter_by(correo=correo).first()


class Categoria(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(128), nullable=False)
	id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
	image = db.relationship('Imagen', backref='categoria')

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()
	
	@staticmethod
	def obtener_categorias(id_usuario):
		return Categoria.query.filter_by(id_usuario=id_usuario).all()


class Imagen(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(128), nullable=False)
	descripcion = db.Column(db.Text, nullable=True)
	fecha = db.Column(db.String(64), nullable=False)
	id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

class Rol(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre_rol = db.Column(db.String(64), nullable=False)
	usuarios = db.relationship('Usuario', backref='rol')

