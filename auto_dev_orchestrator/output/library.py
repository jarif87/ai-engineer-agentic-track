from datetime import date, timedelta
from typing import Dict, List, Optional

DEFAULT_DUE_DAYS = 14
FINE_PER_DAY = 1.0

class LibraryError(Exception):
    pass

class MemberNotFoundError(LibraryError):
    pass

class BookNotFoundError(LibraryError):
    pass

class BookUnavailableError(LibraryError):
    pass

class BorrowLimitError(LibraryError):
    pass

class BorrowRecordNotFoundError(LibraryError):
    pass

class InvalidOperationError(LibraryError):
    pass

class Member:
    def __init__(self, member_id: int, name: str, contact: str):
        self.member_id = member_id
        self.name = name
        self.contact = contact

class Book:
    def __init__(self, book_id: int, title: str, author: str, total_copies: int):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.total_copies = total_copies
        self.available_copies = total_copies

class BorrowRecord:
    def __init__(self, record_id: int, member_id: int, book_id: int, borrow_date: date, due_date: date):
        self.record_id = record_id
        self.member_id = member_id
        self.book_id = book_id
        self.borrow_date = borrow_date
        self.due_date = due_date
        self.return_date: Optional[date] = None
        self.fine_paid: float = 0.0

    def is_overdue(self, current_date: date) -> bool:
        return self.return_date is None and current_date > self.due_date

    def calculate_fine(self, current_date: date, fine_per_day: float = FINE_PER_DAY) -> float:
        if self.return_date:
            overdue_days = (self.return_date - self.due_date).days
        else:
            overdue_days = (current_date - self.due_date).days
        if overdue_days > 0:
            return overdue_days * fine_per_day
        return 0.0

