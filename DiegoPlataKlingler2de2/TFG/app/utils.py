from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'danger')
            return redirect(url_for('usuarios.login'))
        return view_func(*args, **kwargs)
    return wrapped_view
