from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from verteastur.auth import login_required
from verteastur.db import get_db

bp = Blueprint('ppal', __name__)

# Recopilar avistamientos de la BD
@bp.route('/')
def index():
    db = get_db()
    vertederos = db.execute(
        'SELECT p.id, tipo, descripcion, fecha, usuario_id, username'
        ' FROM vertederos p JOIN usuario u ON p.usuario_id = u.id'
        ' ORDER BY fecha DESC'
    ).fetchall()
    return render_template('ppal/index.html', vertederos=vertederos)


# Crear nuevo avistamiento
@bp.route('/nuevo', methods=('GET', 'POST'))
@login_required
def nuevo():
    if request.method == 'POST':
        tipo = request.form['tipo']
        descripcion = request.form['descripcion']
        error = None

        if not tipo:
            error = '¡Escribe el tipo de vertedero!'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO vertederos (tipo, descripcion, usuario_id)'
                ' VALUES (?, ?, ?)',
                (tipo, descripcion, g.usuario['id'])
            )
            db.commit()
            return redirect(url_for('ppal.index'))

    return render_template('ppal/nuevo.html')


# Comprobar la existencia de un registro
def get_vertedero(id, check_usuario=True):
    vertedero = get_db().execute(
        'SELECT p.id, tipo, descripcion, fecha, usuario_id, username'
        ' FROM vertederos p JOIN usuario u ON p.usuario_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if vertedero is None:
        abort(404, f"El vertedero {id} no existe.")

    if check_usuario and vertedero['usuario_id'] != g.usuario['id']:
        abort(403)

    return vertedero


# Editar un avistamiento
@bp.route('/<int:id>/editar', methods=('GET', 'POST'))
@login_required
def editar(id):
    vertedero = get_vertedero(id)

    if request.method == 'POST':
        tipo = request.form['tipo']
        descripcion = request.form['descripcion']
        error = None

        if not tipo:
            error = '¡Escribe el tipo de vertedero!'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE vertederos SET tipo = ?, descripcion = ?'
                ' WHERE id = ?',
                (tipo, descripcion, id)
            )
            db.commit()
            return redirect(url_for('ppal.index'))

    return render_template('ppal/editar.html', vertedero=vertedero)


# Eliminar un registro
@bp.route('/<int:id>/eliminar', methods=('POST',))
@login_required
def eliminar(id):
    get_vertedero(id)
    db = get_db()
    db.execute('DELETE FROM vertederos WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('ppal.index'))