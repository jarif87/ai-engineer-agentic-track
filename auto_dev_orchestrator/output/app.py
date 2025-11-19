import gradio as gr
from datetime import date, timedelta
from library import Library, LibraryError, MemberNotFoundError, BookNotFoundError, BookUnavailableError, BorrowLimitError, BorrowRecordNotFoundError, InvalidOperationError

lib = Library()
current_member_id = None

def register_member(name, contact):
    global current_member_id
    try:
        member_id = lib.register_member(name, contact)
        current_member_id = member_id
        return f"Registered & logged in as: {name} (ID {member_id})", gr.update(visible=True), member_id
    except LibraryError as e:
        return f"Error: {str(e)}", gr.update(visible=False), None

def login_member(member_id):
    global current_member_id
    try:
        info = lib.get_member_info(int(member_id))
        current_member_id = int(member_id)
        return f"Logged in as: {info['name']} (ID {member_id})", gr.update(visible=True), int(member_id)
    except LibraryError as e:
        return f"Error: {str(e)}", gr.update(visible=False), None

def logout_member():
    global current_member_id
    current_member_id = None
    return "", gr.update(visible=False), None

def get_books():
    books = []
    for b in lib.books.values():
        books.append([b.book_id, b.title, b.author, b.total_copies, b.available_copies])
    return books

def add_book(title, author, total_copies):
    try:
        book_id = lib.add_book(title, author, int(total_copies))
        return f"Added book ID {book_id}: {title}", get_books()
    except LibraryError as e:
        return f"Error: {str(e)}", get_books()

def remove_book(book_id):
    try:
        lib.remove_book(int(book_id))
        return f"Book ID {book_id} removed.", get_books()
    except LibraryError as e:
        return f"Error: {str(e)}", get_books()

def borrow_book(book_id):
    global current_member_id
    if not current_member_id:
        return "Please login as a member first.", get_books()
    try:
        today = date.today()
        lib.borrow_book(current_member_id, int(book_id), today)
        return f"Borrowed book ID {book_id}!", get_books()
    except LibraryError as e:
        return f"Error: {str(e)}", get_books()

def return_book(book_id):
    global current_member_id
    if not current_member_id:
        return "Please login as a member first.", get_books()
    try:
        today = date.today()
        fine = lib.return_book(current_member_id, int(book_id), today)
        if fine:
            return f"Returned book ID {book_id}; Fine due: ${fine:.2f}", get_books()
        else:
            return f"Returned book ID {book_id}; No fine.", get_books()
    except LibraryError as e:
        return f"Error: {str(e)}", get_books()

def get_borrow_report():
    borrowed = lib.get_borrowed_books()
    rows = []
    for b in borrowed:
        rows.append([
            b["record_id"], b.get("member_name",""), b.get("book_title",""),
            b.get("borrow_date",""), b.get("due_date","")
        ])
    return rows

def get_overdue_report():
    overdue = lib.get_overdue_books(date.today())
    rows = []
    for r in overdue:
        rows.append([
            r["record_id"], r.get("member_name",""), r.get("book_title",""),
            r.get("borrow_date",""), r.get("due_date",""), f"${r.get('fine_due',0):.2f}"
        ])
    return rows

def get_my_info():
    global current_member_id
    if not current_member_id:
        return "Not logged in.", None, None
    try:
        info = lib.get_member_info(current_member_id)
        msg = f"ID: {info['member_id']}\nName: {info['name']}\nContact: {info['contact']}\nTotal Fine Due: ${info['total_fine_due']:.2f}"
        borrows = []
        for b in info["active_borrows"]:
            borrows.append([
                b["book_id"], b["book_title"], b["borrow_date"], b["due_date"], f"${b['fine_due']:.2f}"
            ])
        return msg, borrows, current_member_id
    except LibraryError as e:
        return f"Error: {str(e)}", None, None

def update_member(new_name, new_contact):
    global current_member_id
    if not current_member_id:
        return "Not logged in."
    try:
        lib.update_member(current_member_id, new_name if new_name else None, new_contact if new_contact else None)
        return "Update successful!"
    except LibraryError as e:
        return f"Error: {str(e)}"

def book_options():
    return [[b.book_id,f"{b.title} (ID {b.book_id})"] for b in lib.books.values()]

