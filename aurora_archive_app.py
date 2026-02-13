# BIT502 Assessment 3
# Name: [Your name]
# Student number: [Your student number]
# Assessment number: 3
# The Aurora Archive – Bookstore membership application (database + GUI)

import tkinter as tk
from tkinter import messagebox as msgbox
from tkinter import ttk
import sqlite3
import os
import time

# ---------------------------------------------------------------------------
# Database and path setup (relative path as per assessment)
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Use the provided database; rename to your project name for submission if required
DB_FILENAME = "BIT502_Assessment_3_Appendix_D_Database_Data__New_.db"
DB_PATH = os.path.join(SCRIPT_DIR, DB_FILENAME)

# Single shared connection for the whole app (avoids "database is locked" with OneDrive/sync folders)
_app_conn = None

def ensure_database_exists():
    """If the database file or Memberships table is missing, create it (same structure as Appendix C)."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Memberships'")
        if cur.fetchone() is None:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Memberships (
                    MemberID INTEGER PRIMARY KEY NOT NULL,
                    First_Name TEXT NOT NULL,
                    Last_Name TEXT NOT NULL,
                    Address TEXT NOT NULL,
                    Mobile TEXT NOT NULL,
                    Membership_Plan TEXT NOT NULL,
                    Payment_Plan TEXT NOT NULL,
                    Extra_Book_Rental BOOLEAN NOT NULL,
                    Extra_Private_Area BOOLEAN NOT NULL,
                    Extra_Booklet BOOLEAN NOT NULL,
                    Extra_Ebook_Rental BOOLEAN NOT NULL,
                    Has_Library_Card BOOLEAN NOT NULL,
                    Library_Card_Number TEXT
                )
            """)
            conn.commit()
    finally:
        if conn is not None:
            conn.close()

def get_db_connection():
    """Return the single app-wide database connection. Do not close it."""
    return _app_conn

# ---------------------------------------------------------------------------
# Constants: membership plans and pricing (from Appendix A)
# ---------------------------------------------------------------------------

PLAN_STANDARD = "Standard"
PLAN_PREMIUM = "Premium"
PLAN_KIDS = "Kids"
PLAN_MONTHLY = "Monthly"
PLAN_ANNUAL = "Annual"

# DB may contain "Regular" from sample data; assessment uses "Standard"
MEMBERSHIP_PLANS = (PLAN_STANDARD, "Regular", PLAN_PREMIUM, PLAN_KIDS)
PAYMENT_PLANS = (PLAN_MONTHLY, PLAN_ANNUAL)

OPTIONAL_1 = "Book Rental"
OPTIONAL_2 = "Private Area Access"
OPTIONAL_3 = "Monthly Booklet"
OPTIONAL_4 = "Online ebook Rental"

# Prices: membership per month, extras per week (Appendix A)
MEMBERSHIP_PRICES = {PLAN_STANDARD: 10.0, "Regular": 10.0, PLAN_PREMIUM: 15.0, PLAN_KIDS: 5.0}
EXTRA_PRICES = {OPTIONAL_1: 5.0, OPTIONAL_2: 15.0, OPTIONAL_3: 2.0, OPTIONAL_4: 5.0}

# For statistics income table (Cost Per Unit – no discounts applied)
INCOME_TABLE_OPTIONS = [
    ("Regular Plan", 10.0, "per month"),
    ("Premium Plan", 15.0, "per month"),
    ("Kids Plan", 5.0, "per month"),
    ("Book Rental", 5.0, "per week"),
    ("Private Area Access", 15.0, "per week"),
    ("Monthly Booklet", 2.0, "per week"),
    ("Online eBook Rental", 5.0, "per week"),
]

# ---------------------------------------------------------------------------
# Scrollable frame helper (Canvas + Scrollbar + inner Frame)
# ---------------------------------------------------------------------------

def _make_scrollable_frame(parent):
    """Returns (canvas, scrollbar, inner_frame). Pack canvas and scrollbar; put content in inner_frame."""
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas)

    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_canvas_configure(event):
        canvas.itemconfig(win_id, width=event.width)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind("<Configure>", _on_canvas_configure)
    canvas.bind("<MouseWheel>", _on_mousewheel)
    return canvas, scrollbar, inner


