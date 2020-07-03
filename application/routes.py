from application import app, db, api
from flask import render_template, request, Response, json, flash, redirect, get_flashed_messages, url_for, session, jsonify
from application.models import User, Courses, Enrollment
from application.forms import LoginForm, RegisterForm
from flask_restplus import Resource

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)

@api.route('/api/', '/api')
class GetAndPost(Resource):
    def get(self):
        return jsonify(User.objects.all())
    
    def post(self):
        data = api.payload
        user = User(user_id=data['user_id'], email=data['email'], first_name=data['first_name'], last_name=data['last_name'])
        user.set_password(data['password'])
        user.save()
        return jsonify(User.objects(user_id=data['user_id']))


@api.route('/api/<idx>')
class GetPutDelete(Resource):
    def get(self, idx):
        return jsonify(User.objects(user_id=idx))

    def put(self, idx):
        data = api.payload
        User.objects(user_id=idx).update(**data)
        return jsonify(User.objects(user_id=idx))

    def delete(self, idx):
        User.objects(user_id=idx).delete()
        return jsonify(User.objects(user_id=idx))

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('username'):
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.objects(email=email).first()
        if user and user.get_password(password):
            flash("You are successfully logged in!","success")
            session['user_id'] = user.user_id
            session['username'] = user.first_name
            return redirect("/index")
        else:
            flash("Sorry, something went wrong!","danger")
    return render_template("login.html", form=form, title="Login", login=True)

@app.route("/logout")
def logout():
    session['user_id'] = False
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/courses/")
@app.route("/courses/<term>")
def courses(term=None):
    if term is None:
        term = "Spring 2019"
    classes = Courses.objects.all()
    return render_template("courses.html", courseData=classes, courses = True, term=term )

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get('username'):
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user_id = User.objects.count()+1
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        print("User ID",user_id)
        user.save()
        flash("You are successfully registered!","success")
        return redirect(url_for('register'))
        # return redirect("/index")
    return render_template("register.html", form=form, title="New User Registration", register=True)

@app.route("/enrollment", methods=["GET","POST"])
def enrollment():

    if not session.get('username'):
        return redirect(url_for('login'))

    courseID = request.form.get('courseID')
    courseTitle = request.form.get('title')
    user_id = session.get('user_id')

    if courseID:
        if Enrollment.objects(user_id=user_id,courseID=courseID):
            flash(f"Oops! You are already registered in this course {courseTitle}!", "danger")
            return redirect(url_for("courses"))
        else:
            Enrollment(user_id=user_id,courseID=courseID).save()
            flash(f"You are enrolled in {courseTitle}!", "success")

    classes = list( User.objects.aggregate(*[
            {
                '$lookup': {
                    'from': 'enrollment', 
                    'localField': 'user_id', 
                    'foreignField': 'user_id', 
                    'as': 'r1'
                }
            }, {
                '$unwind': {
                    'path': '$r1', 
                    'includeArrayIndex': 'r1_id', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$lookup': {
                    'from': 'course', 
                    'localField': 'r1.courseID', 
                    'foreignField': 'courseID', 
                    'as': 'r2'
                }
            }, {
                '$unwind': {
                    'path': '$r2', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$match': {
                    'user_id': user_id
                }
            }, {
                '$sort': {
                    'courseID': 1
                }
            }
        ]))

    return render_template("enrollment.html", enrollment=True, title="Enrollment", classes=classes)

# @app.route("/api/")
# @app.route("/api/<idx>")
# def api(idx=None):
#     if idx == None:
#         data = json_data
#     else:
#         data = json_data[int(idx)]
#     return Response(json.dumps(data), mimetype="application/json")

@app.route("/user")
def user():
    # User(user_id=1, first_name="Shaurya", last_name="Airi", email="shauryaairi@gmail.com", password="abc1234").save()
    # User(user_id=2, first_name="Shreya", last_name="Airi", email="shreyaairi@gmail.com", password="abc1234xyz").save()
    users = User.objects.all()
    return render_template("user.html", users=users)
