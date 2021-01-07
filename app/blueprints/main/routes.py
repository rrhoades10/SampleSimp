from flask import render_template, request, redirect, url_for, flash
from .import bp as main
from app.blueprints.blog.models import BlogPost
from flask_login import login_required, current_user
from .email import send_contact_email




@main.route('/', methods=['GET'])
@login_required
def index():
    context = {
        'posts': current_user.followed_posts()
    }
    return render_template('main/index.html', **context)

@main.route('/about', methods=['GET'])
def about():
    context = {}
    return render_template('main/about.html', **context)

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            form_data = request.form.to_dict()
            send_contact_email(form_data)
            flash('Contact form inquiry sent successfully.', 'success')
            return redirect(url_for('main.contact'))
        except Exception as error:
            flash('There was a problem sending your contact form inquiry. Please try again.', 'danger')
            print(error)
            return redirect(url_for('main.contact'))
    context = {}
    return render_template('main/contact.html', **context)