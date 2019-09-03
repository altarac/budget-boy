from flask import Flask, render_template, url_for, flash, redirect, session, send_from_directory, make_response, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, RadioField, TextField, SelectField, DateField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.fields.html5 import DateField
from docx import Document
from docx.shared import Inches
import datetime
import numpy as np
import sqlite3
import calendar
import smtplib
import hashlib



# UPLOAD_FOLDER = '/downloads/'

app = Flask(__name__)
app.config['SECRET_KEY'] = '14c74a1f98cb8dd7c8a2f68de80c2f78'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDatabase.db'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.template_filter()
def currencyFormat(value):
    value = float(value)
    return "${:,.2f}".format(value)

# database below-------------

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(6), nullable=False)
    budgets_access = db.Column(db.String(100), unique=False, nullable=True)
    super_user = db.Column(db.Integer, unique=False, nullable=True, default=0)


    def __repr__(self):
        return f"User('{self.username}')"

class Budgets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # users = db.Column(db.String(40), unique=False, nullable=False)
    code = db.Column(db.String(20), unique=False, nullable=False)
    description = db.Column(db.String(120), unique=False, nullable=True)
    project_name = db.Column(db.String(100), unique=False, nullable=True)
    initial_amount = db.Column(db.Float, nullable=False)
    amount_spent = db.Column(db.Float, nullable=True)



    def __repr__(self):
        return f"User('{self.code}')"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    users = db.Column(db.String(40), unique=False, nullable=False)
    guests_present = db.Column(db.Text, unique=False, nullable=False)
    school = db.Column(db.Text, unique=False, nullable=False)
    budget_code = db.Column(db.String(20), unique=False, nullable=False)
    duration_of_event = db.Column(db.Integer, nullable=False)
    amount_spent_on_release = db.Column(db.Integer, nullable=True)
    date_of_event = db.Column(db.DateTime, nullable=False)
    is_processed = db.Column(db.Integer, nullable=True)
    project_name = db.Column(db.String(100), unique=False, nullable=True)
    workshop_name = db.Column(db.String(100), unique=False, nullable=True)
    # current_amount = db.Column(db.Integer, nullable=False)


    def __repr__(self):
        return f"User('{self.budget_code}')"







# add db data below-------------


# user1 = User(username='Sam')
#
# b = Budgets(users = 'Sam', code= '54321', initial_amount='10000', amount_spent = '100')

# db.session.add(user1)
# db.session.add(b)
# db.session.commit()


# flask-forms below-------------

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    # remember = BooleanField('Remember me')
    submit = SubmitField('Sign in')

class ModifyUserForm(FlaskForm):
    # # x = User.query.all()
    username = SelectField(u'User names')
    budget_code = SelectField(u'Budget code')
    # username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    # budget_code = StringField('Busget code')
    submit = SubmitField('Done')


class addToBudgetForm(FlaskForm):
    code = StringField(u'Budget Code')
    project_name = StringField('Project Code')
    description = StringField(u'Short Description')
    initial_amount = FloatField('Initial amount')
    amount_spent = FloatField('Amount already spent')
    submit = SubmitField('Create')


class d(FlaskForm):
    id = SelectField('Id #')
    submit = SubmitField('Delete')

class p(FlaskForm):
    event_id = StringField('Event id')
    submit = SubmitField('Print')


class remind(FlaskForm):
    budget_code = SelectField(u'Budget code')
    submit = SubmitField('Send a reminder')


class UpdateBudgetForm(FlaskForm):
    code = SelectField(u'Budget codes')
    tag = TextField('Workshop name', validators=[Length(max=10)])
    guests_present = TextField('People released', validators=[DataRequired(), Length(max=2000)])
    school = TextField('School', validators=[DataRequired(), Length(max=2000)])
    # spent = IntegerField('Amount Used', validators=[DataRequired()])
    duration_of_event = RadioField('Duration of Release', choices=[('120', 'Half day'), ('240', 'Full day'), ('1', 'Other')], validators=[DataRequired()])
    submit = SubmitField('Submit')
    date_of_event = DateField('Date of event (Y-M-D)', format='%Y-%m-%d', id='datepicker')


class UpdateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    password2 = PasswordField('Verify password', validators=[DataRequired(), Length(min=6, max=20)])
    budgets_access = StringField('Budget access')
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

    # db.create_all()
    # p = hashlib.md5('12345'.encode())
    # pword1 = p.hexdigest()

    # p = hashlib.md5('33333'.encode())
    # pword2 = p.hexdigest()

    # user1 = User(username='SamTest', super_user=1, password=pword1, budgets_access='', email='')
    # # user2 = User(username='BobTest', super_user=0, password=pword2, budgets_access='55555', email='saltarachofmann@swlauriersb.qc.ca')
    # # b1 = Budgets(code= '12345', project_name='ebpp', initial_amount='13000', amount_spent = '1000', description='success project')
    # # b2 = Budgets(code= '55555', project_name='NA', initial_amount='1200', amount_spent = '10', description='AC PLC')

    # # db.session.add(b1)
    # # db.session.add(b2)
    # db.session.add(user1)
    # # db.session.add(user2)
    # db.session.commit()

    form = LoginForm()
    # h = hashlib.md5(password.encode())
    # print(h.hexdigest())
    if form.validate_on_submit():

        p = hashlib.md5(form.password.data.encode())
        pword = p.hexdigest()

        users = User.query.filter_by(username=f'{form.username.data}', password=f'{pword}').count()

        if(users > 0 ):
            user = User.query.filter_by(username=f'{form.username.data}', password=f'{pword}').first()

            if(user.super_user == 1):
                session['key']= [True, f'{form.username.data}']

            else:
                session['key']=[False, f'{form.username.data}']

            return redirect(f'profile/{form.username.data}')
        else:
            session['key']=[False, None]
            return render_template('index.html', form = form)

    return render_template('index.html', form = form)




@app.route('/profile/<string:name>', methods=['POST', 'GET'])
def profile(name):
    u = name
    bbb = Budgets.query.all()
    bs1  = []
    bs2  = []
    for i in bbb:
        balance = i.initial_amount-i.amount_spent
        bs1.append(str(i.code))
        bs2.append(round((1-(balance/i.initial_amount))*100, 2))
    if(u != session['key'][1]):
        return redirect(url_for('index'))


    form = UpdateBudgetForm()
    theForm2 = remind()
    # form2 = updateNamesAndSchools()

    tables = []
    x = User.query.filter_by(username=f'{u}').first()
    codes = x.budgets_access.split(',')
    for c in codes:
        b = Budgets.query.filter_by(code=f'{c.strip()}').first()
        tables.append(b)

    form.code.choices = [((g), (g)) for g in codes]
    theForm2.budget_code.choices = [((g.code), (g.code)) for g in Budgets.query.all()]

    if(len(codes) <= 4):
        b_count = len(codes)
    else:
        b_count = 4

    if form.is_submitted():
        bb = Budgets.query.filter_by(code=f'{str(form.code.data).strip()}')[0]

        if(bb.amount_spent + len(form.guests_present.data.split(','))*int(form.duration_of_event.data) > bb.initial_amount):
            flash(f'You have depleted budget {form.code.data}. Please, talk to Admin.')
            return redirect(f'profile/{u}/update')

        # -----------------------------------

        # from email.message import EmailMessag
        # ##############################sss


        names = ', '.join(request.form.getlist('names'))
        schools = ', '.join(request.form.getlist('schools'))


        if(form.duration_of_event.data=='1'):
            dur = int(request.form.get('mins'))
        else:
            dur = int(form.duration_of_event.data)

        # flash(dur)

        try:
            EMAIL_ADDRESS = 'saltarachofmann@swlsb.ca'
            EMAIL_PASSWORD = 'sam05244'


            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()

                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

                subject=f'New release request from {u} using budget code: {form.code.data}. Workshop name: {form.tag.data}'
                body = f'On {form.date_of_event.data} the following teachers are being released: [{names}] from the following schools respectively: [{schools}] using the budget code: {form.code.data}. Thank you.'

                msg = f'Subject: {subject} \n\n {body}'


                smtp.sendmail(EMAIL_ADDRESS, 'erossi@swlauriersb.qc.ca', msg)
        except:
            pass



        pay_rate = 1.04166

        bb.amount_spent = bb.amount_spent + int(len(names.split(','))*int(dur)*pay_rate)



        e = Event(guests_present=names, budget_code=form.code.data.strip(),
        project_name=bb.project_name, duration_of_event=form.duration_of_event.data, amount_spent_on_release=int(len(names.split(','))*int(dur)*pay_rate), date_of_event=form.date_of_event.data, users = u, is_processed = 0, workshop_name=form.tag.data, school=schools)
        db.session.add(e)
        db.session.commit()
        return redirect(f'profile/{u}')




    # ----------------------------

    events = Event.query.filter_by(users=f'{u}')

    # code = b.code
    # initial_amount = b.initial_amount
    # spent = b.amount_spent
    # balance = initial_amount-spent

    return render_template('profile.html', u = u, tables = tables, tables2 = bbb, events = events, b_count = b_count, x = codes, bs1 =bs1, bs2=bs2, form2 = theForm2)


