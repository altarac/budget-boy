from flask import Flask, render_template, url_for, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, RadioField, TextField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.fields.html5 import DateField


app = Flask(__name__)
app.config['SECRET_KEY'] = '14c74a1f98cb8dd7c8a2f68de80c2f78'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDatabase.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# database below-------------

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(6), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"

class Budgets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    users = db.Column(db.String(40), unique=False, nullable=False)
    code = db.Column(db.String(20), unique=False, nullable=False)
    initial_amount = db.Column(db.Integer, nullable=False)
    amount_spent = db.Column(db.Integer, nullable=True)
    # current_amount = db.Column(db.Integer, nullable=False)


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



class UpdateBudgetForm(FlaskForm):


    code = SelectField(u'Budget codes')
    guests_present = TextField('People released', validators=[DataRequired(), Length(max=2000)])
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


    # user1 = User(username='Sam', password='12345')
    # user2 = User(username='bob', password='33333')
    # b = Budgets(users = 'Sam', code= '12345', initial_amount='13000', amount_spent = '1000')
    # b2 = Budgets(users = 'Sam', code= '55555', initial_amount='1200', amount_spent = '0')
    # b3 = Budgets(users = 'bob', code= '55555', initial_amount='1200', amount_spent = '0')
    # db.session.add(b)
    # db.session.add(b2)
    # db.session.add(b3)
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
    b = Budgets.query.filter_by(users=f'{u}')
    form.code.choices = [(g.code, g.code) for g in b]

    if form.validate_on_submit():
        bb = Budgets.query.filter_by(users=f'{u}').filter_by(code=f'{str(form.code.data)}')[0]
        bb.amount_spent = bb.amount_spent + len(form.guests_present.data.split(','))*int(form.duration_of_event.data)

        e = Event(guests_present=form.guests_present.data, budget_code=form.code.data, duration_of_event=form.duration_of_event.data, amount_spent_on_release=len(form.guests_present.data.split(','))*int(form.duration_of_event.data), date_of_event=form.date_of_event.data, users = u)
        db.session.add(e)
        db.session.commit()
        # return redirect(f'profile/{u}')

    events = Event.query.filter_by(users=f'{u}')

    # code = b.code
    # initial_amount = b.initial_amount
    # spent = b.amount_spent
    # balance = initial_amount-spent

    return render_template('profile.html', u = u, b = b, events = events)


@app.route('/profile/<string:name>/update', methods=['POST', 'GET'])
def profile2(name):
    form = UpdateBudgetForm()

    u = name
    b = Budgets.query.filter_by(users=f'{u}')

    form.code.choices = [(g.code, g.code) for g in b]
    # code = b.code
    # initial_amount = b.initial_amount
    # spent = b.amount_spent
    # balance = initial_amount-spent

    return render_template('profile2.html', u = u, b= b, form =form)




@app.route('/master', methods=['POST', 'GET'])
def master():
    if(session['key'] == False):
        return redirect(url_for('index'))

    people = User.query.all()
    form = UpdateUserForm()


    return render_template('master.html', people = people, form = form)



@app.route('/master/profile/<string:name>', methods=['POST', 'GET'])
def masterprofile(name):
    u = name
    # form = updateAndNew()
    form = MasterBudgetForm()
    form2 = addToBudgetForm()
    form3 = d()
    b = Budgets.query.filter_by(users=f'{u}')
    events = Event.query.filter_by(users=f'{u}')
    cs = []
    for i in b:
        cs.append(i.code)

    if form.validate_on_submit():
        bb = Budgets.query.filter_by(code=f'{form.code.data}')[0]
        bb.initial_amount = int(form.initial_amount.data)
        bb.amount_spent = int(form.amount_spent.data)
        db.session.commit()

        return render_template('masterprofile.html', u = u, b = b, events = events, form = form, form2 = form2, form3 = form3)

    if form2.is_submitted():
        new_budget = Budgets(code = form2.code.data, users = u, initial_amount = int(form2.initial_amount.data), amount_spent = int(form2.amount_spent.data))
        db.session.add(new_budget)
        db.session.commit()

        return render_template('masterprofile.html', u = u, b = b, events = events, form = form, form2 = form2, form3 = form3)


    if form3.is_submitted():
        budge = Budgets.query.filter_by(users = f'{u}').filter_by(code = f'{form3.code3.data}').first()
        db.session.delete(budge)
        db.session.commit()

        return render_template('masterprofile.html', u = u, b = b, events = events, form = form, form2 =form2, form3 = form3)

    return render_template('masterprofile.html', u = u, b = b, events = events, form = form, form2 =form2, form3 = form3, cs = cs)


@app.route('/master3/profile/<string:name>', methods=['POST', 'GET'])
def masterprofile3(name):
    u = name
    # form = updateAndNew()
    form = MasterBudgetForm()
    form2 = addToBudgetForm()
    form3 = d()
    b = Budgets.query.filter_by(users=f'{u}')
    events = Event.query.filter_by(users=f'{u}')




    if form3.is_submitted():
        budge = Budgets.query.filter_by(users = f'{u}').filter_by(code = f'{form3.code3.data}').first()
        db.session.delete(budge)
        db.session.commit()

        return render_template('masterprofile.html', u = u, b = b, events = events, form = form, form2 =form2, form3 = form3)

    return render_template('masterprofile.html', u = u, b = b, events = events, form = form, form2 =form2, form3 = form3)






@app.route('/print')
def printing():
    print('sample printing')


    return render_template('print.html')







app.debug=True
app.run(use_reloader=True, port='8080')
