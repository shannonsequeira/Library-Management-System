import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Constants
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes?q=fiction"

# Function to fetch book data from Google Books API
def fetch_books(search_term=None):
    query = search_term if search_term else "fiction"
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}")
    data = response.json()
    books = []
    for item in data.get('items', []):
        volume_info = item.get('volumeInfo', {})
        book = {
            'title': volume_info.get('title', 'No Title'),
            'author': ', '.join(volume_info.get('authors', [])),
            'isbn': next((identifier.get('identifier') for identifier in volume_info.get('industryIdentifiers', []) if identifier.get('type') == 'ISBN_13'), 'No ISBN'),
            'cover_url': volume_info.get('imageLinks', {}).get('thumbnail', ''),
            'status': 'Available'
        }
        books.append(book)
    return books

# Initialize session state
if 'books' not in st.session_state:
    st.session_state.books = fetch_books()

# Function to fetch book cover image from URL
def fetch_image(image_url):
    try:
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        return image
    except Exception as e:
        st.error(f"Error fetching image: {e}")
        return None

# Streamlit app
st.markdown("""
<style>
.main { background-color: #f5f5f5; }
.sidebar { background-color: #2d2d2d; color: white; }
.stButton>button { background-color: #007bff; color: white; }
.stButton>button:hover { background-color: #0056b3; }
.stTextInput>input { border-radius: 5px; }
.card { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 5px; background-color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 200px; }
.card img { border-radius: 8px; width: 100%; height: auto; }
.container { display: flex; flex-wrap: wrap; }
.sidebar .stSidebar [class*="sidebar"] { background-color: #333; }
.sidebar .stSidebar [class*="sidebar"] a { color: white; }
.sidebar .stSidebar [class*="sidebar"] a:hover { color: #007bff; }
</style>
""", unsafe_allow_html=True)

st.title('Library Management System')

