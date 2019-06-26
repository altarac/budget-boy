from flask import Flask, render_template, url_for, flash, redirect, session, send_from_directory, make_response, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, RadioField, TextField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.fields.html5 import DateField
from docx import Document
from docx.shared import Inches
import datetime
import pandas as pd
import sqlite3




# UPLOAD_FOLDER = '/downloads/'

app = Flask(__name__)
app.config['SECRET_KEY'] = '14c74a1f98cb8dd7c8a2f68de80c2f78'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDatabase.db'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# database below-------------

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(6), nullable=False)
    budgets_access = db.Column(db.String(100), unique=False, nullable=True)


    def __repr__(self):
        return f"User('{self.username}')"

class Budgets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # users = db.Column(db.String(40), unique=False, nullable=False)
    code = db.Column(db.String(20), unique=False, nullable=False)
    initial_amount = db.Column(db.Integer, nullable=False)
    amount_spent = db.Column(db.Integer, nullable=True)



    def __repr__(self):
        return f"User('{self.code}')"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    users = db.Column(db.String(40), unique=False, nullable=False)
    guests_present = db.Column(db.Text, unique=False, nullable=False)
    budget_code = db.Column(db.String(20), unique=False, nullable=False)
    duration_of_event = db.Column(db.Integer, nullable=False)
    amount_spent_on_release = db.Column(db.Integer, nullable=True)
    date_of_event = db.Column(db.DateTime, nullable=False)
    is_processed = db.Column(db.Integer, nullable=True)

    # current_amount = db.Column(db.Integer, nullable=False)


    def __repr__(self):
        return f"User('{self.budget_code}')"




db.create_all()


# add db data below-------------


# user1 = User(username='Sam')
#
# b = Budgets(users = 'Sam', code= '54321', initial_amount='10000', amount_spent = '100')

# db.session.add(user1)
# db.session.add(b)
# db.session.commit()


# flask-forms below-------------

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    # remember = BooleanField('Remember me')
    submit = SubmitField('Login')


class addToBudgetForm(FlaskForm):
    code = StringField(u'Budget code')
    initial_amount = IntegerField('Initial amount')
    amount_spent = IntegerField('Amount already spent')
    submit = SubmitField('Create')


class d(FlaskForm):
    code3 = StringField(u'Budget code')
    submit = SubmitField('Delete')

class p(FlaskForm):
    event_id = StringField('Event id')
    submit = SubmitField('Print')



class UpdateBudgetForm(FlaskForm):


    code = SelectField(u'Budget codes')
    guests_present = TextField('People released', validators=[DataRequired(), Length(max=2000)])
    school = TextField('School', validators=[DataRequired(), Length(max=2000)])
    # spent = IntegerField('Amount Used', validators=[DataRequired()])
    duration_of_event = RadioField('Duration of Release', choices=[('140', 'Half day'), ('250', 'Full day')], validators=[DataRequired()])
    submit = SubmitField('Submit')
    date_of_event = DateField('Date of event (Y-M-D)', format='%Y-%m-%d', id='datepicker')


class UpdateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])

    submit = SubmitField('Submit')


class MasterBudgetForm(FlaskForm):
    code = StringField('Budget code', validators=[DataRequired(), Length(min=2, max=20)])
    initial_amount = IntegerField('Initial amount', validators=[DataRequired()])
    amount_spent = IntegerField('Spent', validators=[DataRequired()])

    submit = SubmitField('Update')

# class updateAndNew(FlaskForm):
#     new = wtforms.FormFields(addToBudgetForm)
#     update = wtforms.FormFields(MasterBudgetForm)

# routes below-------------


