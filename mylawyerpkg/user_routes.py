import requests, json, random, os, secrets
from flask import render_template, redirect, flash, request, session, url_for, jsonify
from sqlalchemy import or_, and_, func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from mylawyerpkg import app, db, mail
from mylawyerpkg.models import db, Client, Appointment, Lawyer, State
from mylawyerpkg.forms import LoginForm, Profileform, AppointmentForm
from datetime import datetime, timezone
  


#user signup routes
@app.route('/user/signup/', methods=['POST', 'GET'])
def user_sign_up():
    if request.method == 'GET':
        return render_template('users/signup.html')
    else:
        firstname = request.form.get('ufirstname')
        secondname = request.form.get('usecondname')
        email  = request.form.get('uemail') 
        password = request.form.get('upassword')
        cpassword = request.form.get('cupassword')
        if password != cpassword:
            flash('errormsg', 'password mismatch, please try again')
            return redirect('/user/signup/')
        else:
            hashed = generate_password_hash(password)
            user = Client(client_fname=firstname, client_lname=secondname, client_password=hashed, client_email=email)
            db.session.add(user)
            db.session.commit()
            flash('feedback', 'An account has been created for you, please login')
            return redirect('/user/login/')
#user signup routes ends

#user login routes


@app.route('/user/login/', methods=['GET','POST'])
def user_login():
    loginform = LoginForm() 
    if request.method == 'GET':
        return render_template('users/login.html', loginform=loginform)
    else: 
        if loginform.validate_on_submit():
            email = loginform.email.data
            password = loginform.password.data
            record = db.session.query(Client).filter(Client.client_email==email).first() 
            if record:  
                hashed_password = record.client_password
                chek = check_password_hash(hashed_password, password) 
                if chek: 
                    session['loggedin'] = record.client_id
                    return redirect('/user/profile/') 
                else:
                    flash ('errormsg', 'Invalid Password')
                    return redirect('/user/login/')
            else:
                flash('errormsg', 'invalid Email')
                return redirect('/user/login/')
            
        else:
            return render_template('users/login.html', loginform=loginform)

#user login routes ends

#user logout routes

@app.route('/user/logout/')
def user_logout():
    session.pop('loggedin', None)
    flash('feedback', 'you have logged out')
    return redirect('/login/')

#logout routes ends


#user profile routes

@app.route('/user/profile/', methods=['POST', 'GET'])
def user_dashboard():
    loggedin_client = session.get('loggedin')
    appointments = Appointment.query.filter_by(client_id=session['loggedin'])\
                          .join(Lawyer)\
                          .add_columns(
                              Lawyer.lawyer_fname,
                              Lawyer.lawyer_lname,
                              Appointment.appointment_datetime,
                              Appointment.status
                          ).all()
    cform = Profileform()
    if loggedin_client:
        states = State.query.all()
        client_deets = Client.query.get(loggedin_client)       
        client_deets = db.session.query(Client).get(loggedin_client)
        cform.client_fname.data = client_deets.client_fname
        cform.client_lname.data = client_deets.client_lname
        cform.client_email.data = client_deets.client_email
        cform.client_phone.data = client_deets.client_phone
        cform.client_state.data = client_deets.client_state 
        cform.client_date_registered.data = client_deets.client_date_registered
        cform.client_gender.data = client_deets.client_gender   
        cform.client_profile_picture.data = client_deets.client_profile_picture
               
        if cform.validate_on_submit():
            
            file = cform.client_profile_picture.data
            _,ext = os.path.split(file.filename)
            rand_str = secrets.token_hex(10)
            filename = f'{rand_str}{ext}'
            file.save(f'pkg/static/uploads/{filename}')
            client_deets.client_profile_picture = filename


            client_deets.client_profile_picture = filename
            client_deets.client_fname = cform.client_fname.data
            client_deets.client_lname = cform.client_lname.data
            client_deets.client_email = cform.client_email.data
            client_deets.client_phone = cform.client_phone.data
            client_deets.client_state = cform.client_state.data
            client_deets.client_date_registered = cform.client_date_registered.data
            
            db.session.commit()
            flash('feedback', 'Profile details updated successfully!')
            return redirect('/user/profile/')
        
        return render_template('users/client_profile_page.html', client_deets=client_deets, cform=cform, states=states, appointments=appointments)
    else:
        flash('errormsg', 'Client details not found')
        return redirect('/user/login/')


#user profile routes ends

#user profile update routes

