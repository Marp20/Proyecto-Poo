from flask_sqlalchemy import SQLAlchemy
from clases.classPreceptor import db


class Asistencia(db.Model):
    __tablename__ = 'asistencia'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(50))
    codigoclase = db.Column(db.Integer)
    asistio = db.Column(db.Boolean)
    justificacion = db.Column(db.String(120))
    idestudiante = db.Column(db.Integer, db.ForeignKey('estudiante.id'), nullable=False)
    
    def __str__(self):
        return f"Asistencia: {self.id} - Fecha: {self.fecha} - Código Clase: {self.codigoclase} - Asistió: {self.asistio} - Justificación: {self.justificacion} - ID Estudiante: {self.idestudiante}"