# ---------------------------------------------------------------------------
# Main application window (menu screen)
# ---------------------------------------------------------------------------

def main():
    global _app_conn
    # Ensure database file and Memberships table exist (creates if missing)
    try:
        ensure_database_exists()
    except Exception as e:
        msgbox.showerror(
            "Database error",
            f"Cannot create or open the database.\n\n"
            f"Expected location:\n{DB_PATH}\n\n"
            f"Error: {str(e)}\n\n"
            "Make sure this script is in the same folder as the .db file (or run from that folder)."
        )
        return

    # One connection for the whole app – avoids "database is locked" (e.g. with OneDrive)
    # Retry a few times in case the file is briefly locked by sync/antivirus
    _app_conn = None
    last_error = None
    for attempt in range(3):
        try:
            _app_conn = sqlite3.connect(DB_PATH, timeout=15.0)
            _app_conn.execute("PRAGMA journal_mode=WAL")
            break
        except sqlite3.OperationalError as e:
            last_error = e
            if attempt < 2:
                time.sleep(2)
            else:
                msgbox.showerror(
                    "Database error",
                    f"Cannot open database.\n\n{DB_PATH}\n\nError: {str(e)}\n\n"
                    "Try: (1) Close any other copy of this app. (2) Pause OneDrive sync for this folder. "
                    "(3) Copy the whole project folder to C:\\Temp and run from there."
                )
                return
    if _app_conn is None:
        msgbox.showerror("Database error", f"Could not open database.\n\n{last_error}")
        return

    root = tk.Tk()

    def on_closing():
        global _app_conn
        if _app_conn is not None:
            try:
                _app_conn.close()
            except Exception:
                pass
            _app_conn = None
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.title("The Aurora Archive – Membership")
    root.geometry("380x280")
    root.resizable(True, True)
    root.configure(padx=20, pady=20)

    canvas, scrollbar, inner = _make_scrollable_frame(root)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    lbl_title = tk.Label(inner, text="The Aurora Archive", font=("", 16, "bold"))
    lbl_subtitle = tk.Label(inner, text="Bookstore membership administration")
    lbl_title.pack(pady=(0, 5))
    lbl_subtitle.pack(pady=(0, 25))

    frame_buttons = tk.Frame(inner)
    frame_buttons.pack(pady=10)

    def open_membership():
        _open_membership_form(root)

    def open_search():
        _open_search_form(root)

    def open_statistics():
        _open_statistics_form(root)

    def open_help():
        _open_help_window(root)

    btn_membership = tk.Button(frame_buttons, text="Membership form", width=22, command=open_membership)
    btn_search = tk.Button(frame_buttons, text="Search members", width=22, command=open_search)
    btn_stats = tk.Button(frame_buttons, text="Statistics", width=22, command=open_statistics)
    btn_help = tk.Button(frame_buttons, text="Help", width=22, command=open_help)

    btn_membership.pack(pady=5)
    btn_search.pack(pady=5)
    btn_stats.pack(pady=5)
    btn_help.pack(pady=5)

    lbl_footer = tk.Label(inner, text="Close this window to exit the application.", fg="gray")
    lbl_footer.pack(side="bottom", pady=15)

    root.mainloop()


# ---------------------------------------------------------------------------
# Membership form (based on Assessment 2; saves to database)
# Appendix A: library discount on membership plan only; annual = 11 months paid
# ---------------------------------------------------------------------------