@app.route('/', methods=['POST', 'GET'])
def index():
    # user = User.query.filter_by(username='Sam')[0]
    # user.password = '12345'


    # user1 = User(username='Sam', password='12345', budgets_access='55555, 12345')
    # user2 = User(username='bob', password='33333', budgets_access='55555')
    # b1 = Budgets(code= '12345', initial_amount='13000', amount_spent = '1000')
    # b2 = Budgets(code= '55555', initial_amount='1200', amount_spent = '10')
    #
    # db.session.add(b1)
    # db.session.add(b2)
    # db.session.add(user1)
    # db.session.add(user2)
    # db.session.commit()

    form = LoginForm()
    if form.validate_on_submit():
        users = User.query.filter_by(username=f'{form.username.data}', password=f'{form.password.data}').count()
        # flash(f'Logged in as {form.username.data}', category='success')
        if(users > 0 ):
            users = User.query.filter_by(username=f'{form.username.data}', password=f'{form.password.data}').first()
            masteruser = User.query.filter_by(username='Sam', password='12345').first()
            if(masteruser == users):
                session['key']=True
            else:
                session['key']=False
            return redirect(f'profile/{form.username.data}')
        else:
            session['key']=False
            return render_template('index.html', form = form)

    return render_template('index.html', form = form)




@app.route('/profile/<string:name>', methods=['POST', 'GET'])
def profile(name):
    u = name
    form = UpdateBudgetForm()
    tables = []
    x = User.query.filter_by(username=f'{u}')[0]
    codes = x.budgets_access.split(',')
    for c in codes:
        b = Budgets.query.filter_by(code=int(c)).first()
        tables.append(b)

    form.code.choices = [(int(g), int(g)) for g in codes]

    if(len(codes) <= 4):
        b_count = len(codes)
    else:
        b_count = 4

    if form.is_submitted():
        bb = Budgets.query.filter_by(code=f'{str(form.code.data)}')[0]
        bb.amount_spent = bb.amount_spent + len(form.guests_present.data.split(','))*int(form.duration_of_event.data)

        e = Event(guests_present=form.guests_present.data, budget_code=form.code.data, duration_of_event=form.duration_of_event.data, amount_spent_on_release=len(form.guests_present.data.split(','))*int(form.duration_of_event.data), date_of_event=form.date_of_event.data, users = u, is_processed = 0)
        db.session.add(e)
        db.session.commit()
        # return redirect(f'profile/{u}')

    events = Event.query.filter_by(users=f'{u}')

    # code = b.code
    # initial_amount = b.initial_amount
    # spent = b.amount_spent
    # balance = initial_amount-spent

    return render_template('profile.html', u = u, tables = tables, events = events, b_count = b_count, x = codes)


@app.route('/profile/<string:name>/update', methods=['POST', 'GET'])
def profile2(name):
    # form = UpdateBudgetForm()
    # u = name
    # b = Budgets.query.filter_by(users=f'{u}')
    # .filter_by('budgets_access')
    # b = User.query.filter_by(f'{u}')
    u = name
    form = UpdateBudgetForm()
    tables = []
    x = User.query.filter_by(username=f'{u}')[0]
    codes = x.budgets_access.split(',')
    for c in codes:
        b = Budgets.query.filter_by(code=int(c)).first()
        tables.append(b)

    form.code.choices = [(int(g), int(g)) for g in codes]
    # code = b.code
    # initial_amount = b.initial_amount
    # spent = b.amount_spent
    # balance = initial_amount-spent

    return render_template('profile2.html', u = u, b= tables, form =form)




@app.route('/master', methods=['POST', 'GET'])
def master():
    if(session['key'] == False):
        return redirect(url_for('index'))

    cnx = sqlite3.connect('myDatabase.db')


    df = pd.read_sql_query("SELECT * FROM Event", cnx)
    df2 = pd.read_sql_query("SELECT * FROM Event", cnx).to_html()


    people = User.query.all()
    res = []

    budget_codes = Budgets.query.all()


    for b in budget_codes:
        e = Event.query.filter_by(budget_code=b.code).first()
        if e:
            res.append(e)



    return render_template('master.html', people = people, res = res, df = df, df2 = df2)



