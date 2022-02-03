from flask import Flask, render_template, url_for, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user,LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, DateTimeField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Server13m@localhost/sc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'contraseña'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return usuario.query.get(int(user_id))

class usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    nombre = db.Column(db.String(20), nullable=False)
    apellido = db.Column(db.String(20), nullable=False)
    email =db.Column(db.String(80), nullable=False, unique=True)
    contraseña = db.Column(db.String(512), nullable=False)

class evento(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    email_id = db.Column(db.String(80), primary_key=True,nullable=False)
    nombre_evento = db.Column(db.String(20), nullable=False)
    categoria = db.Column(db.String(20), nullable=False)
    lugar = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(20), nullable=False)
    fecha_inicio = db.Column(db.String(20), nullable=False)
    fecha_fin = db.Column(db.String(20), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)

class eventoform(FlaskForm):
    nombre_evento = StringField(validators=[InputRequired()], render_kw={"placeholder": "nombre_evento"})
    categoria = StringField(validators=[InputRequired()], render_kw={"placeholder": "categoria"})
    lugar = StringField(validators=[InputRequired()], render_kw={"placeholder": "lugar"})
    direccion = StringField(validators=[InputRequired()], render_kw={"placeholder": "direccion"})
    fecha_inicio = StringField(validators=[InputRequired()], render_kw={"placeholder": "fecha_incio"})
    fecha_fin = StringField(validators=[InputRequired()], render_kw={"placeholder": "fecha_fin"})
    tipo =  StringField(validators=[InputRequired()], render_kw={"placeholder": "tipo"})
    submit = SubmitField("Nuevo")



class registroform(FlaskForm):
    nombre = StringField(validators=[InputRequired()], render_kw={"placeholder": "nombre"})
    apellido = StringField(validators=[InputRequired()], render_kw={"placeholder": "apellido"})
    email = EmailField(validators=[InputRequired()], render_kw={"placeholder": "email"})
    contraseña = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "contraseña"})
    submit = SubmitField("Registro")\

    def validate_email(self, email):
        existing_user_email = usuario.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                "Este email se encuentra en uso")

class loginform(FlaskForm):
    email = EmailField(validators=[InputRequired()], render_kw={"placeholder": "email"})
    contraseña = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "contraseña"})
    submit = SubmitField("Inciciar sesión")\

class eliminarform(FlaskForm):
    id_evento = StringField(validators=[InputRequired()], render_kw={"placeholder": "Evento ID"})
    submit = SubmitField("Eliminar")

class editarform(FlaskForm):
    id_evento = StringField(validators=[InputRequired()], render_kw={"placeholder": "evento ID"})
    nombre_evento = StringField(validators=[InputRequired()], render_kw={"placeholder": "nombre_evento"})
    categoria = StringField(validators=[InputRequired()], render_kw={"placeholder": "categoria"})
    lugar = StringField(validators=[InputRequired()], render_kw={"placeholder": "lugar"})
    direccion = StringField(validators=[InputRequired()], render_kw={"placeholder": "direccion"})
    fecha_inicio = StringField(validators=[InputRequired()], render_kw={"placeholder": "fecha_incio"})
    fecha_fin = StringField(validators=[InputRequired()], render_kw={"placeholder": "fecha_fin"})
    tipo = StringField(validators=[InputRequired()], render_kw={"placeholder": "tipo"})
    submit = SubmitField("Editar")

@app.route('/')
def pagina_incio():
    return render_template("inicio.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginform()
    if form.validate_on_submit():
        try:
            user = usuario.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.contraseña, form.contraseña.data):
                login_user(user)
                return redirect(url_for('principal'))
            else:
                flash('Contraseña incorrecta')
        except Exception as e:
            flash('Inicio de sesión invalido')
    return render_template("login.html", form = form)