@app.route('/user/profile/<client_id>/update/', methods=['POST', 'GET'])
def update_profile(client_id):
    loggedin_client = session.get('loggedin')
    if loggedin_client:
        client_deets = db.session.query(Client).get(client_id)      
   
        if request.method == 'POST':    
            client_fname = request.form.get('client_fname')
            client_lname = request.form.get('client_lname')
            client_email = request.form.get('client_email')
            client_phone = request.form.get('client_phone')
            client_gender = request.form.get('client_gender')
            client_state = request.form.get('client_state')
            client_date_registered = request.form.get('client_date_registered')

            allowed_ext =['.jpg','.jpeg','.png','.gif']
            file = request.files.get('client_profile_picture')
            _,ext = os.path.splitext(file.filename)
            rand_str = secrets.token_hex(10)
            
            if ext in allowed_ext:
                filename = f'{rand_str}{ext}'
                file.save(f'mylawyerpkg/static/uploads/{filename}')
            else:
                flash('errormsg','You cover image must be an image file')
                return redirect ('/user/profile/')

            client_deets.client_fname = client_fname
            client_deets.client_lname = client_lname
            client_deets.client_email = client_email
            client_deets.client_phone = client_phone
            client_deets.client_gender = client_gender
            client_deets.client_state = client_state
            client_deets.client_date_registered = client_date_registered
            client_deets.client_profile_picture = filename
            db.session.commit()
            flash('feedback','Profile details Updated successfully!')
            return redirect ('/user/profile/')
        else:
            return redirect('/user/profile/')
    else:
        flash('errormsg', 'you must be logged in')
        return redirect('/user/login/')
    

#user profile updates routes ends

@app.route('/book/appointment/', methods=['GET', 'POST'])
def book_appointment():
    if request.method == 'GET':
        if 'loggedin' not in session:
            return redirect('/user/login/')
        client_deets = Client.query.get(session['loggedin'])
        lawyers = Lawyer.query.all()
        
        return render_template(
            'forms/appointment_form.html',
            client_deets=client_deets,
            lawyers=lawyers
        )

    if 'loggedin' not in session:
        return jsonify({"error": "Authentication required"}), 401

    try:
        data = request.form
        lawyer_id = data.get('lawyer_id')
        case_details = data.get('case_details')
        appointment_price = float(data.get('appointment_price', 0))

        # Validate datetime format
        try:
            submitted_dt = datetime.fromisoformat(data['appointment_datetime'])
        except ValueError:
            return jsonify({"error": "Invalid datetime format"}), 400

        current_dt = datetime.now(timezone.utc).replace(tzinfo=None)
        utc_dt = submitted_dt.astimezone(timezone.utc).replace(tzinfo=None)

        # Prevent past date bookings
        if utc_dt.date() < current_dt.date():
            return jsonify({"error": "Cannot book appointments in the past"}), 400

        # Check if an appointment already exists on the same day with the same lawyer
        existing_appointment = Appointment.query.filter(
            and_(
                Appointment.client_id == session['loggedin'],
                Appointment.lawyer_id == lawyer_id,
                func.date(Appointment.appointment_datetime) == utc_dt.date()
            )
        ).first()

        if existing_appointment:
            return jsonify({"error": "You already have an appointment with this lawyer on the selected date"}), 400

        # Save new appointment
        new_appointment = Appointment(
            client_id=session['loggedin'],
            lawyer_id=lawyer_id,
            appointment_datetime=utc_dt,
            case_details=case_details,
            appointment_price=appointment_price,
            status='pending'
        )

        db.session.add(new_appointment)
        db.session.commit()
        return jsonify({"success": "Appointment booked!", "appointment_id": new_appointment.appointment_id}), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Appointment error: {str(e)}")
        return jsonify({"error": "Server error"}), 500


@app.route('/search-lawyers/', methods=['GET'])
def search_lawyers():
    query = request.args.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    try:
        results = Lawyer.query.filter(
            or_(
                Lawyer.lawyer_fname.ilike(f'%{query}%'),
                Lawyer.lawyer_lname.ilike(f'%{query}%'),
                Lawyer.lawyer_email.ilike(f'%{query}%'),
                Lawyer.lawyer_phone.ilike(f'%{query}%'),
                Lawyer.lawyer_specialization.ilike(f'%{query}%'),
                Lawyer.lawyer_price_range_per_hour.ilike(f'%{query}%'),
                Lawyer.lawyer_license_number.ilike(f'%{query}%')
            )
        ).all()

        lawyers_data = [
            {
                "id": lawyer.lawyer_id,
                "name": f"{lawyer.lawyer_fname} {lawyer.lawyer_lname}",
                "email": lawyer.lawyer_email,
                "phone": lawyer.lawyer_phone,
                "specialization": lawyer.lawyer_specialization,
                "profile_picture": lawyer.lawyer_profile_picture or "/static/images/default-profile.png",
                "price_range": lawyer.lawyer_price_range_per_hour,
                "license_number": lawyer.lawyer_license_number,
            }
            for lawyer in results
        ]

        return jsonify(lawyers_data)
    
    except Exception as e:
        app.logger.error(f"Search error: {str(e)}")
        return jsonify({"error": "Server error"}), 500



