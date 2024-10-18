import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{os.path.join(BASE_DIR, 'library.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')

# Initialize the database
db = SQLAlchemy(app)

# Create upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    cover_image = db.Column(db.String(200), nullable=False)


# Create the database tables when the app starts
with app.app_context():
    db.create_all()


# Function to retrieve a book by ID
def get_book_by_id(book_id):
    return Book.query.get(book_id)  # Retrieve the book


# Route to display books
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)


# Route to add a new book
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        rating = request.form['rating']
        cover = request.files['cover']

        if cover:
            filename = secure_filename(cover.filename)  # Sanitize filename
            cover.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Create a new book entry
            new_book = Book(title=title, author=author, rating=rating, cover_image=filename)
            db.session.add(new_book)
            db.session.commit()

        return redirect(url_for('index'))

    return render_template('add.html')


# Route to delete a book
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('index'))


# Route to edit a book rating
@app.route('/edit_rating/<int:book_id>', methods=['GET', 'POST'])
def edit_rating(book_id):
    book = get_book_by_id(book_id)  # Retrieve the book using the function
    if request.method == 'POST':
        new_rating = request.form['new_rating']
        if book:  # Check if the book exists
            book.rating = new_rating  # Update the rating
            db.session.commit()  # Commit the changes to the database
            return redirect(url_for('index'))  # Redirect back to the main page after updating
    return render_template('edit_rating.html', book=book)  # Render the edit form


if __name__ == '__main__':
    app.run(debug=True)
