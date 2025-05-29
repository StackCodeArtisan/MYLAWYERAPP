import requests, json, random, os, secrets
from flask import render_template, redirect, request, flash, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename 
from mylawyerpkg.models import db,Lawyer, State, Payment,Appointment, Client
from mylawyerpkg import app
from mylawyerpkg.forms import  LawyerLoginForm, Lawyerform
from datetime import datetime
from sqlalchemy.orm import joinedload
from flask_wtf.csrf import CSRFProtect

#lawyer signup routes

@app.route('/lawyer/signup/', methods=['GET', 'POST'])
def lawyer_signup():
    if request.method == 'GET':
        return render_template('lawyers/lawyer_signup.html')
    else:
        firstname = request.form.get('ufirstname')
        secondname = request.form.get('usecondname')
        email  = request.form.get('uemail') 
        password = request.form.get('upassword')
        cpassword = request.form.get('cupassword')
        if password != cpassword:
            flash('errormsg', 'password mismatch, please try again')
            return redirect('/lawyer/signup/')
        else:
            hashed = generate_password_hash(password)
            lawyers = Lawyer(lawyer_fname=firstname, lawyer_lname=secondname, lawyer_password=hashed, lawyer_email=email)
            db.session.add(lawyers)
            db.session.commit()
            flash('feedback', 'An account has been created for you, please login')
            return redirect('/lawyer/login/')
#end of lawyer sign up routes

#lawyer login routes

@app.route('/lawyer/login/', methods=['GET','POST'])
def lawyer_login():
    lawloginform =  LawyerLoginForm() 
    if request.method == 'GET':
        return render_template('lawyers/lawyer_login.html', lawloginform=lawloginform)
    else: 
        if lawloginform.validate_on_submit():
            email = lawloginform.email.data
            password = lawloginform.password.data
            record = db.session.query(Lawyer).filter(Lawyer.lawyer_email==email).first() 
            if record:  
                hashed_password = record.lawyer_password
                chek = check_password_hash(hashed_password, password) 
                if chek: 
                    session['loggedin'] = record.lawyer_id
                    return redirect('/lawyer/profile/') 
                else:
                    flash ('errormsg', 'Invalid Password')
                    return redirect('/lawyer/login/')
            else:
                flash('errormsg', 'invalid Email')
                return redirect('/lawyer/login/')
            
        else:
            return render_template('lawyers/lawyer_login.html', lawloginform=lawloginform)


#emd of lawyer login route

#lawyer logout routes

@app.route('/lawyer/logout/')
def lawyer_logout():
    session.pop('loggedin', None)
    flash('feedback', 'you have logged out')
    return redirect('/login/')

#end of lawyer logout routes

