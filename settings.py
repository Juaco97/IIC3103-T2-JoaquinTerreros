import os

# PRODUCCION
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
SECRET_KEY = os.environ.get('SECRET_KEY')
SQLALCHEMY_TRACK_MODIFICATIONS = False
TAREA_URL="https://iic3103-t2-joaquinterreros.herokuapp.com"
 #Hola

# LOCAL
#DATABASE_URL = 'sqlite:///test.db'
#SQLALCHEMY_DATABASE_URI = DATABASE_URL
#SECRET_KEY = "laksdjlaksjdalksjdlaksjdla"
#SQLALCHEMY_TRACK_MODIFICATIONS = False
#TAREA_URL = '127.0.0.1:5000'