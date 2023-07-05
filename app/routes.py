from flask import Flask, redirect , url_for , render_template , request
import pickle
from functions import *
from models import app, db, Movie, User, Staff, Borrow
import pandas as pd
from flask_mail import Mail, Message

mail=Mail(app)

uni="Prasanna"
with open("recommender_models/rec_model", "rb") as file:
    recommendations = pickle.load(file)
#entry page
@app.route("/")
def home():
  df = pd.read_csv('/home/parthiv/Downloads/VRS/archive/reduced_movie_metadata.csv', low_memory=False)
  for index, row in df.iterrows():
    if str(row['poster_path']).startswith("/"):
      row['poster_path'] = "https://img.lovepik.com/background/20211029/medium/lovepik-film-festival-simple-shooting-videotape-poster-background-image_605811936.jpg"
    movie = Movie(title=row['title'], year=row['release_date'], genre=row['genres'], posterpath=row['poster_path'], overview=row['overview'], stock=10, price=100)
    db.session.add(movie)
  db.session.commit()
  return render_template("_login.html")

#login page 
@app.route("/login", methods =['POST','GET'])
def login():
  if request.method=='POST':
    Username=request.form['username']
    global uni
    uni=Username
    Password=request.form['password']
  
    if User.query.filter_by(name=Username).first() is not None:
      if Password==(User.query.filter_by(name=Username).first()).password:
        if (User.query.filter_by(name=Username).first()).lastmovie is None:
          lastmovie="Jumanji"
          titles=recommendations[lastmovie]
          links=[(Movie.query.filter_by(title=movie).first()).posterpath for movie in titles]
          return render_template("_home.html", movie_titles=recommendations["Jumanji"], movie_links=links, length=len(links), user=Username)
        lastmovie=(User.query.filter_by(name=Username).first()).lastmovie
        titles=recommendations[lastmovie]
        links=[(Movie.query.filter_by(title=movie).first()).posterpath for movie in titles]
        return render_template("_home.html", movie_titles=titles, movie_links=links, length=len(links), user=Username)
      else:
        return render_template("_login.html", warn="y")
      
    elif User.query.filter_by(name=Username).first() is None:
      return render_template("_login.html", warn="y")
 
  return render_template("_login.html", warn="n")

#taking data from staff 
@app.route("/staff_login", methods =['POST','GET'])
def staff_login():
  if request.method=='POST':
    Username=request.form['username']
    Password=request.form['password']
    if Staff.query.filter_by(name=Username).first() is not None:
      if Password==(Staff.query.filter_by(name=Username).first()).password:
        orders=Borrow.query.all()
        titles=[(Movie.query.filter_by(id=movie.movie_id).first()).title for movie in orders]
        deadline=[order.deadline for order in orders]
        uname=[(User.query.filter_by(id=order.user_id).first()).name for order in orders]
        uemail=[(User.query.filter_by(id=order.user_id).first()).email for order in orders]
        length=len(uname)
        return render_template("_staff.html", titles=titles, deadline=deadline, uname=uname, uemail=uemail, length=length)
      else:
        return render_template("_login_staff.html", warn="y")
      
    elif Staff.query.filter_by(name=Username).first() is None:
      return render_template("_login_staff.html", warn="y")
  return render_template("_login_staff.html", warn="n")

#taking data from manager login
@app.route("/manager_login", methods =['POST','GET'])
def manager_login():
  if request.method=='POST':
    Password=request.form['password']
    if Password=="admin":
      return render_template("_manager.html")
    else:
      return render_template("_login_manager.html", warn="y")
  return render_template("_login_manager.html", warn="n")