#lawyer profile routes
@app.route('/lawyer/profile/', methods=['POST', 'GET'])
def lawyers_dashboard():
    loggedin_lawyer = session.get('loggedin')
    # Eagerly load the client relationship so that appointment.client is available
    appointments = Appointment.query.options(joinedload(Appointment.client))\
                        .filter_by(lawyer_id=loggedin_lawyer).all()
    if not appointments:
        appointments = None

    lform = Lawyerform() 
    if loggedin_lawyer:
        states = State.query.all()
        # Note: The line below first retrieves a list but then is overwritten by get().
        # Ensure that your logic aligns with your intended behavior.
        lawyer_deets = db.session.query(Lawyer).filter(
            Lawyer.lawyer_id == loggedin_lawyer,
            Payment.payment_status == 'paid'
        ).all()
        lawyer_deets = db.session.query(Lawyer).get(loggedin_lawyer)

        lform.lawyer_fname.data = lawyer_deets.lawyer_fname
        lform.lawyer_lname.data = lawyer_deets.lawyer_lname
        lform.lawyer_email.data = lawyer_deets.lawyer_email
        lform.lawyer_phone.data = lawyer_deets.lawyer_phone
        lform.lawyer_license_number.data = lawyer_deets.lawyer_license_number
        lform.lawyer_date_registered.data = lawyer_deets.lawyer_date_registered
        lform.lawyer_specialization.data = lawyer_deets.lawyer_specialization
        lform.lawyer_gender.data = lawyer_deets.lawyer_gender
        lform.lawyer_practice_year.data = lawyer_deets.lawyer_practice_year
        lform.lawyer_certification_document.data = lawyer_deets.lawyer_certification_document
        lform.lawyer_price_range_per_hour.data = lawyer_deets.lawyer_price_range_per_hour

        if lform.validate_on_submit():
            lawyer_deets.lawyer_fname = lform.lawyer_fname.data
            lawyer_deets.lawyer_lname = lform.lawyer_lname.data
            lawyer_deets.lawyer_email = lform.lawyer_email.data
            lawyer_deets.lawyer_phone = lform.lawyer_phone.data
            lawyer_deets.lawyer_gender = lform.lawyer_gender.data
            lawyer_deets.lawyer_state = lform.lawyer_state.data
            lawyer_deets.lawyer_license = lform.lawyer_license_number.data
            lawyer_deets.lawyer_date_registered = lform.lawyer_date_registered.data            
            lawyer_deets.lawyer_specialization = lform.lawyer_specialization.data            
            lawyer_deets.lawyer_practice_year = lform.lawyer_practice_year.data
            lawyer_deets.lawyer_certification_document = lform.lawyer_certification_document.data
            lawyer_deets.lawyer_price_range_per_hour = lform.lawyer_price_range_per_hour.data

            db.session.commit()
            flash('feedback', 'Profile details updated successfully!')
            return redirect('/lawyer/profile/')

        return render_template(
            'lawyers/lawyer_profile_page.html',
            lawyer_deets=lawyer_deets,
            lform=lform,
            states=states,
            appointments=appointments
        )
    else:
        flash('errormsg', 'You must be logged in')
        return redirect('/lawyer/login/')

#end of lawyer profile routes


#lawyer profile update routes

@app.route('/lawyer/profile/<lawyer_id>/update/', methods=['POST', 'GET'])
def lawyer_update_profile(lawyer_id):
    loggedin_lawyer = session.get('loggedin')
    
    # Check if the user is logged in
    if loggedin_lawyer:
        states = State.query.all()
        # Fetch the lawyer's details from the database based on the lawyer_id
        lawyer_deets = db.session.query(Lawyer).get(lawyer_id)

        
        if not lawyer_deets:
            flash('errormsg', 'Lawyer not found!')
            return redirect('/lawyer/profile/')
        
        # Handle form submission
        if request.method == 'POST':
            # Get the form fields
            lawyer_fname = request.form.get('lawyer_fname')
            lawyer_lname = request.form.get('lawyer_lname')
            lawyer_email = request.form.get('lawyer_email')
            lawyer_phone = request.form.get('lawyer_phone')
            lawyer_gender = request.form.get('lawyer_gender')
            lawyer_practice_year = request.form.get('lawyer_practice_year')
            lawyer_certification_document = request.form.get('lawyer_certification')
            lawyer_price_range_per_hour = request.form.get('lawyer_price_per_hour')
            lawyer_license_number = request.form.get('lawyer_license_number')
            lawyer_specialization = request.form.get('lawyer_specialization')
            
            # Check if a new profile picture was uploaded
            file = request.files.get('lawyer_profile_picture')
            if file:
                # Validate file type
                allowed_ext = ['.jpg', '.jpeg', '.png', '.gif']
                _, ext = os.path.splitext(file.filename)
                
                if ext.lower() not in allowed_ext:
                    flash('errormsg', 'Profile picture must be an image file (.jpg, .jpeg, .png, .gif)')
                    return redirect(f'/profile/{lawyer_id}/update/')
                
                # Generate a random string for the filename to avoid conflicts
                rand_str = secrets.token_hex(10)
                filename = f'{rand_str}{ext}'
                file.save(os.path.join('mylawyerpkg/static/uploads', filename))
                lawyer_deets.lawyer_profile_picture = filename  # Update profile picture filename
            
            # Update the other lawyer details
            lawyer_deets.lawyer_fname = lawyer_fname
            lawyer_deets.lawyer_lname = lawyer_lname
            lawyer_deets.lawyer_email = lawyer_email
            lawyer_deets.lawyer_phone = lawyer_phone
            lawyer_deets.lawyer_gender = lawyer_gender
            lawyer_deets.lawyer_practice_year = lawyer_practice_year
            lawyer_deets.lawyer_certification_document = lawyer_certification_document
            lawyer_deets.lawyer_price_range_per_hour = lawyer_price_range_per_hour
            lawyer_deets.lawyer_license_number = lawyer_license_number
            lawyer_deets.lawyer_specialization = lawyer_specialization
            
            # Commit changes to the database
            db.session.commit()
            
            flash('feedback', 'Profile details updated successfully!')
            return redirect(f'/lawyer/profile/{lawyer_id}/update/')  # Redirect back to the profile update page
        
        # Handle GET request (show the current profile data in the form)
        return render_template('lawyers/lawyer_profile_page.html', lawyer_deets=lawyer_deets, states=states)
    
    # If the user is not logged in, redirect to login page
    flash('errormsg', 'You must be logged in to update your profile')
    return redirect('/lawyer/login/')

