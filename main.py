from flask import *
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, NewList, TaskForm, RegisterForm
from datetime import datetime

app = Flask(__name__)
Bootstrap(app)
app.secret_key = "yolo"

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    lists = relationship("List", back_populates="author")


class List(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship('User', back_populates='lists')
    title = db.Column(db.String(250))
    tasks = relationship('Task', back_populates='parent_list')


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_list = relationship("List", back_populates="tasks")
    tasks = db.Column(db.String(250))
    date_tbc = db.Column(db.String(10))
    complete = db.Column(db.Integer)
    overdue = db.Column(db.Integer)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = request.form['email']
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('That email is not linked to a account. Please try again.')
            return redirect(url_for('login'))

        elif not check_password_hash(user.password, password):
            flash('Incorrect password, please try again.')

        elif check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html', form=form, current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if form.password.data != form.confirm_password.data:
            flash('Passwords Do Not Match. Please Try again.')
            return redirect(url_for('register'))

        if User.query.filter_by(email=form.email.data).first():
            flash('Account already registered to that email.')
            return redirect(url_for('login'))

        else:

            hash_and_salted_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)

            new_user = User(email=request.form['email'],
                            password=hash_and_salted_password,
                            name=request.form['name']
                            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            return redirect(url_for('home'))

    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home')
def home():
    lists = List.query.filter_by(author_id=current_user.id)
    return render_template('home.html', lists=lists)


@app.route('/create_list', methods=['GET', 'POST'])
def create_list():
    form = NewList()
    if form.validate_on_submit():
        new_list = List(title=str(request.form['title']),
                        author_id=current_user.id)
        db.session.add(new_list)
        db.session.commit()

        return redirect(url_for('tasks', list_title=new_list.title, list_id=new_list.id))

    return render_template('new_list.html', form=form)


@app.route('/<list_title>/<list_id>/tasks', methods=['GET', 'POST'])
def tasks(list_title, list_id):
    form = TaskForm()
    current_day = datetime.now()
    list_tasks = Task.query.filter_by(list_id=int(list_id)).all()

    for task in list_tasks:
        date_converted = datetime.strptime(task.date_tbc, '%d/%m/%y')
        if current_day > date_converted:
            task.overdue = 1

    if request.method == 'POST':

        new_task = Task(list_id=int(list_id),
                        author_id=current_user.id,
                        tasks=request.form['task'],
                        date_tbc=request.form['date_tbc'],
                        complete=0,
                        overdue=0)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('tasks', list_id=list_id, list_title=list_title))

    return render_template('tasks.html', form=form, list_tasks=list_tasks, list_id=list_id, list_title=list_title)


@app.route('/delete/<list_id>')
def delete_list(list_id):
    list_to_delete = List.query.filter_by(id=list_id).first()
    db.session.delete(list_to_delete)
    db.session.commit()
    tasks_to_delete = Task.query.filter_by(list_id=list_id).all()
    for task in tasks_to_delete:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/complete/<list_id>/<list_title>/<task_id>')
def task_complete(task_id, list_id, list_title):
    task_completed = Task.query.filter_by(id=task_id).first()
    task_completed.complete = 1
    db.session.commit()
    return redirect(url_for('tasks', list_id=list_id, list_title=list_title))


if __name__ == "__main__":
    app.run(debug=True)
