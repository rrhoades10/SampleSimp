from .import bp as auth
from flask import render_template, redirect, url_for, request, flash
from .models import User
from flask_login import login_user, logout_user, current_user
from .forms import RegistrationForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        email = form_data.get('email')
        u = User.query.filter_by(email=email).first()
        if u is not None and u.check_hashed_password(form_data.get('password')):
            login_user(u)
            flash(f'{u.email} has logged in successfully', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('There was an error logging you in. Please try again.', 'warning')
            return redirect(url_for('authentication.login'))
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        data = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
        }
        try:
            u = User()
            u.from_dict(data)
            u.hash_password(form.password.data)
            u.save()
            flash('You have registered successfully.', 'primary')
            return redirect(url_for('authentication.login'))
        except Exception as error:
            flash('There was a problem registering you as a new user.', 'danger')
            return redirect(url_for('authentication.register'))
    context = {
        'form': form
    }
    return render_template('auth/register.html', **context)


@auth.route('/logout')
def logout():
    if current_user is not None:
        logout_user()
        return redirect(url_for('authentication.login'))