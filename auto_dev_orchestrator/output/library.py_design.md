# `library.py` – Backend Design for Simple Library Management System

This document provides a complete technical design for a Python module `library.py` implementing a simple library management system. The design uses object-oriented principles, keeping the entire logic in a single file for manageable scope and direct testability. All data storage is done in-memory using Python built-in types for simplicity, but easily adaptable to persistent storage.

---

## Module Structure Overview

- One main entry class: `Library`
- Supporting domain classes: `Member`, `Book`, `BorrowRecord`
- Internal error classes for robust error handling
- Helper functions for date/time, fine calculation, and report formatting

---

## Classes

### 1. `Library`

#### Responsibilities

- System-level interface: manages members, books, and transactions
- Manages in-memory collections for members, books, and borrowing records
- Provides registration, book management, borrow/return operations, and reporting
- Validates business rules – book availability, borrow/return constraints, fine assessment

#### Key Attributes

- `self.members: Dict[int, Member]` — Maps member ID to Member objects
- `self.books: Dict[int, Book]` — Maps book ID to Book objects
- `self.borrow_records: List[BorrowRecord]` — Complete list of current and historical borrow records
- `self.next_member_id: int` — Autoincrement member ID
- `self.next_book_id: int` — Autoincrement book ID

#### Core Methods

- `register_member(name: str, contact: str) -> int`
- `update_member(member_id: int, name: Optional[str]=None, contact: Optional[str]=None) -> None`
- `remove_member(member_id: int) -> None`

- `add_book(title: str, author: str, total_copies: int) -> int`
- `remove_book(book_id: int) -> None`
- `update_book(book_id: int, title: Optional[str]=None, author: Optional[str]=None, total_copies: Optional[int]=None) -> None`

- `borrow_book(member_id: int, book_id: int, borrow_date: date, due_days: int=14) -> int`
- `return_book(member_id: int, book_id: int, return_date: date) -> float`

- `get_borrowed_books() -> List[Dict]`
- `get_overdue_books(current_date: date) -> List[Dict]`
- `get_member_info(member_id: int) -> Dict`
- `get_book_info(book_id: int) -> Dict`

#### Data Flow

- Members and books are referenced by integer IDs for simplicity.
- Borrow and return operations create or update `BorrowRecord`s, enforcing constraints.
- Overdue and fine calculation accessed via reporting and `return_book`.

---

### 2. `Member`

#### Responsibilities

- Represents a library member.
- Stores personal info, supports account management.

#### Attributes

- `member_id: int`
- `name: str`
- `contact: str`

#### Methods

- None (directly managed by `Library`)

---

### 3. `Book`

#### Responsibilities

- Represents a book in the library collection.
- Tracks total and available copies.

#### Attributes

- `book_id: int`
- `title: str`
- `author: str`
- `total_copies: int`
- `available_copies: int`

#### Methods

- None (directly managed by `Library`)

---

### 4. `BorrowRecord`

#### Responsibilities

- Records each loan transaction between a member and a book.
- Tracks dates for due/return and fine calculation.

#### Attributes

- `record_id: int`
- `member_id: int`
- `book_id: int`
- `borrow_date: date`
- `due_date: date`
- `return_date: Optional[date]`
- `fine_paid: float`

#### Methods

- `is_overdue(current_date: date) -> bool`
- `calculate_fine(current_date: date, fine_per_day: float=1.0) -> float`

---

### 5. Exceptions

- `LibraryError(Exception)`: Base class
- `MemberNotFoundError(LibraryError)`
- `BookNotFoundError(LibraryError)`
- `BookUnavailableError(LibraryError)`
- `BorrowLimitError(LibraryError)`
- `BorrowRecordNotFoundError(LibraryError)`
- `InvalidOperationError(LibraryError)`

Custom exceptions provide clear feedback for API consumers and facilitate UI integrations.

---

## Key Methods — Descriptions

### Member Management

#### `register_member(name: str, contact: str) -> int`
- Registers a new member, assigning a unique ID.
- Returns the member ID.