def _open_membership_form(parent):
    win = tk.Toplevel(parent)
    win.title("The Aurora Archive – New membership")
    win.geometry("480x520")
    win.resizable(True, True)
    win.configure(padx=10, pady=10)

    canvas, scrollbar, inner = _make_scrollable_frame(win)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Variables
    membership_plan = tk.StringVar(win, PLAN_STANDARD)
    payment_plan = tk.StringVar(win, PLAN_MONTHLY)
    extra1 = tk.BooleanVar(win, False)
    extra2 = tk.BooleanVar(win, False)
    extra3 = tk.BooleanVar(win, False)
    extra4 = tk.BooleanVar(win, False)
    has_library_card = tk.BooleanVar(win, False)

    # Widgets
    f = tk.Frame(inner)
    f.pack(fill="both", expand=True)

    row = 0
    tk.Label(f, text="First name:").grid(row=row, column=0, sticky="w", pady=2)
    entry_first = tk.Entry(f, width=35)
    entry_first.grid(row=row, column=1, sticky="w", pady=2)
    lbl_req_first = tk.Label(f, text="*", fg="red")
    lbl_req_first.grid(row=row, column=2, sticky="w")
    row += 1

    tk.Label(f, text="Last name:").grid(row=row, column=0, sticky="w", pady=2)
    entry_last = tk.Entry(f, width=35)
    entry_last.grid(row=row, column=1, sticky="w", pady=2)
    lbl_req_last = tk.Label(f, text="*", fg="red")
    lbl_req_last.grid(row=row, column=2, sticky="w")
    row += 1

    tk.Label(f, text="Address:").grid(row=row, column=0, sticky="w", pady=2)
    entry_address = tk.Entry(f, width=35)
    entry_address.grid(row=row, column=1, sticky="w", pady=2)
    lbl_req_addr = tk.Label(f, text="*", fg="red")
    lbl_req_addr.grid(row=row, column=2, sticky="w")
    row += 1

    tk.Label(f, text="Mobile:").grid(row=row, column=0, sticky="w", pady=2)
    entry_mobile = tk.Entry(f, width=35)
    entry_mobile.grid(row=row, column=1, sticky="w", pady=2)
    lbl_req_mobile = tk.Label(f, text="*", fg="red")
    lbl_req_mobile.grid(row=row, column=2, sticky="w")
    row += 1

    tk.Label(f, text="Membership plan:").grid(row=row, column=0, sticky="w", pady=2)
    f_plan = tk.Frame(f)
    f_plan.grid(row=row, column=1, sticky="w", pady=2)
    tk.Radiobutton(f_plan, text=PLAN_STANDARD, variable=membership_plan, value=PLAN_STANDARD).pack(side="left")
    tk.Radiobutton(f_plan, text=PLAN_PREMIUM, variable=membership_plan, value=PLAN_PREMIUM).pack(side="left")
    tk.Radiobutton(f_plan, text=PLAN_KIDS, variable=membership_plan, value=PLAN_KIDS).pack(side="left")
    lbl_req_plan = tk.Label(f, text="*", fg="red")
    lbl_req_plan.grid(row=row, column=2, sticky="w")
    row += 1

    tk.Label(f, text="Payment plan:").grid(row=row, column=0, sticky="w", pady=2)
    f_pay = tk.Frame(f)
    f_pay.grid(row=row, column=1, sticky="w", pady=2)
    tk.Radiobutton(f_pay, text=PLAN_MONTHLY, variable=payment_plan, value=PLAN_MONTHLY).pack(side="left")
    tk.Radiobutton(f_pay, text=PLAN_ANNUAL, variable=payment_plan, value=PLAN_ANNUAL).pack(side="left")
    lbl_req_pay = tk.Label(f, text="*", fg="red")
    lbl_req_pay.grid(row=row, column=2, sticky="w")
    row += 1

    tk.Label(f, text="Optional extras:").grid(row=row, column=0, sticky="w", pady=2)
    f_extras = tk.Frame(f)
    f_extras.grid(row=row, column=1, sticky="w", pady=2)
    tk.Checkbutton(f_extras, text=OPTIONAL_1, variable=extra1).pack(anchor="w")
    tk.Checkbutton(f_extras, text=OPTIONAL_2, variable=extra2).pack(anchor="w")
    tk.Checkbutton(f_extras, text=OPTIONAL_3, variable=extra3).pack(anchor="w")
    tk.Checkbutton(f_extras, text=OPTIONAL_4, variable=extra4).pack(anchor="w")
    row += 1

    tk.Label(f, text="Library card:").grid(row=row, column=0, sticky="w", pady=2)
    tk.Checkbutton(f, text="Has library card", variable=has_library_card).grid(row=row, column=1, sticky="w", pady=2)
    row += 1
    tk.Label(f, text="Card number:").grid(row=row, column=0, sticky="w", pady=2)
    entry_library_id = tk.Entry(f, width=35)
    entry_library_id.grid(row=row, column=1, sticky="w", pady=2)
    lbl_req_lib = tk.Label(f, text="*", fg="red")
    lbl_req_lib.grid(row=row, column=2, sticky="w")
    row += 1

    # Totals (Staff only)
    tk.Label(f, text="Totals", font=("", 10, "bold")).grid(row=row, column=0, sticky="w", pady=(10, 2))
    row += 1
    lbl_base = tk.Label(f, text="Membership cost: --")
    lbl_base.grid(row=row, column=0, columnspan=2, sticky="w", pady=1)
    row += 1
    lbl_extras = tk.Label(f, text="Extra charges: --")
    lbl_extras.grid(row=row, column=0, columnspan=2, sticky="w", pady=1)
    row += 1
    lbl_discount = tk.Label(f, text="Total discount: --")
    lbl_discount.grid(row=row, column=0, columnspan=2, sticky="w", pady=1)
    row += 1
    lbl_total = tk.Label(f, text="Total cost: --")
    lbl_total.grid(row=row, column=0, columnspan=2, sticky="w", pady=1)
    row += 1
    lbl_payment = tk.Label(f, text="Payment due: --")
    lbl_payment.grid(row=row, column=0, columnspan=2, sticky="w", pady=1)
    row += 1

    def format_money(value):
        return f"${value:.2f}"

    def compute_totals():
        plan = membership_plan.get()
        pay = payment_plan.get()
        if plan not in MEMBERSHIP_PRICES or pay not in (PLAN_MONTHLY, PLAN_ANNUAL):
            return None
        base = MEMBERSHIP_PRICES[plan]
        ex = 0.0
        if extra1.get(): ex += EXTRA_PRICES[OPTIONAL_1]
        if extra2.get(): ex += EXTRA_PRICES[OPTIONAL_2]
        if extra3.get(): ex += EXTRA_PRICES[OPTIONAL_3]
        if extra4.get(): ex += EXTRA_PRICES[OPTIONAL_4]
        # Appendix A: 10% discount on membership plan cost only (not extras)
        lib_discount = 0.10 * base if has_library_card.get() else 0.0
        total_monthly = base + ex - lib_discount
        # Annual: one month free → pay for 11 months
        payment_due = total_monthly if pay == PLAN_MONTHLY else total_monthly * 11
        payment_label = "per month" if pay == PLAN_MONTHLY else "per year (11 months)"
        return {
            "base_cost": base, "extras_cost": ex, "total_discount": lib_discount,
            "total_cost_monthly": total_monthly, "payment_due": payment_due, "payment_label": payment_label,
        }

    def refresh_totals(*_):
        t = compute_totals()
        if t is None:
            return
        lbl_base.config(text=f"Membership cost: {format_money(t['base_cost'])}")
        lbl_extras.config(text=f"Extra charges: {format_money(t['extras_cost'])}")
        lbl_discount.config(text=f"Total discount: {format_money(t['total_discount'])}")
        lbl_total.config(text=f"Total cost: {format_money(t['total_cost_monthly'])}")
        lbl_payment.config(text=f"Payment due: {format_money(t['payment_due'])} {t['payment_label']}")

    for var in (membership_plan, payment_plan, extra1, extra2, extra3, extra4, has_library_card):
        var.trace_add("write", refresh_totals)

    req_rows = [0, 1, 2, 3, 4, 5, 8]
    req_labels = [lbl_req_first, lbl_req_last, lbl_req_addr, lbl_req_mobile, lbl_req_plan, lbl_req_pay, lbl_req_lib]

    def set_required(show_list):
        for i, lbl in enumerate(req_labels):
            if i < len(show_list) and show_list[i]:
                lbl.grid(row=req_rows[i], column=2, sticky="w")
            else:
                lbl.grid_remove()

    def validate():
        err = []
        first = entry_first.get().strip()
        last = entry_last.get().strip()
        addr = entry_address.get().strip()
        mobile = entry_mobile.get().strip()
        lib_id = entry_library_id.get().strip()
        show = [not first, not last, not addr, not mobile,
                membership_plan.get() not in MEMBERSHIP_PRICES,
                payment_plan.get() not in (PLAN_MONTHLY, PLAN_ANNUAL),
                has_library_card.get() and (not lib_id or not lib_id.isdigit() or len(lib_id) != 5)]
        set_required(show)
        if not first: err.append("First name is required.")
        if not last: err.append("Last name is required.")
        if not addr: err.append("Address is required.")
        if not mobile: err.append("Mobile is required.")
        if membership_plan.get() not in MEMBERSHIP_PRICES: err.append("Please select a membership plan.")
        if payment_plan.get() not in (PLAN_MONTHLY, PLAN_ANNUAL): err.append("Please select a payment plan.")
        if has_library_card.get():
            if not lib_id: err.append("Library card number is required when library card is selected.")
            elif not lib_id.isdigit() or len(lib_id) != 5: err.append("Library card ID must be a 5-digit number.")
        if any(c.isdigit() for c in first): err.append("First name must not contain numbers.")
        if any(c.isdigit() for c in last): err.append("Last name must not contain numbers.")
        return err

    def clear_form():
        entry_first.delete(0, tk.END)
        entry_last.delete(0, tk.END)
        entry_address.delete(0, tk.END)
        entry_mobile.delete(0, tk.END)
        entry_library_id.delete(0, tk.END)
        membership_plan.set(PLAN_STANDARD)
        payment_plan.set(PLAN_MONTHLY)
        extra1.set(False)
        extra2.set(False)
        extra3.set(False)
        extra4.set(False)
        has_library_card.set(False)
        lbl_base.config(text="Membership cost: --")
        lbl_extras.config(text="Extra charges: --")
        lbl_discount.config(text="Total discount: --")
        lbl_total.config(text="Total cost: --")
        lbl_payment.config(text="Payment due: --")
        set_required([False] * 7)

    def submit():
        err = validate()
        if err:
            msgbox.showwarning("Form errors", "\n".join(err))
            return
        plan = membership_plan.get()
        # Store as Standard (assessment); DB may also have "Regular" from sample data
        plan_db = PLAN_STANDARD if plan == "Regular" else plan
        pay = payment_plan.get()
        lib_id = entry_library_id.get().strip() if has_library_card.get() else ""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Memberships (First_Name, Last_Name, Address, Mobile, Membership_Plan, Payment_Plan,
                Extra_Book_Rental, Extra_Private_Area, Extra_Booklet, Extra_Ebook_Rental, Has_Library_Card, Library_Card_Number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_first.get().strip(),
                entry_last.get().strip(),
                entry_address.get().strip(),
                entry_mobile.get().strip(),
                plan_db,
                pay,
                1 if extra1.get() else 0,
                1 if extra2.get() else 0,
                1 if extra3.get() else 0,
                1 if extra4.get() else 0,
                1 if has_library_card.get() else 0,
                lib_id,
            ))
            conn.commit()
        except Exception as e:
            msgbox.showerror(
                "Error",
                f"Could not save to database.\n\n"
                f"Database location: {DB_PATH}\n\n"
                f"Error: {str(e)}"
            )
            return
        msgbox.showinfo("Saved", "Member added successfully.")
        clear_form()

    # Buttons
    btn_frame = tk.Frame(inner)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Calculate totals", command=lambda: refresh_totals()).pack(side="left", padx=2)
    tk.Button(btn_frame, text="Submit", command=submit).pack(side="left", padx=2)
    tk.Button(btn_frame, text="Back to menu", command=win.destroy).pack(side="left", padx=2)

    refresh_totals()