@app.route('/remind/<name>', methods=['GET', 'POST'])
def reminder(name):
    u = name
    theForm2 = remind()
    sent = 0
    if theForm2.is_submitted():
        ccc = f'{theForm2.budget_code.data}'

        people_to_email = []
        x = User.query.all()

        for i in x:
            if(ccc in i.budgets_access.split(',')):
                people_to_email.append(i.email)


        try:
            EMAIL_ADDRESS = 'saltarachofmann@swlsb.ca'
            EMAIL_PASSWORD = 'sam05244'


            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()

                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)


                subject = 'Reminder'
                body=f'Please make sure you are tending to budget: {theForm2.budget_code.data}. Thank you.'

                msg = f'Subject: {subject} \n\n {body}'


                smtp.sendmail(EMAIL_ADDRESS, people_to_email, msg)
                smtp.quit()

            sent = 1

        except:
            sent = 0
            pass

        if sent == 1:
            flash(f"Reminders sent")
        else:
            flash("Emails didn't go through")

        return redirect(url_for('profile', name=u))



@app.route('/profile/<string:name>/update', methods=['POST', 'GET'])
def profile2(name):
    u = name

    if(u != session['key'][1]):
        return redirect(url_for('index'))


    form = UpdateBudgetForm()
    tables = []
    x = User.query.filter_by(username=f'{u}')[0]
    codes = x.budgets_access.split(',')
    for c in codes:
        b = Budgets.query.filter_by(code=(c.strip())).first()
        tables.append(b)

    form.code.choices = [((g.strip()), (g.strip())) for g in codes]
    # code = b.code
    # initial_amount = b.initial_amount
    # spent = b.amount_spent
    # balance = initial_amount-spent

    return render_template('update.html', u = u, b= tables, form =form)


@app.route('/profile/<string:name>/delete', methods=['POST', 'GET'])
def delete(name):
    u = name

    if(u != session['key'][1]):
        return redirect(url_for('index'))


    form = d()

    tables = []
    e = Event.query.filter_by(users=f'{u}')
    x = User.query.filter_by(username=f'{u}')[0]
    codes = x.budgets_access.split(',')
    for c in codes:
        b = Budgets.query.filter_by(code=(c.strip())).first()
        tables.append(b)

    form.id.choices = [(int(g.id), int(g.id)) for g in e]

    if form.is_submitted():
        row = Event.query.filter_by(id=f'{form.id.data}').first()

        bb = Budgets.query.filter_by(code=f'{str(row.budget_code).strip()}')[0]
        bb.amount_spent = bb.amount_spent - row.amount_spent_on_release


        db.session.delete(row)
        db.session.commit()


    return render_template('delete.html', u = u, b= tables, form =form, ee = e)




@app.route('/master', methods=['POST', 'GET'])
def master():
    if(session['key'][0] == False):
        return redirect(url_for('index'))
    else:
        u=session['key'][1]
    # cnx = sqlite3.connect('myDatabase.db')



    people = User.query.filter(User.super_user != 1).all()
    codes = Budgets.query.all()

    pro=[]
    isnt_processed = Event.query.filter_by(is_processed=0)
    for i in isnt_processed:
        if i.is_processed == 0:
            pro.append(i.budget_code)


    res = []

    budget_codes = Budgets.query.all()


    for b in budget_codes:
        e = Event.query.filter_by(budget_code=b.code).first()
        if e:
            res.append(e)



    return render_template('master.html', people = people, res = res, codes = codes, u = u, pro =pro)



