from flask import render_template, redirect, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from mylawyerpkg import app
from mylawyerpkg.models import Client, Lawyer, db
from mylawyerpkg.forms import LoginForm


@app.route('/')
def home_page():
    lawyer_deets = None
    client_deet = None
    loggedin_lawyer = session.get('loggedin')
    if loggedin_lawyer:
        lawyer_deets = db.session.query(Lawyer).get(loggedin_lawyer)
    loggedin_client = session.get('loggedin') 
    if loggedin_client: 
        client_deet = db.session.query(Client).get(loggedin_client) 
        return render_template('landing_page/index.html', client_deet=client_deet, lawyer_deets=lawyer_deets)
    else:
        
        return render_template('landing_page/index.html', client_deet=client_deet, lawyer_deets=lawyer_deets)

@app.route('/home/message/')
def message_flash():
    flash('We Welcome to MYLAWYEr!',category='success')
    return redirect('/home/')

@app.route('/about/')
def about_us():
    loggedin_lawyer = session.get('loggedin')
    if loggedin_lawyer:
        lawyer_deets = db.session.query(Lawyer).get(loggedin_lawyer)
    loggedin_client = session.get('loggedin') 
    if loggedin_client: 
        client_deet = db.session.query(Client).get(loggedin_client) 
    return render_template('landing_page/about_us.html', lawyer_deets=lawyer_deets, client_deet=client_deet)

@app.route('/blog/')
def blog():
    loggedin_lawyer = session.get('loggedin')
    if loggedin_lawyer:
        lawyer_deets = db.session.query(Lawyer).get(loggedin_lawyer)
    loggedin_client = session.get('loggedin') 
    if loggedin_client: 
        client_deet = db.session.query(Client).get(loggedin_client) 
    return render_template('landing_page/blog.html', lawyer_deets=lawyer_deets, client_deet=client_deet)

@app.route('/cor/')
def cor():
    return render_template('landing_page/about.html')



    