#end of lawyer profile upadate routes

@app.route('/lawyer/home/')
def lawyer_home():
    loggedin_lawyer = session.get('loggedin')
    if loggedin_lawyer:
        lawyer_deets = db.session.query(Lawyer).get(loggedin_lawyer) 
    return render_template('landing_page/index.html', lawyer_deets=lawyer_deets)

@app.route('/lawyer/about/')
def lawyer_about():
    loggedin_lawyer = session.get('loggedin')
    if loggedin_lawyer:
        lawyer_deets = db.session.query(Lawyer).get(loggedin_lawyer)
    return render_template('landing_page/about_us.html', lawyer_deets=lawyer_deets)

@app.route('/lawyer/blog/')
def lawyer_blog():
    loggedin_lawyer = session.get('loggedin')
    if loggedin_lawyer:
        lawyer_deets = db.session.query(Lawyer).get(loggedin_lawyer)
    return render_template('landing_page/blog.html', lawyer_deets=lawyer_deets)


# Add to lawyer_dashboard route
@app.route('/lawyer/profile/', methods=['POST','GET'])
def lawyer_dashboard():
    loggedin_lawyer = session.get('loggedin')  # Retrieve logged-in lawyer ID from session
    if not loggedin_lawyer:
        flash('errormsg', 'You must be logged in')
        return redirect('/lawyer/login/')
    
    # Fetch lawyer details
    lawyer_deets = db.session.query(Lawyer).get(loggedin_lawyer)
    if not lawyer_deets:
        flash('errormsg', 'Lawyer details not found')
        return redirect('/lawyer/login/')
    
    # Define lform
    lform = Lawyerform()

    # Add this line before the return statement
    appointments = db.session.query(Appointment).options(
            db.joinedload(Appointment.client)
        ).filter(Appointment.lawyer_id == loggedin_lawyer).all()
    states = State.query.all()  # Define states by querying the State model
    
    return render_template('lawyers/lawyer_profile_page.html', 
                         lawyer_deets=lawyer_deets, 
                         lform=lform, 
                         states=states,
                         appointments=appointments)  # Add appointments to context

# Add new routes for appointment management
@app.route('/lawyer/appointment/<int:appointment_id>/accept/', methods=['POST'])
def accept_appointment(appointment_id):
    if 'loggedin' not in session:
        flash('errormsg', 'You must be logged in')
        return redirect('/lawyer/login/')

    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        flash('errormsg', 'Appointment not found')
        return redirect('/lawyer/profile/')

    if appointment.lawyer_id != session['loggedin']:
        flash('errormsg', 'Unauthorized action')
        return redirect('/lawyer/profile/')

    appointment.status = 'accepted'
    db.session.commit()
    flash('feedback', 'Appointment accepted successfully')
    return redirect('/lawyer/profile/')

@app.route('/lawyer/appointment/<int:appointment_id>/reject/', methods=['POST'])
def reject_appointment(appointment_id):
    if 'loggedin' not in session:
        flash('errormsg', 'You must be logged in')
        return redirect('/lawyer/login/')

    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        flash('errormsg', 'Appointment not found')
        return redirect('/lawyer/profile/')

    if appointment.lawyer_id != session['loggedin']:
        flash('errormsg', 'Unauthorized action')
        return redirect('/lawyer/profile/')

    appointment.status = 'rejected'
    db.session.commit()
    flash('feedback', 'Appointment rejected successfully')
    return redirect('/lawyer/profile/')