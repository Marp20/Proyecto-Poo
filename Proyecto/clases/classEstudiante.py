from flask_sqlalchemy import SQLAlchemy
from clases.classPreceptor import db

class Estudiante(db.Model):
    __tablename__ = 'estudiante'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    apellido = db.Column(db.String(50))
    idcurso = db.Column(db.Integer, nullable=False)
    idpadre = db.Column(db.Integer, db.ForeignKey('padre.id'), nullable=False)

    
    
    