with gr.Blocks(title="Library Management Demo") as demo:
    gr.Markdown("# 📚 Simple Library Management System (Demo)")

    with gr.Tab("Member & Account"):
        member_status = gr.State(None)
        member_id_state = gr.State(None)
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Register new member")
                name = gr.Textbox(label="Name")
                contact = gr.Textbox(label="Contact")
                register_btn = gr.Button("Register & Login")
            with gr.Column():
                gr.Markdown("### Login as Member")
                member_id_login = gr.Number(label="Member ID", precision=0)
                login_btn = gr.Button("Login")

        msg_reg = gr.Textbox(label="", interactive=False)
        logout_btn = gr.Button("Logout")
        logout_btn.visible = False

        def on_register(name, contact):
            msg, vis, member_id = register_member(name, contact)
            logout_btn.visible = True if member_id else False
            return msg, gr.update(visible=True), member_id

        register_btn.click(fn=register_member, inputs=[name, contact], outputs=[msg_reg, logout_btn, member_id_state])
        login_btn.click(fn=login_member, inputs=member_id_login, outputs=[msg_reg, logout_btn, member_id_state])
        logout_btn.click(fn=logout_member, inputs=None, outputs=[msg_reg, logout_btn, member_id_state])

        gr.Markdown("#### Update account info (only while logged in)")
        new_name = gr.Textbox(label="New Name (opt.)")
        new_contact = gr.Textbox(label="New Contact (opt.)")
        update_btn = gr.Button("Update Info")
        update_msg = gr.Textbox(label="", interactive=False)
        update_btn.click(fn=update_member, inputs=[new_name, new_contact], outputs=update_msg)

        gr.Markdown("#### My Active Borrows")
        my_borrow_status = gr.Textbox(label="Account")
        my_borrow_table = gr.Dataframe(headers=["Book ID","Title","Borrowed","Due","Fine Due"], datatype=["number","str","str","str","str"])
        refresh_my_btn = gr.Button("Refresh")
        refresh_my_btn.click(fn=get_my_info, inputs=None, outputs=[my_borrow_status, my_borrow_table, member_id_state])

    with gr.Tab("Book Management"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Add Book")
                title = gr.Textbox(label="Title")
                author = gr.Textbox(label="Author")
                total_copies = gr.Number(label="Total Copies", precision=0)
                add_btn = gr.Button("Add Book")
            with gr.Column():
                gr.Markdown("### Remove Book")
                book_remove_id = gr.Number(label="Book ID to remove", precision=0)
                remove_btn = gr.Button("Remove Book")

        add_result = gr.Textbox(label="", interactive=False)
        books_table = gr.Dataframe(value=get_books, headers=["ID","Title","Author","Total","Available"], datatype=["number","str","str","number","number"])
        add_btn.click(fn=add_book, inputs=[title, author, total_copies], outputs=[add_result, books_table])
        remove_btn.click(fn=remove_book, inputs=book_remove_id, outputs=[add_result, books_table])

    with gr.Tab("Borrow/Return"):
        gr.Markdown("**Borrow and return require you to be logged in as a member.**")
        with gr.Row():
            with gr.Column():
                br_id = gr.Number(label="Book ID to borrow", precision=0)
                borrow_btn = gr.Button("Borrow Book")
            with gr.Column():
                ret_id = gr.Number(label="Book ID to return", precision=0)
                return_btn = gr.Button("Return Book")

        borrow_result = gr.Textbox(label="", interactive=False)

        borrow_btn.click(fn=borrow_book, inputs=br_id, outputs=[borrow_result, books_table])
        return_btn.click(fn=return_book, inputs=ret_id, outputs=[borrow_result, books_table])

        gr.Markdown("#### All books")
        books_table_overview = gr.Dataframe(value=get_books, headers=["ID","Title","Author","Total","Available"], datatype=["number","str","str","number","number"])

    with gr.Tab("Reports"):
        gr.Markdown("#### Currently Borrowed Books")
        borrowed_table = gr.Dataframe(value=get_borrow_report, headers=["Record ID","Member","Book","Borrow Date","Due Date"], datatype=["number","str","str","str","str"])
        refresh_borrowed_btn = gr.Button("Refresh Borrowed Books")
        refresh_borrowed_btn.click(fn=get_borrow_report, inputs=None, outputs=borrowed_table)

        gr.Markdown("#### Overdue Books")
        overdue_table = gr.Dataframe(value=get_overdue_report, headers=["Record ID","Member","Book","Borrow Date","Due Date","Fine Due"], datatype=["number","str","str","str","str","str"])
        refresh_overdue_btn = gr.Button("Refresh Overdue")
        refresh_overdue_btn.click(fn=get_overdue_report, inputs=None, outputs=overdue_table)

if __name__ == "__main__":
    demo.launch()