#taking data from create_acc
@app.route("/create_acc", methods =['POST','GET'])
def create_acc():
  if request.method=='POST':
    Username=request.form['username']
    global uni
    uni=Username
    Designation=request.form['user_cat']
    email=request.form['email']
    Password=request.form['password']
    rePassword=request.form['repassword']
    if Password==rePassword:
      if Designation=='User':
        user = User(name=Username, email=email, password=Password, lastmovie="Jumanji", balance=1000)
        db.session.add(user)
        db.session.commit()
        lastmovie="Jumanji"
        titles=recommendations[lastmovie]
        links=[(Movie.query.filter_by(title=movie).first()).posterpath for movie in titles]
        return render_template("_home.html", movie_titles=recommendations["Jumanji"], movie_links=links, length=len(links), user=Username)
      
      elif Designation=='Staff':
        staff = Staff(name=Username, email=email, password=Password)
        db.session.add(staff)
        db.session.commit()
        orders=Borrow.query.all()
        titles=[(Movie.query.filter_by(id=movie.movie_id).first()).title for movie in orders]
        deadline=[order.deadline for order in orders]
        uname=[(User.query.filter_by(id=order.user_id).first()).name for order in orders]
        uemail=[(User.query.filter_by(id=order.user_id).first()).email for order in orders]
        length=len(uname)
        return render_template('_staff.html', titles=titles, deadline=deadline, uname=uname, uemail=uemail, length=length)
    else:
      return render_template("_create_acc.html", warn="y")
  return render_template("_create_acc.html", warn="n")

#manager data
@app.route("/manager", methods =['POST','GET'])
def manager():
  if request.method=='POST':
    title=request.form['movieName']
    year=request.form['year']
    genre=request.form['genre']
    posterpath=request.form['posterpath']
    overview=request.form['overview']
    stock=request.form['stock']
    price=request.form['price']
    rating=request.form['rating']
    add_movie(title, stock, genre, rating, year, posterpath, price, overview)
  return render_template("_manager.html")
  

#route for deleting user for manager
@app.route("/deluser", methods =['POST','GET'])
def deluser():
  if request.method=='POST':
    Username=request.form['username']
    Designation=request.form['user_cat']
    if Designation=='User':
      User.query.filter_by(name=Username).delete()
      db.session.commit()
      return render_template("_deluser.html")
    elif Designation=='Staff':
      Staff.query.filter_by(name=Username).delete()
      db.session.commit()
      return render_template("_deluser.html")
  return render_template("_deluser.html")

#routing to staff.html
@app.route("/staff", methods =['POST','GET'])
def staff():
  return render_template("_staff.html")

#displaying list of movies and deadline taken by customer 
@app.route("/customer", methods =['POST','GET'])
def customer():
    rentals=Borrow.query.filter_by(user_id=(User.query.filter_by(name=uni).first()).id).all()
    titles=[(Movie.query.filter_by(id=movie.movie_id).first()).title for movie in rentals]
    id=[order.id for order in rentals]
    borrow_date=[order.borrow_date for order in rentals]
    deadline=[order.deadline for order in rentals]
    length=len(titles)
    balance=(User.query.filter_by(name=uni).first()).balance
    if request.method=="POST":
      rating=request.form['rating']
      titlesel= request.form['titlesel']
      movie=(Movie.query.filter_by(title=titlesel).first())
      movie.rating=float(movie.rating)+float(rating)
      db.session.commit()
      print(movie.rating)
      return render_template("_customer.html", id=id,balance=balance, titles=titles, borrow_date=borrow_date, deadline=deadline, length=length, user=uni)
    return render_template("_customer.html", id=id,balance=balance, titles=titles, borrow_date=borrow_date, deadline=deadline, length=length, user=uni)

#searching for a movie in database
@app.route('/search', methods=['GET', 'POST'])
def search():
  if request.method=='POST':
    inp=request.form['inp']
    if inp not in recommendations and Movie.query.filter_by(title=inp).first() is None:
      return render_template('blank_search.html', input=inp, movie_links=inp)
    elif inp not in recommendations:
      return render_template('search.html', input=inp, movie_links=(Movie.query.filter_by(title=inp).first()).posterpath, movie_titles=[inp], length=1)
    inplink=(Movie.query.filter_by(title=inp).first()).posterpath
    return render_template('search.html', input=inp, inplink=inplink, movie_titles=recommendations[inp], movie_links=[(Movie.query.filter_by(title=movie).first()).posterpath for movie in recommendations[inp]], length=len(recommendations[inp]))
  return render_template('search.html', input=inp, movie_links=[], length=0)

#redirect to view.html 
@app.route('/view/<title>', methods=['POST', 'GET'])
def view(title):
  if request.method=='POST':
    return redirect(url_for("rent", title=title, warn="n"))
  price=(Movie.query.filter_by(title=title).first()).price
  genre=(Movie.query.filter_by(title=title).first()).genre
  overview=(Movie.query.filter_by(title=title).first()).overview
  posterpath=(Movie.query.filter_by(title=title).first()).posterpath
  rating=(Movie.query.filter_by(title=title).first()).rating
  stock=(Movie.query.filter_by(title=title).first()).stock
  return render_template("_view.html", title=title, price=str(price), genre=str(genre), overview=overview, posterpath=str(posterpath), rating=str(rating), stock=str(stock))

