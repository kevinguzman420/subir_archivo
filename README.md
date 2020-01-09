# Sistema de ejemplo almacenar nuestras imagenes
Este ejemplo permite registrar usuarios, poder iniciar sesión, cerrar sesión, además permite la manipulación del menu principal para saber el estado del usuario.

Se incluyen los siguientes scripts:
- models.py Sirve para generar las tablas de la base de datos previamente creada.
- app.py Este archivo contiene las vistas, la cadena de conección

Instalación
-----------
Procedimiento básico (se requiere de unix, linux o C9.io), una vez que se ha bajado el archivo, se debe descomprimir y entrar al directorio que se genera (app):

	cd app

Una vez dentro del directorio se procede a crear el ambiente virtual de ejecución:

	virtualenv venv

Activamos el ambiente virtual:

	source venv/bin/activate

Ahora, una vez activado el ambiente virtual, instalamos los paquetes y extensiones necesarias:

	pip install -r requirements.txt

Ya instalados los requerimientos, procedemos a ejecutar la demo:

	export FLASK_APP=app.py
    export FLASK_DEBUG=True # Para activar el modo debug.
    flask run

Uso
----
Para poder usarlo basta con usar un navegador de internet y teclear la siguiente dirección:

	http://127.0.0.1:5000/

Paquetería o extensiones instaladas
------------------------------------
- Flask:		Es el framework que estamos usando para el sisema
- Flask-Login:	Extensión que permite el manejo de autenticación de usuarios
- Flask-SQLAlchemy:	Extensión que nos permite el uso de ORM hacia nuestra base de datos

## Copyright
Copyright © 2018-2020
