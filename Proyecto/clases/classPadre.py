from flask_sqlalchemy import SQLAlchemy
from clases.classPreceptor import db



class Padre(db.Model):
    __tablename__ = 'padre'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    apellido = db.Column(db.String(50))
    correo = db.Column(db.String(120),unique=True, nullable=False)
    clave = db.Column(db.String(50), nullable=False)
    
    
    