# ---------------------------------------------------------------------------
# Search form: ID, name, membership plan, payment plan; combinable; table
# ---------------------------------------------------------------------------

def _open_search_form(parent):
    win = tk.Toplevel(parent)
    win.title("The Aurora Archive – Search members")
    win.geometry("720x400")
    win.resizable(True, True)
    win.configure(padx=10, pady=10)

    canvas, scrollbar, inner = _make_scrollable_frame(win)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Search criteria
    f_criteria = tk.Frame(inner)
    f_criteria.pack(fill="x", pady=(0, 5))
    tk.Label(f_criteria, text="Member ID:").grid(row=0, column=0, sticky="w", padx=(0, 5))
    entry_id = tk.Entry(f_criteria, width=10)
    entry_id.grid(row=0, column=1, sticky="w", padx=(0, 15))
    tk.Label(f_criteria, text="Last name:").grid(row=0, column=2, sticky="w", padx=(0, 5))
    entry_name = tk.Entry(f_criteria, width=18)
    entry_name.grid(row=0, column=3, sticky="w", padx=(0, 15))
    tk.Label(f_criteria, text="Membership plan:").grid(row=0, column=4, sticky="w", padx=(0, 5))
    var_plan = tk.StringVar(win, value="")
    combo_plan = ttk.Combobox(f_criteria, textvariable=var_plan, width=12, values=["", "Standard", "Regular", "Premium", "Kids"])
    combo_plan.grid(row=0, column=5, sticky="w", padx=(0, 15))
    tk.Label(f_criteria, text="Payment plan:").grid(row=0, column=6, sticky="w", padx=(0, 5))
    var_pay = tk.StringVar(win, value="")
    combo_pay = ttk.Combobox(f_criteria, textvariable=var_pay, width=10, values=["", "Monthly", "Annual"])
    combo_pay.grid(row=0, column=7, sticky="w", padx=(0, 10))
    tk.Button(f_criteria, text="Search", command=lambda: do_search()).grid(row=0, column=8, padx=5)

    # Results table
    f_tree = tk.Frame(inner)
    f_tree.pack(fill="both", expand=True, pady=5)
    columns = ("id", "first", "last", "address", "mobile", "plan", "payment", "extras", "card")
    tree = ttk.Treeview(f_tree, columns=columns, show="headings", height=12)
    for c in columns:
        tree.heading(c, text=c.replace("_", " ").title())
        tree.column(c, width=70)
    tree.column("address", width=120)
    tree.column("extras", width=80)
    scroll = ttk.Scrollbar(f_tree, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    lbl_status = tk.Label(inner, text="Enter criteria and click Search.")
    lbl_status.pack(anchor="w", pady=2)
    tk.Button(inner, text="Back to menu", command=win.destroy).pack(anchor="w", pady=5)

    def do_search():
        for i in tree.get_children():
            tree.delete(i)
        id_val = entry_id.get().strip()
        name_val = entry_name.get().strip().lower()
        plan_val = var_plan.get().strip()
        pay_val = var_pay.get().strip()
        if not any([id_val, name_val, plan_val, pay_val]):
            lbl_status.config(text="Please enter at least one search criterion.")
            return
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM Memberships")
            rows = cur.fetchall()
        except Exception as e:
            lbl_status.config(text=f"Error: {str(e)}")
            return
        # Filter: case-insensitive, partial match
        result = []
        for r in rows:
            mid, first, last, addr, mobile, plan, pay, e1, e2, e3, e4, has_card, card_no = r
            if id_val and (id_val not in str(mid)):
                continue
            if name_val and name_val not in last.lower():
                continue
            if plan_val and plan_val.lower() not in (plan or "").lower():
                continue
            if pay_val and pay_val.lower() not in (pay or "").lower():
                continue
            extras = []
            if e1: extras.append("Book")
            if e2: extras.append("Private")
            if e3: extras.append("Booklet")
            if e4: extras.append("Ebook")
            result.append((mid, first, last, addr, mobile, plan or "", pay or "", ", ".join(extras) or "-", "Yes" if has_card else "No"))
        for r in result:
            tree.insert("", "end", values=r)
        if not result:
            lbl_status.config(text="No members found matching your criteria.")
        else:
            lbl_status.config(text=f"Found {len(result)} member(s).")



# ---------------------------------------------------------------------------
# Statistics form: counts + income table
# ---------------------------------------------------------------------------

def _open_statistics_form(parent):
    win = tk.Toplevel(parent)
    win.title("The Aurora Archive – Statistics")
    win.geometry("560x520")
    win.resizable(True, True)
    win.configure(padx=10, pady=10)

    canvas, scrollbar, inner = _make_scrollable_frame(win)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Memberships")
        rows = cur.fetchall()
    except Exception as e:
        msgbox.showerror("Error", f"Could not load database.\n{str(e)}")
        win.destroy()
        return

    # Counts
    total = len(rows)
    by_plan = {}
    by_pay = {}
    extra_book = extra_private = extra_booklet = extra_ebook = 0
    no_extras = 0
    has_card = 0
    for r in rows:
        mid, first, last, addr, mobile, plan, pay, e1, e2, e3, e4, hc, card_no = r
        by_plan[plan or ""] = by_plan.get(plan or "", 0) + 1
        by_pay[pay or ""] = by_pay.get(pay or "", 0) + 1
        if e1: extra_book += 1
        if e2: extra_private += 1
        if e3: extra_booklet += 1
        if e4: extra_ebook += 1
        if not (e1 or e2 or e3 or e4): no_extras += 1
        if hc: has_card += 1

    f_top = tk.Frame(inner)
    f_top.pack(fill="x", pady=(0, 10))
    tk.Label(f_top, text="Member statistics", font=("", 12, "bold")).pack(anchor="w")
    text_stats = (
        f"Total members: {total}\n"
        f"By membership plan: {dict(by_plan)}\n"
        f"By payment: Monthly {by_pay.get('Monthly', 0)}, Annual {by_pay.get('Annual', 0)}\n"
        f"Optional extras – Book rental: {extra_book}, Private area: {extra_private}, Booklet: {extra_booklet}, Ebook: {extra_ebook}\n"
        f"Members with no optional extras: {no_extras}\n"
        f"Members with library card: {has_card}"
    )
    tk.Label(f_top, text=text_stats, justify="left").pack(anchor="w")

    # Income table (Cost Per Unit from appendix; no discounts)
    tk.Label(inner, text="Expected income (approximation; no discounts)", font=("", 10, "bold")).pack(anchor="w", pady=(10, 5))
    plan_counts = {PLAN_STANDARD: by_plan.get(PLAN_STANDARD, 0) + by_plan.get("Regular", 0), PLAN_PREMIUM: by_plan.get(PLAN_PREMIUM, 0), PLAN_KIDS: by_plan.get(PLAN_KIDS, 0)}
    extra_counts = [extra_book, extra_private, extra_booklet, extra_ebook]
    cols = ("Option", "Cost per unit", "Member amount", "Total income")
    tree = ttk.Treeview(inner, columns=cols, show="headings", height=12)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=120)
    tree.pack(fill="both", expand=True, pady=5)
    # Rows: Regular, Premium, Kids, Book Rental, Private Area, Booklet, eBook
    plan_keys = (PLAN_STANDARD, PLAN_PREMIUM, PLAN_KIDS)  # Regular Plan row uses Standard (includes Regular)
    for i, (label, cost, unit) in enumerate(INCOME_TABLE_OPTIONS):
        if i < 3:
            cnt = plan_counts.get(plan_keys[i], 0)
        else:
            cnt = extra_counts[i - 3]
        total_income = cost * cnt
        tree.insert("", "end", values=(label, f"${cost:.2f} ({unit})", cnt, f"${total_income:.2f}"))
    tk.Button(inner, text="Back to menu", command=win.destroy).pack(anchor="w", pady=10)