@app.route('/master/profile/<string:name>', methods=['POST', 'GET'])
def masterprofile(name):
    u = name
    if(session['key'][0]==False):
        return redirect(url_for('index'))
    # form = updateAndNew()
    form = MasterBudgetForm()
    form2 = addToBudgetForm()
    form3 = d()
    printform = p()
    tables = []
    x = User.query.filter_by(username=f'{u}')[0]
    codes = x.budgets_access.split(',')
    for c in codes:
        b = Budgets.query.filter_by(code=(c.strip())).first()
        tables.append(b)
    events = Event.query.filter_by(users=f'{u}').order_by(desc(Event.budget_code))
    cs = codes


    y =Event.query.filter_by(users=f'{u}').order_by(desc(Event.budget_code)).filter_by(is_processed='0')

    events2 = y


    if form.validate_on_submit():
        bb = Budgets.query.filter_by(code=f'{form.code.data.strip()}')[0]
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








@app.route('/master2/profile2/<string:budget_code>', methods=['POST', 'GET'])
def masterprofile2(budget_code):
    if(session['key'][0]==False):
        return redirect(url_for('index'))

    u = session['key'][1]
    bc = budget_code
    printform = p()
    e = Event.query.filter_by(budget_code=f'{bc}', is_processed='0')
    e2 = Event.query.filter_by(budget_code=f'{bc}')


    return render_template('masterprofile2.html',u =u, events = e, bc= bc, printform = printform, events2 = e2)










@app.route('/master3/profile/<string:name>', methods=['POST', 'GET'])
def masterprofile3(name):
    if(session['key'][0] == False):
        return redirect(url_for('index'))
    u = name
    # form = updateAndNew()
    form = MasterBudgetForm()
    form2 = addToBudgetForm()
    form3 = d()

    tables = []
    x = User.query.filter_by(username=f'{u}')[0]
    codes = x.budgets_access.split(',')
    for c in codes:
        b = Budgets.query.filter_by(code=(c.strip())).first()
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
    if(session['key'][0] == False):
        return redirect(url_for('index'))
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
# ------
@app.route('/print2/<string:budget_code>', methods=['GET','POST'])
def printing2(budget_code):
    bc = budget_code
    if(session['key'][0] == False):
        return redirect(url_for('index'))

    if(session['key'] == False):
        return redirect(url_for('index'))

    e = Event.query.filter_by(budget_code=f'{bc}', is_processed='0').all()
    for i in e:
        i.is_processed = 1
    db.session.commit()

    return redirect(url_for('master'))



@app.route('/newbudget', methods=['GET','POST'])
def newbudget():
    if(session['key'][0] == False):
        return redirect(url_for('index'))
    else:
        u=session['key'][1]

    form=addToBudgetForm()

    bb = Budgets.query.all()


    if form.is_submitted():

        # bs = Budgets.query.filter_by(code=f'{form.code.data}').count()
        # if (bs>0):
        #     flash('Code already exists')
        #     return redirect('newbudget')
        x = float(form.initial_amount.data)
        y = float(form.amount_spent.data)
        b = Budgets(code= f'{form.code.data}', project_name = f'{form.project_name.data}', initial_amount=f'{x}', amount_spent = f'{y}', description=f'{form.description.data}')
        db.session.add(b)
        db.session.commit()
        return redirect('newbudget')


    return render_template('newbudget.html', form = form, bb = bb, u = u)


@app.route('/newuser', methods=['GET','POST'])
def newuser():
    if(session['key'][0] == False):
        return redirect(url_for('index'))
    else:
        u=session['key'][1]

    form=UpdateUserForm()

    uu = User.query.all()


    if form.is_submitted():
        users = User.query.filter_by(username=f'{form.username.data}').count()
        if (users>0):
            flash('Username already taken')
            return redirect('newuser')

        if(form.password.data == form.password2.data):

            p = hashlib.md5(form.password.data.encode())
            pword = p.hexdigest()


            user = User(username= f'{form.username.data}', password=f'{pword}', budgets_access = f'{form.budgets_access.data}', email = f'{form.email.data}')
            db.session.add(user)
            db.session.commit()
            return redirect('newuser')



    return render_template('newuser.html', form = form, uu = uu, u=u)


@app.route('/modifyuser', methods=['GET','POST'])
def modifyuser():
    if(session['key'][0] == False):
        return redirect(url_for('index'))
    else:
        u=session['key'][1]

    form=ModifyUserForm()

    uu = User.query.all()
    b = Budgets.query.all()

    form.username.choices = [(str(g.username), str(g.username)) for g in uu]
    form.budget_code.choices = [(str(g.code), str(g.code)) for g in b]



    if form.is_submitted():

        user = User.query.filter_by(username=f'{form.username.data}').first()
        if(form.budget_code.data.strip() not in user.budgets_access.split(', ')):
            user.budgets_access = user.budgets_access + f', {form.budget_code.data}'
            db.session.commit()
            flash('Done')
        else:
            flash('Already has permission')
            return redirect(url_for('modifyuser'))



    return render_template('modifyuser.html', form = form, uu = uu, u = u)



