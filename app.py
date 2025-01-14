from flask import Flask, render_template,request,redirect, url_for ,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_login import LoginManager, UserMixin,login_user,logout_user,current_user,login_required
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename



app = Flask(__name__)
load_dotenv()

UPLOAD_FOLDER = "static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] =  os.getenv("SECRETE_KEY")
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tracker.db"
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")


#intitializing database
db = SQLAlchemy(app)

#initinalizing Login manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


# User loader fuction for allowing Flask to loggin users
@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


ALLOWED_EXTENSIONS = {"png","jpeg","jpg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

# Database schema for user Account
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    workout = db.relationship("Workout", backref='users', passive_deletes=True)
    
class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    calories_burned = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    type_of_workout = db.Column(db.String(120), nullable=False)
    authour = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)



@app.route("/")
@app.route("/home")
def home():
    users = Users.query.all()
    return render_template("index.html", users=current_user) 



# Creating User account
@app.route("/sign-up", methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        email_exits = Users.query.filter_by(email=email).first()
        if email_exits:
            flash("Email already exits", category="error")
            print("Email failed")
        elif password != confirm_password:
            flash("Password don't match", category="error")
            print("Password failed")
        elif len(password) < 5:
            flash("Password must be at least 5 characters", category="error")
            print("password2 failed")
        elif len(username) < 4:
            flash("Username must be at least 4 characters", category="error")
            print("username failed")
        elif len(email) < 4:
            flash("Email must be at least 4 characters", category="error")
            print("Email failed again")
        elif len(password) > 10:
            flash("Password must be at most 10 characters", category="error")
            print("password failed again")
        else:
            new_user = Users(username=username, email=email,password=generate_password_hash(password, method="pbkdf2:sha256"))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created successfully", category="success")
            return redirect(url_for('login'))
    return render_template("sign-up.html", users=current_user)



# Handels Logging in users
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()
        if not user:
            flash("Account does not Exist!", category="error")
        elif user:
            if check_password_hash(user.password, password):
                flash("Loggin Successful!", category="success")
                login_user(user,remember=True)
                return redirect(url_for('dashboard'))
            else:
                flash("Incorrect email or password, Please enter the correct password", category="error")
                return render_template("login.html", users=current_user)
        
            
    return render_template("login.html", users=current_user)


@app.route("/dashboard")
@login_required
def dashboard():
    workouts = Workout.query.filter_by(authour=current_user.id).all()
    # users = Users.query.all()
    calories = []
    duration = []
    for workout in workouts:
        calories_count = workout.calories_burned
        duration_count = workout.duration
        calories.append(float(calories_count))
        duration.append(float(duration_count))
    total_cal = sum(calories)
    total_dur = sum(duration)
    return render_template("dashboard.html", users=current_user,workouts=workouts,total_cal=total_cal,total_dur=total_dur)



def is_number(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


@app.route("/tracker",methods=['GET','POST'])
@login_required
def tracker():
    if request.method == 'POST':
        data  = request.get_json()

        if data == None:
            flash("Please fill in the fields!", category="error")
            return jsonify({"message":"No data provided!"}),400
        

        calories_burned = data.get('calories')
        duration = data.get('duration')
        date = data.get('formatSent')
        workout_option = data.get('workoutoption')

        if calories_burned:
            workout = Workout(calories_burned=calories_burned, duration=duration,date=date,type_of_workout=workout_option,authour=current_user.id)
            db.session.add(workout)
            db.session.commit()
            flash("Workout Created Successfully!", category="success")
            print(calories_burned,duration,date,workout_option)
        else:
            flash("Please fill in the fields!", category="error")
        return jsonify({"message":"Data Sent Successfully"}),200

    # workout = Workout.query.filter_by(authour=current_user.id).all()
    return render_template("tracker.html", users=current_user)


@app.route("/tracker_data")
@login_required
def tracker_data():
    workouts = Workout.query.filter_by(authour=current_user.id).all()
    if not workouts:
        # flash("Please fill in the fields!", category="error")
        return jsonify({"message":"No workout data found!"})
    
    output = []
    for workout in workouts:
        workout_dic = {}
        workout_dic['calories_burned'] = workout.calories_burned
        workout_dic['duration'] = workout.duration
        workout_dic['date'] = workout.date
        workout_dic['type_of_workout'] = workout.type_of_workout
        output.append(workout_dic)
    flash("Workout Created Successfully!", category="success") 
    return jsonify(output)



@app.route("/settings")
@login_required
def settings():
    workouts = Workout.query.all()
    calories = []
    duration = []
    for workout in workouts:
        calories_count = workout.calories_burned
        duration_count = workout.duration
        calories.append(float(calories_count))
        duration.append(float(duration_count))
    total_cal = sum(calories)
    total_dur = sum(duration)
    return render_template("settings.html", users=current_user,total_cal=total_cal, total_dur=total_dur)



@app.route('/uploads', methods=['POST'])
@login_required
def upload_file():
    if 'image' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Return the file path to the client
        return jsonify({'message': 'File uploaded successfully', 'path': f'static/uploads/{filename}'}), 200

    return jsonify({'message': 'Invalid file format'}), 400




@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout Successfully", category="success")
    return redirect("login")

if __name__ == "__main__":
    app.run()
