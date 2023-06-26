from datetime import timedelta,datetime
from flask import Flask, render_template, redirect, url_for, request, abort,flash,session,g
from flask_sqlalchemy import SQLAlchemy
import hashlib


app = Flask(__name__)
app.config.from_pyfile('config.py')


from clases.classPreceptor import Preceptor,db
from clases.classPadre import Padre
from clases.classCurso import Curso
from clases.classEstudiante import Estudiante
from clases.classAsistencia import Asistencia

class User:
    def __init__(self, user_id, rol):
        self.id = user_id
        self.rol = rol

user = None
Login = False
cont_asistencia = 0

@app.route('/')
def pagina_principal():
    return render_template('inicio.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global Login
    global user
    
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['clave']
        rol = request.form['rol']
        
        user = Preceptor.query.filter_by(correo=correo).first()
        if user and user.clave == hashlib.md5(password.encode()).hexdigest() and rol == 'Preceptor':
            Login = True
            user_id = user.id
            user = User(user_id, rol)
            session['user_id'] = user.id
            session['rol'] = rol
            session.permanent = True
            g.last_activity = datetime.now()  
            flash('Has iniciado sesión exitosamente')
            return render_template('index.html')
        
        user = Padre.query.filter_by(correo=correo).first()
        if user and user.clave == hashlib.md5(password.encode()).hexdigest() and rol == 'Padre':
            Login = True
            user_id = user.id
            user = User(user_id, rol)
            session['user_id'] = user.id
            session['rol'] = rol
            session.permanent = True
            g.last_activity = datetime.now()  
            flash('Has iniciado sesión exitosamente')
            return render_template('inicio_padre.html')
        
            
        return abort(401)
        
    return render_template('login.html')

@app.before_request
def update_last_activity():
    if 'user_id' in session:
        g.last_activity = datetime.now()
    else:
        g.last_activity = None

@app.route('/Registro')
def mostrar_cursos():
    global Login
    global user
    
    pag=request.args.get('pag')
    cursos = Curso.query.filter_by(idpreceptor=user.id).all()
    estudiantes = []
    codigos_clase = set()
    fechas_asistencia = set()

    i = 0
    if g.last_activity and (datetime.now() - g.last_activity) <= app.permanent_session_lifetime:
        while i < len(cursos) and user.rol == 'Preceptor':
            curso = cursos[i]
            estudiantes_curso = Estudiante.query.filter_by(idcurso=curso.id).all()
            estudiantes.extend(estudiantes_curso)
                
            j = 0
            while j < len(estudiantes_curso):
                estudiante = estudiantes_curso[j]
                asistencias = Asistencia.query.filter_by(idestudiante=estudiante.id).all()
                codigos = [asistencia.codigoclase for asistencia in asistencias]
                codigos_clase.update(codigos)
                fechas = [asistencia.fecha for asistencia in asistencias]
                fechas_asistencia.update(fechas)
                    
                j += 1
                
            i += 1
                
        if pag == 'registro':   
            return render_template('cursos.html', cursos=cursos, fechas=fechas_asistencia, codigos_clase=codigos_clase)
        elif pag =='detalles':
            return render_template('cursos_informe.html', cursos=cursos, fechas=fechas_asistencia, codigos_clase=codigos_clase)
        else:
            flash('No tienes autoridad sobre esta funcion.')
            return render_template('inicio_padre.html')
    else:
        flash('Tu sesión ha expirado. Inicia sesión nuevamente.')
        return redirect(url_for('login'))


@app.route('/cargar_asistencia', methods=['GET', 'POST'])
def estudiantes():
    
    global user
    
    if g.last_activity and (datetime.now() - g.last_activity) <= app.permanent_session_lifetime:
        if request.method == 'POST':
            idcurso = request.form['curso']
            estudiantes = Estudiante.query.filter_by(idcurso=idcurso).all()
            curso = Curso.query.get(idcurso)

            asistencias = []
            for estudiante in estudiantes:
                asistencia = Asistencia.query.filter_by(idestudiante=estudiante.id).first()
                asistencias.append(asistencia)
            
            return render_template('estudiantes.html', estudiantes=estudiantes, curso=curso, asistencias=asistencias)
        
        return render_template('cursos.html')
    else:
        flash('Tu sesión ha expirado. Inicia sesión nuevamente.')
        return redirect(url_for('login'))

@app.route('/guardar_asistencia', methods=['POST'])
def guardar_asistencia():
    curso_id = request.form['curso']
    clase = request.form['tipo_asistencia']
    fecha = request.form['fecha_asistencia']
    
    
    curso = Curso.query.get(curso_id)
    if g.last_activity and (datetime.now() - g.last_activity) <= app.permanent_session_lifetime:
        if curso and curso.idpreceptor == user.id:
            estudiantes = Estudiante.query.filter_by(idcurso=curso_id).all()
            
            for estudiante in estudiantes:
                asistencia_key = 'asistencia_{}'.format(estudiante.id)
                justificacion_key = 'justificacion_{}'.format(estudiante.id)
                asistencia = request.form.get(asistencia_key)
                justificacion = request.form.get(justificacion_key)
                
                asistencia_obj = Asistencia(fecha=fecha, codigoclase=clase, asistio=asistencia=="True", justificacion=justificacion, idestudiante=estudiante.id)
                print(asistencia_obj)
                db.session.add(asistencia_obj)
                
            db.session.commit()
            return render_template('index.html')
        
        return render_template('index.html')
    else:
        flash('Tu sesión ha expirado. Inicia sesión nuevamente.')
        return redirect(url_for('login'))


@app.route('/informe', methods=['GET', 'POST'])
def detalles():
    global Login
    global user
    
    curso_id = request.form['curso']
    curso = Curso.query.get(curso_id)
    if g.last_activity and (datetime.now() - g.last_activity) <= app.permanent_session_lifetime:    
        if curso and curso.idpreceptor == user.id:
            estudiantes = Estudiante.query.filter_by(idcurso=curso_id).all()
            estudiantes_info = []
            i=0
            while i<int(len(estudiantes)):
                asistencias = Asistencia.query.filter_by(idestudiante=estudiantes[i].id).all()
                asistencias_totales = len(asistencias)
                aula_presente = 0
                educacion_fisica_presente = 0
                aula_ausente_justificada = 0
                aula_ausente_injustificada = 0
                educacion_fisica_ausente_justificada = 0
                educacion_fisica_ausente_injustificada = 0
                total_inasistencias = 0
                j=0
                while j<int(len(asistencias)):
                    if int(asistencias[j].codigoclase) == 1:
                        if bool(asistencias[j].asistio):
                            aula_presente += 1
                        else:
                            total_inasistencias += 1
                            
                        if str(asistencias[j].justificacion) == 'si':
                            aula_ausente_justificada += 1
                        else:
                            aula_ausente_injustificada += 1
                            
                        
                    elif int(asistencias[j].codigoclase) == 2:
                        if bool(asistencias[j].asistio):
                            educacion_fisica_presente += 1
                        else:
                            total_inasistencias += 0.5
                        if str(asistencias[j].justificacion) == 'si':
                            educacion_fisica_ausente_justificada += 1
                        else:
                            educacion_fisica_ausente_injustificada += 1
                        
                        
                    j+=1
                estudiante_info = {
                    'nombre': estudiantes[i].nombre,
                    'apellido': estudiantes[i].apellido,
                    'asistencias_totales': asistencias_totales,
                    'aula_presente': aula_presente,
                    'educacion_fisica_presente': educacion_fisica_presente,
                    'aula_ausente_justificada': aula_ausente_justificada,
                    'aula_ausente_injustificada': aula_ausente_injustificada,
                    'educacion_fisica_ausente_justificada': educacion_fisica_ausente_justificada,
                    'educacion_fisica_ausente_injustificada': educacion_fisica_ausente_injustificada,
                    'total_inasistencias': total_inasistencias
                }
                
                estudiantes_info.append(estudiante_info)
                i+=1
            estudiantes_info_sorted = sorted(estudiantes_info, key=lambda x: x['nombre'])
            
            return render_template('detalles.html', curso=curso, estudiantes=estudiantes_info_sorted)
        
        return redirect(url_for('pagina_principal'))
    else:
        flash('Tu sesión ha expirado. Inicia sesión nuevamente.')
        return redirect(url_for('login'))



@app.route('/logout')
def logout():
    global Login
    global user
    if g.last_activity and (datetime.now() - g.last_activity) <= app.permanent_session_lifetime:        
        if Login:
            Login = False
            user = None
            return redirect(url_for('pagina_principal'))
        else: 
            return abort(401)
    else:
        flash('Tu sesión ha expirado. Inicia sesión nuevamente.')
        return redirect(url_for('login'))

    
if __name__ == '__main__':
    app.run(debug=True)