# ---------------------------------------------------------------------------
# Help window
# ---------------------------------------------------------------------------

def _open_help_window(parent):
    win = tk.Toplevel(parent)
    win.title("Help – The Aurora Archive")
    win.geometry("500x340")
    win.resizable(True, True)
    win.configure(padx=15, pady=15)

    canvas, scrollbar, inner = _make_scrollable_frame(win)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    text = """
How to use this application

Main menu
  Use the buttons to open the Membership form, Search members, Statistics, or this Help screen. Close any opened window to return to the main menu (or close the main window to exit the application).

Membership form
  Enter the new member’s details: first name, last name, address, and mobile (all required). Choose a membership plan (Standard, Premium, or Kids) and payment plan (Monthly or Annual). Optionally select extras (book rental, private area, booklet, ebook) and/or a library card with a 5-digit card number. Click “Calculate totals” to see costs; click “Submit” to save the member to the database. The form clears only after a successful save. Fix any validation errors shown before submitting.

Search form
  Enter one or more criteria: Member ID, last name, membership plan, or payment plan. You can combine options to narrow results. Click “Search”. Results appear in the table. If no members match, a message is shown. Search is case-insensitive and supports partial matches (e.g. part of a last name).

Statistics form
  View total member count, counts by membership plan and payment plan, counts for each optional extra, how many members have no extras, and how many have a library card. The income table shows cost per option, how many members have that option, and total income (approximation; discounts are not applied).
    """
    tk.Label(inner, text=text.strip(), justify="left", wraplength=420).pack(anchor="w")
    tk.Button(inner, text="Back to menu", command=win.destroy).pack(anchor="w", pady=10)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