@app.route('/registro',methods=['GET', 'POST'])
def registro():
    form = registroform()
    if form.validate_on_submit():
        hash = generate_password_hash(form.contraseña.data)
        nuevo_usuario = usuario(nombre=form.nombre.data,
                                apellido=form.apellido.data,
                                email=form.email.data,
                                contraseña=hash)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("registro.html", form = form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def cerrar_sesion():
    logout_user()
    return redirect(url_for('login'))

@app.route('/principal', methods=['GET', 'POST'])
@login_required
def principal():
    eventos = evento.query.filter_by(email_id='{}'.format(current_user.email)).all()  #.filter(evento.email_id=='{}'.format(current_user.email)).all()
    return render_template("principal.html", eventos=eventos)
        #return render_template('principal.html', nombre_evento=ids) #.nombre_evento,
                           #categoria=consulta.categoria,
                           #lugar=consulta.lugar,
                           #direccion=consulta.direccion,
                           #fecha_inicio=consulta.fecha_inicio,
                           #fecha_fin=consulta.fecha_fin,s
                           #tipo=consulta.tipo,
                               #id=1)
    #else:
    #    return render_template('no_hay_eventos.html')

@app.route('/nuevo_evento', methods=['GET', 'POST'])
@login_required
def añadir_evento():
    form = eventoform()
    if form.is_submitted():
        nuevo_evento = evento(email_id= current_user.email,
                              nombre_evento=form.nombre_evento.data,
                              categoria=form.categoria.data,
                              lugar=form.lugar.data,
                              direccion=form.direccion.data,
                              fecha_inicio=form.fecha_inicio.data,
                              fecha_fin=form.fecha_fin.data,
                              tipo=form.tipo.data)
        db.session.add(nuevo_evento)
        db.session.commit()
        return redirect(url_for('principal'))
    return render_template('nuevo_evento.html', form=form, usuario= current_user.email)

@app.route('/principal/eliminar_evento', methods=['GET', 'POST'])
@login_required
def eliminar_evento():
    form = eliminarform()
    if form.is_submitted():
        eliminar = evento.query.filter_by(id=form.id_evento.data).one()
        db.session.delete(eliminar)
        db.session.commit()
        return redirect(url_for('principal'))
    else:
       return render_template('eliminar_evento.html', form=form)


@app.route('/principal/editar_evento', methods=['GET', 'POST'])
@login_required
def editar_evento():
    form = editarform()
    if form.is_submitted():
        seleccionar_evento = evento.query.filter_by(id=form.id_evento.data).one()
        seleccionar_evento.nombre_evento = form.nombre_evento.data
        seleccionar_evento.categoria = form.categoria.data
        seleccionar_evento.lugar = form.lugar.data
        seleccionar_evento.direccion = form.direccion.data
        seleccionar_evento.fecha_inicio = form.fecha_inicio.data
        seleccionar_evento.fecha_fin = form.fecha_fin.data
        seleccionar_evento.tipo = form.tipo.data
        #db.session.commit()
        return redirect(url_for('editar', val = seleccionar_evento.id))
    else:
       return render_template('seleccion_evento.html', form=form)


@app.route('/principal/<val>/editar', methods=['GET', 'POST'])
@login_required
def editar(val):
    form = editarform()
    seleccionar_evento = evento.query.filter_by(id='{}'.format(val)).one()
    if form.is_submitted():
        seleccionar_evento.nombre_evento = form.nombre_evento.data
        seleccionar_evento.categoria = form.categoria.data
        seleccionar_evento.lugar = form.lugar.data
        seleccionar_evento.direccion = form.direccion.data
        seleccionar_evento.fecha_inicio = form.fecha_inicio.data
        seleccionar_evento.fecha_fin = form.fecha_fin.data
        seleccionar_evento.tipo = form.tipo.data
        db.session.commit()
        return redirect(url_for('principal'))
    return render_template('edicion.html', form=form,campos = seleccionar_evento)


if __name__ == '__main__':
    app.run(debug=True)
