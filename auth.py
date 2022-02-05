import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from 'verteastur.db' import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Registro de usuarios
@bp.route('/registro', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Indica un nombre de usuario.'
        elif not password:
            error = 'Indica una contraseña.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO usuario (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"El usuario {username} ya está registrado."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/registro.html')


# Inicio de sesión
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM usuario WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'El usuario no existe.'
        elif not check_password_hash(user['password'], password):
            error = 'Contraseña incorrecta.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# Cargar la sesión del usuario
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM usuario WHERE id = ?', (user_id,)
        ).fetchone()


# Cerrar sesión
@bp.route('/salir')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Requerir autenticación
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view