@app.route('/tutorial/<string:name>')
def tutorial(name):
    u = name
    return render_template('tutorial.html', u = u)



@app.route('/register', methods=['GET','POST'])
def register():
    # if(session['key'][0] == False):
    #     return redirect(url_for('index'))
    # else:
    #     u=session['key'][1]


    form=UpdateUserForm()

    uu = User.query.all()


    if form.is_submitted():
        if(form.password.data == form.password2.data):

            p = hashlib.md5(form.password.data.encode())
            pword = p.hexdigest()

            user = User(username= f'{form.username.data}', password=f'{pword}', budgets_access = f'{form.budgets_access.data}')
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))


    return render_template('register.html', form = form, uu = uu)


@app.route('/super-register', methods=['GET','POST'])
def superRegister():
    # if(session['key'][0] == False):
    #     return redirect(url_for('index'))
    # else:
    #     u=session['key'][1]


    form=UpdateUserForm()

    uu = User.query.all()


    if form.is_submitted():
        if(form.password.data == form.password2.data):

            p = hashlib.md5(form.password.data.encode())
            pword = p.hexdigest()

            user = User(username= f'{form.username.data}', password=f'{pword}', budgets_access = f'{form.budgets_access.data}', super_user=1, email = f'{form.email.data}')
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))


    return render_template('superRegister.html', form = form, uu = uu)

@app.route('/<string:name>/reach')
def reach(name):
    u = name
    if(session['key'][0] == False):
        return redirect(url_for('index'))
    number_of_teachers=[]
    number_of_schools = []
    number_of_schools2 = []
    events = Event.query.all()

    for i in range(1, 13):
        t = 0
        for e in events:
            if e.date_of_event.month==i:
                t = t + len(e.guests_present.split())
                # nt.append((e.date_of_event.month, len(e.guests_present.split())))

        if t != 0:
            number_of_teachers.append((calendar.month_name[i], t))
            # nt.append((i, t))


        a=[]
        total_teachers = 0
        es = Event.query.with_entities(Event.school).all()
        for i in es:
            for x in i.school.split(','):
                a.append(x.strip().upper())
                total_teachers = len(a)



        s = x, y = np.unique(a, return_counts=True)



    return render_template('reach.html',u=u, events = events, nt = number_of_teachers, s = s, t = total_teachers)


@app.route('/logout')
def logout():
    form = LoginForm()
    session.clear()

    return redirect(url_for('index'))




@app.route('/corrections', methods=['GET','POST'])
def corrections():
    if(session['key'][0]==False):
        return redirect(url_for('index'))

    u = session['key'][1]
    printform = p()
    e = Event.query.all()

    if request.method == 'POST':
        b = request.form.get('budget_code')
        pay_rate = 1.04166
        dur = int(request.form.get('duration_of_event'))
        e_id = request.form.get('event_id')
        bb = Budgets.query.filter_by(code=f'{str(b).strip()}')[0]
        ee = Event.query.filter_by(id=f'{e_id}').first()
        diff = float(ee.duration_of_event - dur)

        if(bb.amount_spent + dur*pay_rate > bb.initial_amount):
            flash(f'Cannot make this change - the budget is depleted. Please, talk to Admin.')
            return redirect(url_for('corrections'))


        if(diff < 0):

            ee.duration_of_event = dur
            number_of_teachers = int(len(ee.guests_present.strip().split(',')))
            bb.amount_spent = bb.amount_spent + diff*pay_rate*number_of_teachers
            db.session.commit()

        elif(diff > 0):

            ee.duration_of_event = dur
            number_of_teachers = int(len(ee.guests_present.strip().split(',')))
            bb.amount_spent = bb.amount_spent - diff*pay_rate*number_of_teachers
            db.session.commit()

        else:
            pass







    return render_template('corrections.html', e=e, u=u)


@app.route('/corrections/<int:id>', methods=['GET','POST'])
def corrections2(id):
    if(session['key'][0]==False):
        return redirect(url_for('index'))

    form = p()
    event_id = id
    u = session['key'][1]
    printform = p()
    e = Event.query.filter_by(id=event_id).first()



    return render_template('corrections2.html', e=e, u=u, form = form)
