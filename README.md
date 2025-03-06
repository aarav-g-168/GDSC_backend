# Library Management API

This is a simple Flask-based Library Management API that supports user management, book borrowing, returning, reviewing, and searching functionalities.

## Setup

1. Install dependencies:
   ```sh
   pip install flask flask_sqlalchemy flask_cors
   ```

2. Run the application:
   ```sh
   python app.py
   ```

## API Endpoints & cURL Commands

### 1. Users

#### Add a User
- **Endpoint:** `POST /users`
- **cURL Command:**
  ```sh
  curl -X POST http://127.0.0.1:5000/users \
       -H "Content-Type: application/json" \
       -d '{"name": "John Doe", "email": "john@example.com"}'
  ```

#### Get All Users
- **Endpoint:** `GET /users`
- **cURL Command:**
  ```sh
  curl -X GET http://127.0.0.1:5000/users
  ```

### 2. Books

#### Add a Book
- **Endpoint:** `POST /books`
- **cURL Command:**
  ```sh
  curl -X POST http://127.0.0.1:5000/books \
       -H "Content-Type: application/json" \
       -d '{"isbn": "978-3-16-148410-0", "title": "Flask for Beginners", "author": "John Doe", "genre": "Programming", "copies": 5}'
  ```

#### Get All Books
- **Endpoint:** `GET /books`
- **cURL Command:**
  ```sh
  curl -X GET http://127.0.0.1:5000/books
  ```

#### Get a Single Book by ID
- **Endpoint:** `GET /books/<book_id>`
- **cURL Command:**
  ```sh
  curl -X GET http://127.0.0.1:5000/books/1
  ```

#### Update a Book
- **Endpoint:** `PUT /books/<book_id>`
- **cURL Command:**
  ```sh
  curl -X PUT http://127.0.0.1:5000/books/1 \
       -H "Content-Type: application/json" \
       -d '{"title": "Flask for Experts"}'
  ```

#### Delete a Book
- **Endpoint:** `DELETE /books/<book_id>`
- **cURL Command:**
  ```sh
  curl -X DELETE http://127.0.0.1:5000/books/1
  ```

### 3. Borrowing & Returning Books

#### Borrow a Book
- **Endpoint:** `POST /borrow`
- **cURL Command:**
  ```sh
  curl -X POST http://127.0.0.1:5000/borrow \
       -H "Content-Type: application/json" \
       -d '{"user_id": 1, "book_id": 1}'
  ```

#### Get Borrowed Books by User ID
- **Endpoint:** `GET /borrowed-books/<user_id>`
- **cURL Command:**
  ```sh
  curl -X GET http://127.0.0.1:5000/borrowed-books/1
  ```

#### Return a Book
- **Endpoint:** `POST /return`
- **cURL Command:**
  ```sh
  curl -X POST http://127.0.0.1:5000/return \
       -H "Content-Type: application/json" \
       -d '{"user_id": 1, "book_id": 1}'
  ```

### 4. Reviews

#### Add a Review
- **Endpoint:** `POST /books/<book_id>/review`
- **cURL Command:**
  ```sh
  curl -X POST http://127.0.0.1:5000/books/1/review \
       -H "Content-Type: application/json" \
       -d '{"user_id": 1, "rating": 5, "review": "Great book!"}'
  ```

#### Get Reviews for a Book
- **Endpoint:** `GET /books/<book_id>/reviews`
- **cURL Command:**
  ```sh
  curl -X GET http://127.0.0.1:5000/books/1/reviews
  ```

### 5. Search & Suggestions

#### Search Books by Title
- **Endpoint:** `GET /books/search_by_title?title=<query>`
- **cURL Command:**
  ```sh
  curl -X GET "http://127.0.0.1:5000/books/search_by_title?title=Flask"
  ```

#### Suggest Books by Genre
- **Endpoint:** `GET /books/suggest_by_genre?genre=<genre>&min_rating=<rating>&available_only=<true/false>`
- **cURL Command:**
  ```sh
  curl -X GET "http://127.0.0.1:5000/books/suggest_by_genre?genre=Programming&min_rating=4&available_only=true"
  ```

## Notes
- Make sure to replace `<book_id>`, `<user_id>`, and other parameters with actual values.
- Ensure that the Flask application is running before making API requests.
- Modify the database URI in `app.config['SQLALCHEMY_DATABASE_URI']` if necessary.

---
**Enjoy managing your library with this API!** 📚🚀