#page to rent a movie
@app.route('/rent/<title>', methods=['POST', 'GET'])
def rent(title):
  price=(Movie.query.filter_by(title=title).first()).price
  genre=(Movie.query.filter_by(title=title).first()).genre
  overview=(Movie.query.filter_by(title=title).first()).overview
  posterpath=(Movie.query.filter_by(title=title).first()).posterpath
  rating=(Movie.query.filter_by(title=title).first()).rating
  stock=(Movie.query.filter_by(title=title).first()).stock
  if request.method=='POST':
    Username=request.form['username']
    if (Movie.query.filter_by(title=title).first()).stock==0:
      return render_template("_rent.html", title=title, price=str(price), genre=str(genre), overview=overview, posterpath=str(posterpath), rating=str(rating), stock=str(stock),warn="ystock")
    if (User.query.filter_by(name=Username).first()).balance<(Movie.query.filter_by(title=title).first()).price:
      return render_template("_rent.html", title=title, price=str(price), genre=str(genre), overview=overview, posterpath=str(posterpath), rating=str(rating), stock=str(stock),warn="ybalance")
    if User.query.filter_by(name=Username).first() is not None:
      rent_movie((User.query.filter_by(name=Username).first()).id, (Movie.query.filter_by(title=title).first()).id)
      rentals=Borrow.query.filter_by(user_id=(User.query.filter_by(name=Username).first()).id).all()
      titles=[(Movie.query.filter_by(id=movie.movie_id).first()).title for movie in rentals]
      id=[order.id for order in rentals]
      borrow_date=[order.borrow_date for order in rentals]
      deadline=[order.deadline for order in rentals]
      length=len(titles)
      balance=(User.query.filter_by(name=Username).first()).balance
      return render_template("_customer.html", id=id,balance=balance, titles=titles, borrow_date=borrow_date, deadline=deadline, length=length, user=uni)
  
  return render_template("_rent.html", title=title, price=str(price), genre=str(genre), overview=overview, posterpath=str(posterpath), rating=str(rating), stock=str(stock), warn="n")

#showing list of orders email to staff 
@app.route('/totalorders', methods=['POST', 'GET'])
def totalorders():
  orders=Borrow.query.all()
  titles=[(Movie.query.filter_by(id=movie.movie_id).first()).title for movie in orders]
  id=[order.id for order in orders]
  borrow_date=[order.borrow_date for order in orders]
  deadline=[order.deadline for order in orders]
  uid=[(User.query.filter_by(id=order.user_id).first()).id for order in orders]
  uname=[(User.query.filter_by(id=order.user_id).first()).name for order in orders]
  length=len(titles)
  return render_template("_totalorders.html", id=id, titles=titles, borrow_date=borrow_date, deadline=deadline, length=length, uid=uid, uname=uname)

#sending email to users by staff
@app.route('/sendmail', methods=['POST', 'GET'])
def sendmail():
  orders=Borrow.query.all()
  titles=[(Movie.query.filter_by(id=movie.movie_id).first()).title for movie in orders]
  deadline=[order.deadline for order in orders]
  uname=[(User.query.filter_by(id=order.user_id).first()).name for order in orders]
  uemail=[(User.query.filter_by(id=order.user_id).first()).email for order in orders]
  length=len(uname)
  if request.method=='POST':
    
    temp=request.form['recipients']
    message=request.form['message']
    all = request.form.get('allusers')
    Username=temp.split(',')
    
    
    if all=="User":
      emails=[user.email for user in User.query.all()]
      mail.send_message('User authentication', sender='vrslightmodecoders@gmail.com', recipients=emails, body=message)
    else:
      emails=[(User.query.filter_by(name=user).first()).email for user in Username]
      for user in Username:
        mail.send_message('User authentication', sender='vrslightmodecoders@gmail.com', recipients=emails, body=message)
    
    return render_template('_staff.html', titles=titles, deadline=deadline, uname=uname, uemail=uemail, length=length)
  return render_template('_staff.html', titles=titles, deadline=deadline, uname=uname, uemail=uemail, length=length)

if __name__== "__main__":
  app.run(debug=True)
