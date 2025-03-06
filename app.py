from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    copies = db.Column(db.Integer, nullable=False)
    available_copies = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    borrowed_count = db.Column(db.Integer, default=0)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class Borrowing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.now)
    due_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)  # Assuming user IDs are stored
    rating = db.Column(db.Integer, nullable=False)  # Rating from 1 to 5
    review = db.Column(db.Text, nullable=True)  # Optional review text
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    book = db.relationship('Book', backref=db.backref('reviews', lazy=True))


# Routes

# Get all users
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User added successfully!", "user_id": new_user.id}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{"id": user.id, "name": user.name, "email": user.email} for user in users]
    return jsonify(users_list), 200

# Get all books
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "copies": book.copies,
        "available_copies": book.available_copies,
        "rating": book.rating
    } for book in books])

# Get a single book by ID
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify({
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "copies": book.copies,
        "available_copies": book.available_copies,
        "rating": book.rating
    })

# Add a new book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    
    # Check if a book with the same ISBN already exists
    existing_book = Book.query.filter_by(isbn=data['isbn']).first()
    if existing_book:
        return jsonify({"error": "Book with this ISBN already exists!"}), 400
    
    # Create a new book entry
    new_book = Book(
        isbn=data['isbn'],
        title=data['title'],
        author=data['author'],
        genre=data['genre'],
        copies=data['copies'],
        available_copies=data['copies']
    )
    
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added successfully!"}), 201


# Update a book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404
    
    data = request.get_json()
    
    # Update only if the data exists in the request
    if 'isbn' in data:
        book.isbn = data['isbn']
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'genre' in data:
        book.genre = data['genre']
    if 'copies' in data:
        book.copies = data['copies']
    if 'available_copies' in data:
        book.available_copies = data['available_copies']
    if 'rating' in data:
        book.rating = data['rating']
    
    db.session.commit()
    
    return jsonify({"message": "Book updated successfully!"}), 200


# Delete a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def remove_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book removed successfully"}), 200