class Library:
    def __init__(self):
        self.members: Dict[int, Member] = {}
        self.books: Dict[int, Book] = {}
        self.borrow_records: List[BorrowRecord] = []
        self.next_member_id: int = 1
        self.next_book_id: int = 1
        self.next_record_id: int = 1

    def register_member(self, name: str, contact: str) -> int:
        member_id = self.next_member_id
        self.next_member_id += 1
        self.members[member_id] = Member(member_id, name, contact)
        return member_id

    def update_member(self, member_id: int, name: Optional[str] = None, contact: Optional[str] = None) -> None:
        member = self.members.get(member_id)
        if not member:
            raise MemberNotFoundError("Member not found")
        if name is not None:
            member.name = name
        if contact is not None:
            member.contact = contact

    def remove_member(self, member_id: int) -> None:
        member = self.members.get(member_id)
        if not member:
            raise MemberNotFoundError("Member not found")
        for record in self.borrow_records:
            if record.member_id == member_id and record.return_date is None:
                raise InvalidOperationError("Member has active borrowed books")
        del self.members[member_id]

    def add_book(self, title: str, author: str, total_copies: int) -> int:
        if total_copies <= 0:
            raise InvalidOperationError("Total copies must be positive")
        book_id = self.next_book_id
        self.next_book_id += 1
        self.books[book_id] = Book(book_id, title, author, total_copies)
        return book_id

    def remove_book(self, book_id: int) -> None:
        book = self.books.get(book_id)
        if not book:
            raise BookNotFoundError("Book not found")
        if book.available_copies != book.total_copies:
            raise InvalidOperationError("Cannot remove: copies are currently borrowed")
        del self.books[book_id]

    def update_book(self, book_id: int, title: Optional[str] = None, author: Optional[str] = None, total_copies: Optional[int] = None) -> None:
        book = self.books.get(book_id)
        if not book:
            raise BookNotFoundError("Book not found")
        borrowed_count = book.total_copies - book.available_copies
        if total_copies is not None:
            if total_copies < borrowed_count:
                raise InvalidOperationError("Total copies cannot be less than the number of copies currently borrowed")
            delta = total_copies - book.total_copies
            book.total_copies = total_copies
            book.available_copies += delta
            if book.available_copies < 0:
                book.available_copies = 0
        if title is not None:
            book.title = title
        if author is not None:
            book.author = author

    def borrow_book(self, member_id: int, book_id: int, borrow_date: date, due_days: int = DEFAULT_DUE_DAYS) -> int:
        member = self.members.get(member_id)
        if not member:
            raise MemberNotFoundError("Member not found")
        book = self.books.get(book_id)
        if not book:
            raise BookNotFoundError("Book not found")
        if book.available_copies == 0:
            raise BookUnavailableError("No copies available for borrowing")
        for record in self.borrow_records:
            if record.member_id == member_id and record.book_id == book_id and record.return_date is None:
                raise BorrowLimitError("Member already has this book borrowed and not returned")
        due_date = borrow_date + timedelta(days=due_days)
        record_id = self.next_record_id
        self.next_record_id += 1
        record = BorrowRecord(record_id, member_id, book_id, borrow_date, due_date)
        self.borrow_records.append(record)
        book.available_copies -= 1
        return record_id

    def return_book(self, member_id: int, book_id: int, return_date: date) -> float:
        to_return = None
        for record in self.borrow_records:
            if record.member_id == member_id and record.book_id == book_id and record.return_date is None:
                to_return = record
                break
        if not to_return:
            raise BorrowRecordNotFoundError("No active borrow record found for member and book")
        if return_date < to_return.borrow_date:
            raise InvalidOperationError("Return date cannot be before borrow date")
        to_return.return_date = return_date
        fine = to_return.calculate_fine(return_date, FINE_PER_DAY)
        to_return.fine_paid = fine
        book = self.books.get(book_id)
        if book:
            book.available_copies += 1
        return fine

    def get_borrowed_books(self) -> List[Dict]:
        borrowed = []
        for record in self.borrow_records:
            if record.return_date is None:
                book = self.books.get(record.book_id)
                member = self.members.get(record.member_id)
                if book and member:
                    borrowed.append({
                        "record_id": record.record_id,
                        "member_id": record.member_id,
                        "member_name": member.name,
                        "book_id": record.book_id,
                        "book_title": book.title,
                        "borrow_date": record.borrow_date,
                        "due_date": record.due_date
                    })
        return borrowed

    def get_overdue_books(self, current_date: date) -> List[Dict]:
        overdue = []
        for record in self.borrow_records:
            if record.is_overdue(current_date):
                book = self.books.get(record.book_id)
                member = self.members.get(record.member_id)
                fine = record.calculate_fine(current_date, FINE_PER_DAY)
                if book and member:
                    overdue.append({
                        "record_id": record.record_id,
                        "member_id": record.member_id,
                        "member_name": member.name,
                        "book_id": record.book_id,
                        "book_title": book.title,
                        "borrow_date": record.borrow_date,
                        "due_date": record.due_date,
                        "fine_due": fine
                    })
        return overdue

    def get_member_info(self, member_id: int) -> Dict:
        member = self.members.get(member_id)
        if not member:
            raise MemberNotFoundError("Member not found")
        borrows = []
        total_fines = 0.0
        for record in self.borrow_records:
            if record.member_id == member_id and record.return_date is None:
                book = self.books.get(record.book_id)
                fine = record.calculate_fine(date.today(), FINE_PER_DAY)
                total_fines += fine
                if book:
                    borrows.append({
                        "book_id": record.book_id,
                        "book_title": book.title,
                        "borrow_date": record.borrow_date,
                        "due_date": record.due_date,
                        "fine_due": fine
                    })
        return {
            "member_id": member.member_id,
            "name": member.name,
            "contact": member.contact,
            "active_borrows": borrows,
            "total_fine_due": total_fines
        }

    def get_book_info(self, book_id: int) -> Dict:
        book = self.books.get(book_id)
        if not book:
            raise BookNotFoundError("Book not found")
        active_borrows = []
        for record in self.borrow_records:
            if record.book_id == book_id and record.return_date is None:
                member = self.members.get(record.member_id)
                if member:
                    active_borrows.append({
                        "member_id": record.member_id,
                        "member_name": member.name,
                        "borrow_date": record.borrow_date,
                        "due_date": record.due_date
                    })
        return {
            "book_id": book.book_id,
            "title": book.title,
            "author": book.author,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies,
            "active_borrows": active_borrows
        }