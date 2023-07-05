# Utility functions that are called to perform tasks when respective buttons are pressed.
from datetime import datetime, timedelta
from models import User, Movie, Borrow, db
from flask import flash
from fpdf import FPDF
import os

# Utility function to implement necessary changes in the database when a movie is rented.
def rent_movie(user_id, movie_id):
    try:
        #get movie details
        user_obj = User.query.filter_by(id=user_id).first() #sure to exist
        movie_obj = Movie.query.filter_by(id=movie_id).first()
        if movie_obj is not None:    
            #check for funds, and stock, and existence of movie
            if user_obj.balance < movie_obj.price :
                raise ValueError("Insufficient Balance")
            elif movie_obj.stock < 1 :
                raise ValueError("Insufficient Quantity in Stock")
            else:
                my_order = Borrow(user_id = user_obj.id, movie_id = movie_id, borrow_date=datetime.utcnow(), deadline=datetime.utcnow()+timedelta(days=30))
                movie_obj.stock -= 1
                user_obj.balance -= movie_obj.price
                db.session.add(my_order)
                user_obj.lastmovie=movie_obj.title
                db.session.commit()
                flash('Congratulations. Movie Rented Successful')
                generate_receipt(my_order.id)
        else:
            raise ValueError("Movie Not Found!")

    except ValueError as e:
        flash(e)

# Utility function to generate a PDF receipt of the order of a user.
def generate_receipt(order_id):
    try:
        order_obj = Borrow.query.filter_by(id=order_id).first()
        movie_obj = Movie.query.filter_by(id=order_obj.movie_id).first()
        user_obj = User.query.filter_by(id=order_obj.user_id).first()

        if order_obj is not None and movie_obj is not None and user_obj is not None:
            receipt = FPDF()
            receipt.add_page()
            receipt.set_font('Arial', 'B', 16)
            receipt.cell(200, 10, 'VRS Movie Rentals', 0, 1, 'C')
            receipt.cell(200, 10, 'Receipt', 0, 1, 'C')
            # receipt.image(movie_obj.posterpath, x=98, w=15, h=25)
            receipt.set_font('Arial', '', 12)
            receipt.cell(200, 10, 'Order ID: {}'.format(order_obj.id), 0, 1, 'L')
            receipt.cell(200, 10, txt=f"Customer ID: {order_obj.user_id}", ln=1, align="L")
            receipt.cell(200, 10, txt=f"Customer Name: {user_obj.name}", ln=1, align="L")
            receipt.cell(200, 10, txt=f"Movie ID: {order_obj.movie_id}", ln=1, align="L")   
            receipt.cell(200, 10, txt=f"Movie Name: {movie_obj.title}", ln=1, align="L")
            receipt.cell(200, 10, txt=f"Movie Genre: {movie_obj.genre}", ln=1, align="L")
            receipt.cell(200, 10, txt=f" Date: {order_obj.borrow_date}", ln=1, align="L")
            receipt.set_font('Arial', 'B', 16)
            receipt.cell(200, 10, txt=f"Total Price: {movie_obj.price}", ln=1, align="C")

            if not os.path.exists('Receipts'):
                os.makedirs('Receipts')
            receipt.output("Receipts/receipt" + str(order_obj.id)+".pdf")
            flash("Receipt Generated Successfully and downloaded.")
        
        else:
            raise KeyError("Order Not Found!")
    except KeyError as e:
        flash(e)

# Utility function to return an outstanding order.
def return_movie(order_id, rating, people):
    try:
        
        order_obj = Borrow.query.filter_by(id=order_id).first()

        if order_obj is not None:
            movie_obj.rating=((movie_obj.rating*(people-1))+rating)/people
            movie_obj = Movie.query.filter_by(id=order_obj.movie_id).first()
            movie_obj.stock += 1
            db.session.commit()
            flash("Movie returned successfully.")
        else:
            raise ValueError("Order Not Found!")

    except ValueError as e:
        flash(e)

# Utility function to return a list of all orders that the user has created on the VRS.
def view_orders(user_id):
    try:
        user_obj = User.query.filter_by(id=user_id).first()

        if user_obj is not None:
            return(Borrow.query.filter_by(user_id=user_id))
        else:
            raise KeyError("User Not Found!")

    except KeyError as e:
        flash(e)
    return None

#add a movie to database
def add_movie(title, stock, genre="", rating=0, year=0, img_path="https://img.lovepik.com/background/20211029/medium/lovepik-film-festival-simple-shooting-videotape-poster-background-image_605811936.jpg", price=0, overview=""):
    try:
        movie_obj = Movie.query.filter_by(title=title).first()
        if movie_obj is not None:
            movie_obj.stock += stock
            if price!=0:
                movie_obj.price = price
            db.session.commit()
        else:
            movie_obj = Movie(title=title, genre=genre, rating=rating, price=price, stock=stock, year=year, posterpath=img_path, overview=overview)
            db.session.add(movie_obj)
            db.session.commit()
            flash("Movie Added Successfully!")
    except ValueError as e:
        flash(e)
