import os
from app import db
from flask import render_template, redirect, url_for, request, flash, send_from_directory, g, current_app, abort
from .import bp as blog
from .models import BlogPost
from app.blueprints.authentication.models import User
from flask_login import current_user, login_required
from .forms import ProfileForm, EditBlogPostForm, SearchForm
from werkzeug.utils import secure_filename
from datetime import datetime as dt



@blog.before_app_request
def before_app_request():
    if current_user.is_authenticated:
        current_user.lastseen = dt.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    return
    
    

@blog.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditBlogPostForm()
    post_id = request.args.get('post_id')
    if form.validate_on_submit():
        data = {
            'body': form.body.data,
            'user_id': current_user.id
        }
        post = BlogPost.query.get(post_id)
        post.from_dict(data)
        db.session.commit()
        flash('Post has updated successfully', 'info')
        return redirect(url_for('blog.edit', post_id=post_id))
    context = {
        'post': BlogPost.query.get(post_id),
        'form': form
    }
    return render_template('blog/single-post.html', **context)


@blog.route('/delete', methods=['GET'])
@login_required
def delete():
    post_id = request.args.get('post_id')
    post = BlogPost.query.get(post_id)
    post.remove()
    flash('Post has been deleted successfully.', 'warning')
    return redirect(url_for('main.index'))
    
@blog.route('/create', methods=['POST'])
@login_required
def create():
    data = {
        'body': request.form.get('post'),
        'user_id': current_user.id
    }
    post = BlogPost()
    post.from_dict(data)
    post.save()
    return redirect(url_for('main.index'))



@blog.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        try:
            data = {
                'first_name': form.first_name.data,
                'last_name': form.last_name.data,
                'email': form.email.data
            }
            u = User.query.get(current_user.id)
            u.from_dict(data)
            if form.password.data and form.confirm_password.data:
                u.hash_password(form.password.data)
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('blog.profile'))
        except Exception:
            flash('Profile was not updated. Please try again.', 'danger')
            return redirect(url_for('blog.profile'))
    context = {
        'posts': current_user.posts,
        'form': form
    }
    return render_template('blog/profile.html', **context)


@blog.route('/network', methods=['GET'])
@login_required
def network():
    context = {
        'users': [u for u in User.query.all() if current_user.id != u.id]
    }
    return render_template('blog/network.html', **context)

@blog.route('/follow', methods=['GET'])
@login_required
def follow():
    user_id = request.args.get('user_id')
    u = User.query.get(user_id)
    current_user.follow(u)
    db.session.commit()
    flash(f'You have followed {u.first_name} {u.last_name}', 'success')
    return redirect(url_for('blog.network'))

@blog.route('/unfollow', methods=['GET'])
@login_required
def unfollow():
    user_id = request.args.get('user_id')
    u = User.query.get(user_id)
    current_user.unfollow(u)
    db.session.commit()
    flash(f'You have unfollowed {u.first_name} {u.last_name}', 'warning')
    return redirect(url_for('blog.network'))



@blog.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('blog.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('blog.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('templates/layout.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)




@blog.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('blog.network'))
    page = request.args.get('page', 1, type=int)
    posts, total = BlogPost.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])

    next_url = url_for('blog.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('blog.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None 
    return render_template('search.html', title=('Search'), posts=posts, next_url=next_url, prev_url=prev_url)


def allowed_image(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):
    if filesize <= current_app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False

@blog.route("/upload-image", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":               
        if request.files:
            if not allowed_image_filesize(request.cookies.get("filesize")):
                flash("File exceeded maximum size!", 'danger')
                return redirect(request.url)      
            image = request.files['image']            
            if image.filename == "":
                flash("Please select a file.", 'danger')
                return redirect(request.url)
            
            if not allowed_image(image.filename):
                flash("That image extension is not allowed", 'danger')
                return redirect(request.url)
            else:
                filename = secure_filename(image.filename)           
                image.save(os.path.join(current_app.config["IMAGE_UPLOADS"], filename))
            flash('Your file has been uploaded!', 'primary')
            
            return redirect(request.url)

    return render_template("blog/upload.html")

@blog.route("/get-image/<image_name>")
def get_image(image_name):
    try:
        return send_from_directory(
            current_app.config['CLIENT_IMAGES'], filename=image_name, as_attachment=True )

    except FileNotFoundError:
        abort(404)

@blog.route("/get-csv/<filename>")
def get_csv(filename):
    try:
        return send_from_directory(
            current_app.config['CLIENT_OTHER'], filename=filename, as_attachment=True )

    except FileNotFoundError:
        abort(404)

    
    




# @blog.route('/upload_sample', methods=['GET', 'POST'])
# def upload_sample():
#     if request.method == 'POST':
#         flash('No File Part')
#         return redirect(request.url)

#     file = request.files.get('file')
#     if file.filename == '':
#         flash('No file was selected')
#         return redirect(request.url)

#     if file and allowed_files(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(BASE_PATH, 'DESKTOP/test', filename))
#         flash('File uploaded successfully')
#         return redirect(url_for('download'))
#     return render_template('upload.html')

# @blog.route('/download', methods=['GET'])
# def download():
#     return 'Download Page'

    

    




# @blog.route('/', methods=['GET', 'POST'])
# def allowed_file(filename):
#     return '.' in filename and \
#         filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# @blog.route('/upload_file', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('uploaded_file', filename=filename))
    

# @blog.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# @blog.route('/upload', methods=['GET', 'POST'])
# def upload():
#     context = {
               
#     }

#     return render_template(url_for('blog/upload.html', **context))

   






    









     
    










