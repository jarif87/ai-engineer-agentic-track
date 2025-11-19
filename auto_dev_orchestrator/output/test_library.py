import unittest
from datetime import date, timedelta

import library

class TestLibrary(unittest.TestCase):

    def setUp(self):
        self.lib = library.Library()

    # --- Member related tests ---

    def test_register_member(self):
        mid = self.lib.register_member("Alice","12345")
        self.assertIsInstance(mid, int)
        info = self.lib.get_member_info(mid)
        self.assertEqual(info["name"], "Alice")
        self.assertEqual(info["contact"], "12345")

    def test_update_member(self):
        mid = self.lib.register_member("Bob","555")
        self.lib.update_member(mid, name="Bobby")
        info = self.lib.get_member_info(mid)
        self.assertEqual(info["name"], "Bobby")
        self.lib.update_member(mid, contact="999")
        info = self.lib.get_member_info(mid)
        self.assertEqual(info["contact"], "999")

    def test_update_nonexistent_member_raises(self):
        with self.assertRaises(library.MemberNotFoundError):
            self.lib.update_member(99, name="Ghost")
        with self.assertRaises(library.MemberNotFoundError):
            self.lib.get_member_info(777)

    def test_remove_member(self):
        mid = self.lib.register_member("Cathy", "phone")
        self.lib.remove_member(mid)
        with self.assertRaises(library.MemberNotFoundError):
            self.lib.get_member_info(mid)

    def test_remove_nonexistent_member_raises(self):
        with self.assertRaises(library.MemberNotFoundError):
            self.lib.remove_member(44)

    def test_remove_member_with_active_borrows_raises(self):
        mid = self.lib.register_member("Derek", "contact")
        bid = self.lib.add_book("B1", "A1", 2)
        today = date.today()
        self.lib.borrow_book(mid, bid, today)
        with self.assertRaises(library.InvalidOperationError):
            self.lib.remove_member(mid)

    # --- Book related tests ---

    def test_add_book(self):
        bid = self.lib.add_book("Dune", "Frank", 3)
        self.assertIsInstance(bid, int)
        info = self.lib.get_book_info(bid)
        self.assertEqual(info["title"], "Dune")
        self.assertEqual(info["author"], "Frank")
        self.assertEqual(info["total_copies"], 3)
        self.assertEqual(info["available_copies"], 3)

    def test_add_book_with_invalid_copies_raises(self):
        with self.assertRaises(library.InvalidOperationError):
            self.lib.add_book("foo", "aut", 0)
        with self.assertRaises(library.InvalidOperationError):
            self.lib.add_book("foo", "aut", -2)

    def test_update_book_title_author_and_total_copies(self):
        bid = self.lib.add_book("Old", "Unknown", 2)
        self.lib.update_book(bid, title="NewTitle", author="Known", total_copies=4)
        info = self.lib.get_book_info(bid)
        self.assertEqual(info["title"], "NewTitle")
        self.assertEqual(info["author"], "Known")
        self.assertEqual(info["total_copies"], 4)
        self.assertEqual(info["available_copies"], 4)

    def test_update_book_decrease_total_copies_not_below_borrowed(self):
        bid = self.lib.add_book("book", "author", 2)
        mid = self.lib.register_member("User","c")
        today = date.today()
        self.lib.borrow_book(mid, bid, today)
        # Should allow setting total_copies=2 or more, not 0
        with self.assertRaises(library.InvalidOperationError):
            self.lib.update_book(bid, total_copies=0)
        self.lib.update_book(bid, total_copies=2)  # ok

    def test_update_nonexistent_book_raises(self):
        with self.assertRaises(library.BookNotFoundError):
            self.lib.update_book(999, title="Nope")
        with self.assertRaises(library.BookNotFoundError):
            self.lib.get_book_info(321)

    def test_remove_book(self):
        bid = self.lib.add_book("Eragon", "Paolini", 1)
        self.lib.remove_book(bid)
        with self.assertRaises(library.BookNotFoundError):
            self.lib.get_book_info(bid)

    def test_remove_nonexistent_book_raises(self):
        with self.assertRaises(library.BookNotFoundError):
            self.lib.remove_book(31415)

    def test_remove_book_with_borrowed_copies_raises(self):
        bid = self.lib.add_book("HP", "Rowling", 2)
        mid = self.lib.register_member("Harry", "hogwarts")
        today = date.today()
        self.lib.borrow_book(mid, bid, today)
        with self.assertRaises(library.InvalidOperationError):
            self.lib.remove_book(bid)

    # --- Borrow/return/limit/availability tests ---

    def test_borrow_and_return_book_no_fine(self):
        mid = self.lib.register_member("Ian","777")
        bid = self.lib.add_book("Sapiens", "Yuval", 1)
        today = date.today()
        recid = self.lib.borrow_book(mid, bid, today)
        info = self.lib.get_book_info(bid)
        self.assertEqual(info["available_copies"], 0)
        fine = self.lib.return_book(mid, bid, today+timedelta(days=14))
        self.assertEqual(fine, 0.0)
        info2 = self.lib.get_book_info(bid)
        self.assertEqual(info2["available_copies"], 1)

    def test_borrow_returns_overdue_fine(self):
        mid = self.lib.register_member("Jim","333")
        bid = self.lib.add_book("Title", "A", 1)
        bday = date(2023,1,1)
        recid = self.lib.borrow_book(mid, bid, bday)
        return_date = bday + timedelta(days=18)  # 4 days late
        fine = self.lib.return_book(mid, bid, return_date)
        self.assertEqual(fine, 4*library.FINE_PER_DAY)
        rec = [r for r in self.lib.borrow_records if r.record_id==recid][0]
        self.assertEqual(rec.fine_paid, 4*library.FINE_PER_DAY)

    def test_borrow_book_no_copies_raises(self):
        bid = self.lib.add_book("Solo", "Uniq", 1)
        m1 = self.lib.register_member("One", "A")
        m2 = self.lib.register_member("Two", "B")
        today = date.today()
        self.lib.borrow_book(m1, bid, today)
        with self.assertRaises(library.BookUnavailableError):
            self.lib.borrow_book(m2, bid, today)

    def test_member_borrows_same_book_twice_without_return_raises(self):
        bid = self.lib.add_book("BK", "RT", 2)
        mid = self.lib.register_member("Pep", "Emil")
        today = date.today()
        self.lib.borrow_book(mid, bid, today)
        with self.assertRaises(library.BorrowLimitError):
            self.lib.borrow_book(mid, bid, today+timedelta(days=1))

    def test_borrow_book_invalid_member_or_book_raises(self):
        with self.assertRaises(library.MemberNotFoundError):
            self.lib.borrow_book(42, 1, date.today())
        bid = self.lib.add_book("x", "y", 2)
        with self.assertRaises(library.BookNotFoundError):
            self.lib.borrow_book(self.lib.register_member("A","B"), 999, date.today())

    def test_return_book_invalid_member_or_book_raises(self):
        # no records exist
        with self.assertRaises(library.BorrowRecordNotFoundError):
            self.lib.return_book(5,10,date.today())

    def test_return_book_before_borrow_date_raises(self):
        mid = self.lib.register_member("Kal", "omen")
        bid = self.lib.add_book("Omer", "Author", 1)
        today = date.today()
        self.lib.borrow_book(mid, bid, today)
        with self.assertRaises(library.InvalidOperationError):
            self.lib.return_book(mid, bid, today - timedelta(days=1))

    # --- Active borrowing/overdue queries ---

    def test_get_borrowed_books_and_overdue_books(self):
        m1 = self.lib.register_member("Anna","1")
        m2 = self.lib.register_member("Ben","2")
        b1 = self.lib.add_book("B1", "AA", 2)
        b2 = self.lib.add_book("B2", "BB", 1)
        d1 = date(2022, 5, 1)
        r1 = self.lib.borrow_book(m1, b1, d1)
        r2 = self.lib.borrow_book(m2, b2, d1)
        # Anna returns on time, Ben doesn't
        self.lib.return_book(m1, b1, d1+timedelta(days=14))
        now = d1 + timedelta(days=20)
        overdue = self.lib.get_overdue_books(now)
        self.assertTrue(any(rec["member_id"]==m2 and rec["book_id"]==b2 for rec in overdue))
        borrowed = self.lib.get_borrowed_books()
        # Only Ben should be left borrowing
        self.assertTrue(all(x["member_id"]==m2 for x in borrowed))
        self.assertTrue(all(x["book_id"]==b2 for x in borrowed))

    def test_get_member_info_fines(self):
        mid = self.lib.register_member("Lu", "C")
        bid = self.lib.add_book("B", "A", 1)
        bday = date.today() - timedelta(days=16)
        self.lib.borrow_book(mid, bid, bday)
        info = self.lib.get_member_info(mid)
        self.assertEqual(len(info["active_borrows"]), 1)
        # Should be overdue by 2 days
        self.assertEqual(info["active_borrows"][0]["fine_due"], 2.0)
        self.assertEqual(info["total_fine_due"], 2.0)

    def test_get_book_info_active_borrows(self):
        mid = self.lib.register_member("Joy","phone")
        bid = self.lib.add_book("JBook","Joyee",4)
        today = date.today()
        self.lib.borrow_book(mid, bid, today)
        info = self.lib.get_book_info(bid)
        self.assertEqual(info["available_copies"], 3)
        self.assertEqual(len(info["active_borrows"]), 1)
        self.assertEqual(info["active_borrows"][0]["member_id"], mid)

    # --- BorrowRecord object methods ---

    def test_borrow_record_is_overdue_and_fine(self):
        rec = library.BorrowRecord(1, 77, 88, date(2020,1,1), date(2020,1,14))
        self.assertFalse(rec.is_overdue(date(2020,1,14)))
        self.assertFalse(rec.is_overdue(date(2020,1,10)))
        self.assertTrue(rec.is_overdue(date(2020,2,1)))

        # Not returned
        self.assertEqual(rec.calculate_fine(date(2020,2,1)), 18)
        rec.return_date = date(2020,1,18)
        self.assertFalse(rec.is_overdue(date(2020,2,1)))
        self.assertEqual(rec.calculate_fine(date(2020,2,1)), 4)

    # --- Edge cases ---

    def test_multiple_members_books_records(self):
        # Borrow/return with multiple members/books, unique records
        mid = []
        bid = []
        for i in range(3):
            mid.append(self.lib.register_member(f"name{i}", f"c{i}"))
            bid.append(self.lib.add_book(f"title{i}",f"a{i}",2))
        dates = [date.today()-timedelta(days=2*i) for i in range(3)]
        rids = []
        for i in range(3):
            rids.append(self.lib.borrow_book(mid[i], bid[i], dates[i]))
        # All borrowed, now return all
        for i in range(3):
            self.lib.return_book(mid[i], bid[i], dates[i]+timedelta(days=5))
        # All books become available
        for i in range(3):
            info = self.lib.get_book_info(bid[i])
            self.assertEqual(info["available_copies"], 2)
            self.assertEqual(len(info["active_borrows"]), 0)

    def test_borrow_record_not_found_return(self):
        # borrow, return, then try to return again (should not find record)
        mid = self.lib.register_member("Extra","c")
        bid = self.lib.add_book("Once","Rem",1)
        today = date.today()
        self.lib.borrow_book(mid, bid, today)
        self.lib.return_book(mid, bid, today+timedelta(days=2))
        with self.assertRaises(library.BorrowRecordNotFoundError):
            self.lib.return_book(mid, bid, today+timedelta(days=3))

if __name__ == '__main__':
    unittest.main()