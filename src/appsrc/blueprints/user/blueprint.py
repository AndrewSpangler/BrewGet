import os
import random
import string
from flask import (
    Blueprint,
    request,
    session,
    render_template,
    redirect,
    url_for,
    flash
)
from flask_login import login_user, current_user, logout_user
from werkzeug.security import generate_password_hash
from .models import User, PermissionsLevel, PermissionsMap, init_db
from .forms import (
    PermissionForm,
    LoginForm,
    RegisterForm,
    ChangePasswordForm,
    GenerateUserForm
)
from ...main import app, db
from ...modules.parsing import make_table_button, pretty_date, localize
from ...modules.datatables import create_table_page

blueprint = Blueprint(
    'user',
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__),"static"),
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
)
blueprint.init_db = init_db

@blueprint.route("/")
def index():
    """Home page, redirects to dashboard or login in not signed in"""
    return redirect(url_for("user.dashboard"))

@blueprint.route("/login", methods=["GET", "POST"])
def login():
    if not User.query.get(1):
        return redirect(url_for("user.register"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email.lower()).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully", 'success')
            return redirect(url_for("user.dashboard"))
        else:
            flash("Failed to log in")
            form.email.errors.append("Invalid email or password")
    return render_template("login.html", form=form)

@blueprint.route('/register', methods=['GET', 'POST'])
def register(): # First time setup login
    if User.query.count() > 0:
        flash('Owner registration is not available', 'error')
        return redirect(url_for('user.login'))
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            email=form.email.data,
            permission_integer=PermissionsLevel.OWNER
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash(f'Account created for {form.email.data}!', 'success')
        return redirect(url_for('user.dashboard'))
    else:
        try:
            for e in form.errors:
                try:
                    flash(f'{e} - {form.errors[e]}')
                except:
                    pass
        except:
            pass
    return render_template('register.html', title='Register', form=form)


@blueprint.route('/setup', methods=['GET', 'POST'])
@app.permission_required(PermissionsLevel.OWNER)
def setup():    
    return redirect(url_for("user.dashboard"))


@blueprint.route('/generate', methods=['GET', 'POST'])
@app.permission_required(PermissionsLevel.ADMIN)
def generate():    
    form = GenerateUserForm()
    if form.validate_on_submit():
        email = form.email.data
        if not User.query.filter_by(email=email).first():
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            hashed_password = generate_password_hash(password)
            new_user = User(
                email=email,
                password=hashed_password,
                must_change_password=True,
                permission_integer=PermissionsLevel.USER
            )
            db.session.add(new_user)
            db.session.commit()
            flash(f"""
Account created successfully.<br>
Username: {email}<br>
Password: {password}<br>
            """.strip())
        else:
            flash('Email already exists')
            return render_template('generate.html', form=form)
        return redirect(url_for('user.users'))
    else:
        return render_template('generate.html', form=form)

@blueprint.route('/change_password', methods=['GET', 'POST'])
@app.permission_required(PermissionsLevel.EVERYONE) # Everyone can access
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            current_user.must_change_password = False
            db.session.commit()
            flash('Password changed successfully', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Incorrect current password', 'error')
    return render_template('change_password.html', form=form)

@blueprint.route('/users')
@app.permission_required(PermissionsLevel.ADMIN)
def users():
    rows = [
        (
            u.email,
            PermissionsMap[u.permission_integer],
            (
                make_table_button(
                    "Edit Role",
                    (('user.edit_user_permissions',),dict(user_id=u.id)),
                    btn_type="primary",
                    classes=["bi", "bi-pencil"],
                ) + make_table_button(
                    "Delete User",
                    (('user.delete_user',),dict(user_id=u.id)),
                    btn_type="danger",
                    classes=["bi", "bi-trash"],
                )
            )
        )
        for u in User.query.all()
    ]
    add_button = make_table_button(
        "New User",
        (("user.generate", ),{}),
        classes=["bi", "bi-plus"]
    )
    return create_table_page(
        "users",
        title="Users Page",
        columns=["Email", "Role", "Actions"],
        rows=rows,
        header_elements=[add_button]
    )

@blueprint.route('/delete_user/<int:user_id>', methods=['POST'])
@app.permission_required(PermissionsLevel.ADMIN)
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('user.users'))
    if user.id == current_user.id:
        flash("Can't delete own user.", 'error')
        return redirect(url_for('user.users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('user.users'))

@blueprint.route('/edit_user_permissions/<int:user_id>', methods=['GET', 'POST'])
@app.permission_required(PermissionsLevel.ADMIN)
def edit_user_permissions(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('user.users'))
    if user.id == current_user.id:
        flash("Can't edit own user.", 'error')
        return redirect(url_for('user.users'))
    if (form := PermissionForm()).validate_on_submit():
        selected_permission = form.permission.data
        try:
            selected_permission = int(selected_permission)
            if selected_permission == PermissionsLevel.OWNER:
                flash(err:="Cannot set permission level to owner", 'error')
                raise ValueError(err)
            user.permission_integer = int(selected_permission)

            db.session.commit()
            flash('User updated successfully.', 'success')
            return redirect(url_for("user.users"))
        except Exception as e:
            flash(f'Failed to update user permissions. {e}', 'error')

    return render_template('change_permissions.html', form=form, user=user)

@blueprint.route('/dashboard')
@app.permission_required(PermissionsLevel.USER)
def dashboard():
    return render_template(
        'dashboard.html',
        tabs=app.config["DASHBOARD_TABS"]
    )


@blueprint.route('/background_tasks', methods=["GET", "POST"])
@app.permission_required(PermissionsLevel.ADMIN)
def background_tasks():
    url_args = request.args.to_dict()
    toggle = url_args.get("toggle")
    run_now = url_args.get("run_now")
    task_name = url_args.get("task")
    if (toggle or run_now):
        if not task_name in app.task_manager.tasks:
            flash("Task not found", "danger")
            return redirect(url_for("user.background_tasks"))
        task = app.task_manager.tasks[task_name]

    if toggle:
        task.enabled = not task.enabled
        flash(f"Task {task.name} {'Enabled' if task.enabled else 'Disabled'}", "success")
        return redirect(url_for("user.background_tasks"))
    elif run_now:
        task.trigger()
        if task.running:
            flash(f"Task {task.name} already running", "danger")
            return redirect(url_for("user.background_tasks"))
        flash(f"Task {task.name} Triggered successfully", "success")
        return redirect(url_for("user.background_tasks"))
                
    rows = [
        (
            k,
            v.interval,
            make_table_button(
                " "+str(v.enabled),
                (('user.background_tasks',),dict(task=k, toggle=True)),
                btn_type="primary",
                classes=["bi", "bi-toggle-"+("on" if v.enabled else "off")],
            ),
            v.running,
            pretty_date(localize(v.last_run)),
            pretty_date(v.job.next_run_time),
            make_table_button(
                " Trigger Task Run",
                (('user.background_tasks',),dict(task=k, run_now=True)),
                btn_type="primary",
                classes=["bi", "bi-play-fill"],
            ),
        ) for k,v in app.task_manager.tasks.items()
    ]
    return create_table_page(
        "background_tasks",
        title="Background Tasks",
        columns=["Task", "Frequency (Minutes)", "Enabled", "Running", "Last Run", "Next Run", "Actions"],
        rows=rows,
    )

@blueprint.route('/logout')
@app.permission_required(PermissionsLevel.ADMIN)
def logout():
    logout_user()
    return redirect(url_for('user.login'))