#### `update_member(member_id: int, name: Optional[str]=None, contact: Optional[str]=None) -> None`
- Updates the member's details.
- Raises `MemberNotFoundError` if ID invalid.

#### `remove_member(member_id: int) -> None`
- Removes a member if they have no outstanding borrowed books.
- Raises `MemberNotFoundError`, `InvalidOperationError` as appropriate.

### Book Management

#### `add_book(title: str, author: str, total_copies: int) -> int`
- Adds a new book, assigning unique book ID.
- Returns the book ID.

#### `remove_book(book_id: int) -> None`
- Removes a book only if all copies are available (none currently borrowed).
- Raises `BookNotFoundError`, `InvalidOperationError`.

#### `update_book(book_id: int, title: Optional[str]=None, author: Optional[str]=None, total_copies: Optional[int]=None) -> None`
- Updates book details or adjusts copy count (not below currently borrowed).
- Raises `BookNotFoundError`, `InvalidOperationError`.

### Borrow/Return Operations

#### `borrow_book(member_id: int, book_id: int, borrow_date: date, due_days: int=14) -> int`
- Records a new loan transaction for a member and book.
- Checks availability and member existence.
- Book's `available_copies` decremented, `BorrowRecord` created.
- Returns unique record ID.
- Raises `MemberNotFoundError`, `BookNotFoundError`, `BookUnavailableError`, or `BorrowLimitError`.

#### `return_book(member_id: int, book_id: int, return_date: date) -> float`
- Member returns borrowed book.
- Updates related `BorrowRecord` with actual return date.
- Computes and returns fine if overdue.
- Raises `BorrowRecordNotFoundError`, `InvalidOperationError`.

### Reports

#### `get_borrowed_books() -> List[Dict]`
- Returns currently active borrow records with book & member info.

#### `get_overdue_books(current_date: date) -> List[Dict]`
- Returns all overdue books as of `current_date`, with full details.

#### `get_member_info(member_id: int) -> Dict`
- Returns member account info, current borrows & any fines due.

#### `get_book_info(book_id: int) -> Dict`
- Returns book details, copies status, and any active borrows.

---

## Additional Design Details

### Constants

- `DEFAULT_DUE_DAYS = 14` — Standard loan period (2 weeks)
- `FINE_PER_DAY = 1.0` — Default fine per overdue day

### Thread Safety
- No explicit threading support (designed for single-process or sequential UI).

### Date Handling
- Assumes Python `datetime.date` type for all dates.
- UI layer is responsible for date formatting and parsing.

### Invariants

- A book cannot be borrowed if no copies are available.
- Cannot borrow same book by same member if unreturned.
- Cannot return a book not currently borrowed by that member.
- Cannot remove member or book if active borrows exist.

### Constraints

- All IDs (member, book, borrow record) are positive integers, auto-incremented.
- The module is ready for direct unit testing and UI integration.
- No persistent storage; could be extended with DB adapters if required.

---

## Summary Table

| Functionality                           | Method(s)                                 | Business Rules/Notes                                             |
|------------------------------------------|-------------------------------------------|------------------------------------------------------------------|
| Register/Update/Remove Member            | `register_member`, `update_member`, `remove_member` | No outstanding borrows to remove.                                |
| Add/Update/Remove Book                   | `add_book`, `update_book`, `remove_book`  | All copies must be in to remove.                                 |
| Borrow Book                              | `borrow_book`                             | Must have available copy. One outstanding borrow per member-book |
| Return Book                              | `return_book`                             | Must exist. Fine if overdue.                                     |
| Overdue/Fine Tracking                    | `BorrowRecord.calculate_fine`, `get_overdue_books` | Customizable fine rate.                                          |
| Reporting                                | `get_borrowed_books`, `get_overdue_books`, `get_member_info`, `get_book_info` | Book/member linked data.                                         |

---

## Example Usage Flow

1. Register member(s)
2. Add book(s)
3. Member borrows book; due date is set
4. Member returns book; fine is calculated if past due
5. Library generates reports as required

---

This design endeavors to maximize clarity, maintainability, and direct implementability for the backend developer.