# Sidebar with icons
st.sidebar.markdown("""
<style>
.sidebar {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.sidebar h2 {
    color: white;
}
.sidebar a {
    color: #ffffff;
    text-decoration: none;
    font-size: 16px;
    padding: 10px;
    display: flex;
    align-items: center;
}
.sidebar a:hover {
    background-color: #444;
    border-radius: 5px;
}
.sidebar i {
    margin-right: 10px;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title('Navigation')
app_mode = st.sidebar.radio(
    label="Navigation Menu",  # Non-empty label for accessibility
    options=[
        "View All Books",
        "Add Book",
        "Update Book",
        "Delete Book",
        "Search Books",
        "Borrow Book"
    ],
    label_visibility="collapsed"  # Hide label visually
)

# Assign icons to each mode
icons = {
    "View All Books": "📚",
    "Add Book": "➕",
    "Update Book": "✏️",
    "Delete Book": "🗑️",
    "Search Books": "🔍",
    "Borrow Book": "🛒"
}

# Use the selected app mode
st.sidebar.markdown(f"**{icons[app_mode]} {app_mode}**")

if app_mode == "View All Books":
    st.header("All Books")
    st.write("Displaying books fetched from Google Books API.")
    cols = st.columns(3)  # Adjust column number based on desired grid width

    with st.container():
        st.markdown('<div class="container">', unsafe_allow_html=True)
        for i, book in enumerate(st.session_state.books):
            with cols[i % 3]:  # Distribute cards across columns
                st.markdown(f"""
                <div class="card">
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>ISBN:</strong> {book['isbn']}</p>
                    <p><strong>Status:</strong> {book['status']}</p>
                    <img src="{book['cover_url']}" alt="{book['title']}">
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif app_mode == "Add Book":
    st.header("Add a New Book")
    with st.form("add_book_form"):
        book_title = st.text_input(
            label="Title",  # Non-empty label for accessibility
            placeholder="Enter the title of the book",
            value=""
        )
        book_author = st.text_input(
            label="Author",  # Non-empty label for accessibility
            placeholder="Enter the author of the book",
            value=""
        )
        book_isbn = st.text_input(
            label="ISBN",  # Non-empty label for accessibility
            placeholder="Enter the ISBN of the book",
            value=""
        )
        book_cover_url = st.text_input(
            label="Book Cover Image URL",  # Non-empty label for accessibility
            placeholder="Enter the URL of the book cover image",
            value=""
        )
        submit_button = st.form_submit_button("Add Book")
        
        if submit_button:
            if all([book_title, book_author, book_isbn, book_cover_url]):
                image = fetch_image(book_cover_url)
                if image:
                    new_book = {"title": book_title, "author": book_author, "isbn": book_isbn, "cover_url": book_cover_url, "status": "Available"}
                    st.session_state.books.append(new_book)
                    st.success(f'Book "{book_title}" added successfully!')
                else:
                    st.error("Failed to add book cover image.")
            else:
                st.error("Please fill all fields.")

elif app_mode == "Update Book":
    st.header("Update Book Details")
    with st.form("update_book_form"):
        isbn_to_update = st.text_input(
            label="Enter ISBN of the book to update",  # Non-empty label for accessibility
            placeholder="Enter the ISBN of the book you want to update",
            value=""
        )
        book_title = st.text_input(
            label="New Title",  # Non-empty label for accessibility
            placeholder="Enter the new title (optional)",
            value=""
        )
        book_author = st.text_input(
            label="New Author",  # Non-empty label for accessibility
            placeholder="Enter the new author (optional)",
            value=""
        )
        book_cover_url = st.text_input(
            label="New Book Cover Image URL",  # Non-empty label for accessibility
            placeholder="Enter the new cover image URL (optional)",
            value=""
        )
        status = st.selectbox(
            label="Status",  # Non-empty label for accessibility
            options=["Available", "Borrowed"]
        )
        submit_button = st.form_submit_button("Update Book")

        if submit_button:
            if isbn_to_update:
                book_found = False
                for book in st.session_state.books:
                    if book['isbn'] == isbn_to_update:
                        if book_title:
                            book['title'] = book_title
                        if book_author:
                            book['author'] = book_author
                        if book_cover_url:
                            book['cover_url'] = book_cover_url
                        book['status'] = status
                        st.success(f'Book "{isbn_to_update}" updated successfully!')
                        book_found = True
                        break
                if not book_found:
                    st.error("Book not found.")
            else:
                st.error("Please enter ISBN of the book to update.")

elif app_mode == "Delete Book":
    st.header("Delete a Book")
    with st.form("delete_book_form"):
        isbn_to_delete = st.text_input(
            label="Enter ISBN of the book to delete",  # Non-empty label for accessibility
            placeholder="Enter the ISBN of the book you want to delete",
            value=""
        )
        submit_button = st.form_submit_button("Delete Book")

        if submit_button:
            if isbn_to_delete:
                book_found = False
                for book in st.session_state.books:
                    if book['isbn'] == isbn_to_delete:
                        st.session_state.books.remove(book)
                        st.success(f'Book "{isbn_to_delete}" deleted successfully!')
                        book_found = True
                        break
                if not book_found:
                    st.error("Book not found.")
            else:
                st.error("Please enter ISBN of the book to delete.")

elif app_mode == "Search Books":
    st.header("Search Books")
    search_term = st.text_input(
        label="Search Term",  # Non-empty label for accessibility
        placeholder="Enter title, author, or ISBN to search",
        value=""
    )
    search_button = st.button("Search")

    if search_button:
        if search_term:
            results = fetch_books(search_term)
            if results:
                st.write("Search results:")
                for book in results:
                    st.write(f"Title: {book['title']}, Author: {book['author']}, ISBN: {book['isbn']}")
            else:
                st.write("No results found.")
        else:
            st.error("Please enter a search term.")

elif app_mode == "Borrow Book":
    st.header("Borrow a Book")
    with st.form("borrow_book_form"):
        isbn_to_borrow = st.text_input(
            label="Enter ISBN of the book to borrow",  # Non-empty label for accessibility
            placeholder="Enter the ISBN of the book you want to borrow",
            value=""
        )
        submit_button = st.form_submit_button("Borrow Book")

        if submit_button:
            if isbn_to_borrow:
                book_found = False
                for book in st.session_state.books:
                    if book['isbn'] == isbn_to_borrow:
                        if book['status'] == "Available":
                            book['status'] = "Borrowed"
                            st.success(f'Book "{book["title"]}" borrowed successfully!')
                        else:
                            st.error("Book is already borrowed.")
                        book_found = True
                        break
                if not book_found:
                    st.error("Book not found.")
            else:
                st.error("Please enter ISBN of the book to borrow.")