# Borrow a book
@app.route('/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json()
    user_id = data.get('user_id')
    book_id = data.get('book_id')

    # Check if the user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found!"}), 404

    # Check if the book exists
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found!"}), 404

    # Check if the user has already borrowed the same book
    existing_borrowing = Borrowing.query.filter_by(user_id=user_id, book_id=book_id, return_date=None).first()
    if existing_borrowing:
        return jsonify({"message": "You have already borrowed this book!"}), 400

    # Check if the book is available
    if book.available_copies <= 0:
        return jsonify({"message": "No copies available for borrowing!"}), 400

    # Borrowing
    book.available_copies -= 1
    book.borrowed_count += 1  # Track how many times the book has been borrowed
    borrowing = Borrowing(
        user_id=user_id,
        book_id=book_id,
        due_date=datetime.now() + timedelta(days=14)
    )

    db.session.add(borrowing)
    db.session.commit()

    return jsonify({
        "message": "Book borrowed successfully!",
        "borrow_id": borrowing.id,
        "due_date": borrowing.due_date.strftime('%Y-%m-%d %H:%M:%S')
    }), 200



# Get borrowed books by user ID
@app.route('/borrowed-books/<int:user_id>', methods=['GET'])
def get_borrowed_books(user_id):
    borrowings = Borrowing.query.filter_by(user_id=user_id, return_date=None).all()
    
    if not borrowings:
        return jsonify({"message": "No books borrowed"}), 200  

    borrowed_books = []
    for borrowing in borrowings:
        book = Book.query.get(borrowing.book_id)
        if book:
            borrowed_books.append({
                "borrow_id": borrowing.id,
                "book_id": book.id,
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "borrow_date": borrowing.borrow_date.strftime('%Y-%m-%d %H:%M:%S'),
                "due_date": borrowing.due_date.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return jsonify(borrowed_books)


# Search books by title
@app.route('/books/search_by_title', methods=['GET'])
def search_books_by_title():
    title = request.args.get('title')

    if not title:
        return jsonify({"error": "Title parameter is required"}), 400

    books = Book.query.filter(Book.title.ilike(f"%{title}%")).all()

    if not books:
        return jsonify({"message": "No books found with this title"}), 404

    return jsonify([
        {
            "id": book.id,
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "available_copies": book.available_copies
        }
        for book in books
    ]), 200


# Add a review for a book
@app.route('/books/<int:book_id>/review', methods=['POST'])
def add_review(book_id):
    data = request.get_json()

    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Create and add the new review
    new_review = Review(
        book_id=book_id,
        user_id=data['user_id'],
        rating=data['rating'],
        review=data['review']
    )
    db.session.add(new_review)
    db.session.commit()

    # Recalculate the book's average rating
    reviews = Review.query.filter_by(book_id=book_id).all()
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        avg_rating = 0  # In case all reviews get deleted

    # Update the book's rating
    book.rating = round(avg_rating, 2)  # Keep it to 2 decimal places
    db.session.commit()

    return jsonify({"message": "Review added successfully!", "new_average_rating": book.rating}), 201



# Get reviews for a book
@app.route('/books/<int:book_id>/reviews', methods=['GET'])
def get_reviews(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    reviews = Review.query.filter_by(book_id=book_id).all()
    if not reviews:
        return jsonify({"message": "No reviews yet for this book."}), 200

    avg_rating = sum([review.rating for review in reviews]) / len(reviews)

    return jsonify({
        "book_id": book_id,
        "title": book.title,
        "average_rating": round(avg_rating, 2),
        "reviews": [
            {
                "user_id": review.user_id,
                "rating": review.rating,
                "review": review.review,
                "timestamp": review.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for review in reviews
        ]
    })


# Rate a book
@app.route('/rate-book', methods=['POST'])
def rate_book():
    data = request.get_json()
    book = Book.query.get(data['book_id'])
    if not book:
        return jsonify({"message": "Book not found!"}), 404
    book.rating = data['rating']
    db.session.commit()
    return jsonify({"message": "Rating updated!"}), 200


# Return a book and update the borrowed books list
@app.route('/return', methods=['POST'])
def return_book():
    data = request.get_json()
    user_id = data.get('user_id')
    book_id = data.get('book_id')

    # Find the active borrowing record
    borrowing = Borrowing.query.filter_by(user_id=user_id, book_id=book_id, return_date=None).first()
    
    if not borrowing:
        return jsonify({"message": "No active borrowing found for this book!"}), 400
    
    # Update borrowing record with return date
    borrowing.return_date = datetime.now()

    # Update book's available copies
    book = Book.query.get(book_id)
    if book:
        book.available_copies += 1

    db.session.commit()

    return jsonify({"message": "Book returned successfully!"}), 200


# Get all returned books by user ID
@app.route('/returned-books/<int:user_id>', methods=['GET'])
def get_returned_books(user_id):
    returned_books = Borrowing.query.filter_by(user_id=user_id).filter(Borrowing.return_date.isnot(None)).all()
    
    if not returned_books:
        return jsonify({"message": "No books returned"}), 200  

    books_list = []
    for borrowing in returned_books:
        book = Book.query.get(borrowing.book_id)
        if book:
            books_list.append({
                "borrow_id": borrowing.id,
                "book_id": book.id,
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "borrow_date": borrowing.borrow_date.strftime('%Y-%m-%d %H:%M:%S'),
                "return_date": borrowing.return_date.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return jsonify(books_list), 200


# Suggest books by genre with optional filters
@app.route('/books/suggest_by_genre', methods=['GET'])
def suggest_books_by_genre():
    genre = request.args.get('genre')  # Get the genre from query parameters
    min_rating = request.args.get('min_rating', type=float)  # Optional: Minimum rating
    available_only = request.args.get('available_only', default=False, type=lambda v: v.lower() == 'true')  # Optional: Available copies only

    if not genre:
        return jsonify({"error": "Genre parameter is required"}), 400

    # Base query
    query = Book.query.filter(Book.genre.ilike(f"%{genre}%"))

    # Apply optional filters
    if min_rating is not None:
        query = query.filter(Book.rating >= min_rating)
    if available_only:
        query = query.filter(Book.available_copies > 0)

    # Execute the query
    books = query.all()

    if not books:
        return jsonify({"message": f"No books found in the genre: {genre}"}), 404

    # Return the list of books
    return jsonify([
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "available_copies": book.available_copies,
            "rating": book.rating
        }
        for book in books
    ]), 200


# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