@app.route('/master/profile/<string:name>', methods=['POST', 'GET'])
def masterprofile(name):
    u = name
    # form = updateAndNew()
    form = MasterBudgetForm()
    form2 = addToBudgetForm()
    form3 = d()
    printform = p()
    tables = []
    x = User.query.filter_by(username=f'{u}')[0]
    codes = x.budgets_access.split(',')
    for c in codes:
        b = Budgets.query.filter_by(code=int(c)).first()
        tables.append(b)
    events = Event.query.filter_by(users=f'{u}').order_by(desc(Event.budget_code))
    cs = codes


    y =Event.query.filter_by(users=f'{u}').order_by(desc(Event.budget_code)).filter_by(is_processed='0')

    events2 = y


    if form.validate_on_submit():
        bb = Budgets.query.filter_by(code=f'{form.code.data}')[0]
        bb.initial_amount = int(form.initial_amount.data)
        bb.amount_spent = int(form.amount_spent.data)
        db.session.commit()

        return render_template('masterprofile.html', u = u, b = tables, events = events, form = form, form2 = form2, form3 = form3, printform = printform, events2 = events2)

    if form2.is_submitted():
        new_budget = Budgets(code = form2.code.data, initial_amount = int(form2.initial_amount.data), amount_spent = int(form2.amount_spent.data))
        db.session.add(new_budget)
        db.session.commit()

        return render_template('masterprofile.html', u = u, b = tables, events = events, form = form, form2 = form2, form3 = form3, printform = printform, events2 = events2)


    if form3.is_submitted():
        xx = User.query.filter_by(username=f'{u}')[0]
        codes = x.budgets_access.split(',')
        codes = codes.pop(str(codes.index(str(form3.code3.data))))
        uu = User.query.filter_by(username=f'{u}')[0]
        uu.budgets_access = codes
        db.session.commit()

        return render_template('masterprofile.html', u = u, b = b, events = events, form = form, form2 =form2, form3 = form3, printform = printform, events2 = events2)

    if printform.is_submitted():

        db.session.commit()

        return render_template('masterprofile.html', u = u, b = b, events = events, form = form, form2 =form2, form3 = form3, printform = printform, events2 = events2)

    return render_template('masterprofile.html', u = u, b = tables, events = events, form = form, form2 =form2, form3 = form3, cs = cs, printform = printform, events2 = events2)


@app.route('/master3/profile/<string:name>', methods=['POST', 'GET'])
def masterprofile3(name):
    u = name
    # form = updateAndNew()
    form = MasterBudgetForm()
    form2 = addToBudgetForm()
    form3 = d()

    tables = []
    x = User.query.filter_by(username=f'{u}')[0]
    codes = x.budgets_access.split(',')
    for c in codes:
        b = Budgets.query.filter_by(code=int(c)).first()
        tables.append(b)
    # b = Budgets.query.filter_by(users=f'{u}')
    events = Event.query.filter_by(users=f'{u}')




    if form3.is_submitted():

        codes = codes.pop(codes.index(str(form3.code3.data)))
        uu = User.query.filter_by(username=f'{u}')[0]
        uu.budgets_access = codes
        db.session.commit()

        return render_template('masterprofile.html', u = u, b = tables, events = events, form = form, form2 =form2, form3 = form3)

    return render_template('masterprofile.html', u = u, b = tables, events = events, form = form, form2 = form2, form3 = form3)






@app.route('/print/<string:name>', methods=['GET','POST'])
def printing(name):
    u = name

    if(session['key'] == False):
        return redirect(url_for('index'))

    people = User.query.all()
    res = []

    budget_codes = Budgets.query.all()


    for b in budget_codes:
        ev = Event.query.filter_by(budget_code=b.code).first()
        if ev:
            res.append(ev)

    e = Event.query.filter_by(users=f'{u}').all()
    for i in e:
        i.is_processed = 1
    db.session.commit()

    return redirect(url_for('master'))







app.debug=True
app.run(use_reloader=True, port='8081')
