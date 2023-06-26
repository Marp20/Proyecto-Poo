from flask_sqlalchemy import SQLAlchemy
from clases.classPreceptor import db


class Curso(db.Model):
    __tablename__ = 'curso'
    id = db.Column(db.Integer, primary_key=True)
    anio = db.Column(db.String(50))
    division = db.Column(db.String(50))
    idpreceptor = db.Column(db.Integer, db.ForeignKey('preceptor.id'), nullable=False)

    
    
    
