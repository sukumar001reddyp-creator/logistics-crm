from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "logistics.db")
app = Flask(__name__)
app.secret_key = "logisticscrm123"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- AUTH ROUTES ---
@app.route('/login')
def login(): return render_template('login.html')

@app.route('/login_check', methods=['POST'])
def login_check():

    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    if role == "admin":

        conn = get_db_connection()

    admin = conn.execute(
        """
        SELECT * FROM admins
        WHERE username=?
        AND password=?
        """,
        (username, password)
    ).fetchone()

    conn.close()

    if admin:

        session['user'] = admin['username']

        return redirect('/')

    elif role == "employee":

        conn = get_db_connection()

        employee = conn.execute(
            """
            SELECT * FROM employees
            WHERE username=?
            AND password=?
            """,
            (username, password)
        ).fetchone()

        conn.close()

        if employee:

            session['employee'] = employee['username']
            return redirect('/employee_dashboard')

    return "Invalid Login Details"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')
   
@app.route('/employee_dashboard')
def employee_dashboard():

    if 'employee' not in session:
        return redirect('/employee_login')

    conn = get_db_connection()

    total_shipments = conn.execute(
        "SELECT COUNT(*) FROM shipments"
    ).fetchone()[0]

    pending_shipments = conn.execute(
        "SELECT COUNT(*) FROM shipments WHERE status='Pending'"
    ).fetchone()[0]

    delivered_shipments = conn.execute(
        "SELECT COUNT(*) FROM shipments WHERE status='Delivered'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        'employee_dashboard.html',
        total_shipments=total_shipments,
        pending_shipments=pending_shipments,
        delivered_shipments=delivered_shipments
    )  
@app.route('/employee_logout')
def employee_logout():

    session.pop('employee', None)

    return redirect('/login')

    session.pop('employee', None)

    return redirect('/employee_login')         

# --- DASHBOARD ---
@app.route('/')
def dashboard():
    if 'user' not in session: return redirect('/login')
    conn = get_db_connection()
    total_clients = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    total_shipments = conn.execute("SELECT COUNT(*) FROM shipments").fetchone()[0]
    delivered = conn.execute("SELECT COUNT(*) FROM shipments WHERE status = 'Delivered'").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM shipments WHERE status = 'Pending'").fetchone()[0]
    shipments_data = conn.execute("SELECT * FROM shipments").fetchall()
    conn.close()
    return render_template('dashboard.html', total_clients=total_clients, total_shipments=total_shipments, 
                           delivered_shipments=delivered, pending_shipments=pending, shipments=shipments_data)

# --- SHIPMENTS ROUTES ---
@app.route('/shipments')
def shipments():

    if 'user' not in session and 'employee' not in session:
        return redirect('/login')

    conn = get_db_connection()

    data = conn.execute(
        "SELECT * FROM shipments"
    ).fetchall()

    conn.close()

    return render_template(
        'shipments.html',
        shipments=data
    )

@app.route('/add_shipment', methods=['POST'])
def add_shipment():
    conn = get_db_connection()
    conn.execute("INSERT INTO shipments (client_name, origin, destination, status) VALUES (?,?,?,?)",
                 (request.form['client_name'], request.form['origin'], request.form['destination'], request.form['status']))
    conn.commit()
    conn.close()
    return redirect('/shipments')

@app.route('/edit_shipment/<int:id>')
def edit_shipment(id):
    conn = get_db_connection()
    s = conn.execute("SELECT * FROM shipments WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template('edit_shipment.html', shipment=s)

@app.route('/update_shipment/<int:id>', methods=['POST'])
def update_shipment(id):
    conn = get_db_connection()
    conn.execute("UPDATE shipments SET client_name=?, origin=?, destination=?, status=? WHERE id=?",
                 (request.form['client_name'], request.form['origin'], request.form['destination'], request.form['status'], id))
    conn.commit()
    conn.close()
    return redirect('/shipments')

@app.route('/delete_shipment/<int:id>')
def delete_shipment(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM shipments WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/shipments')

# --- INVOICES ROUTES ---
@app.route('/invoices')
def invoices():

    if 'user' not in session:
        return "Access Denied"

    conn = get_db_connection()

    data = conn.execute(
        "SELECT * FROM invoices"
    ).fetchall()

    conn.close()

    return render_template(
        'invoices.html',
        invoices=data
    )

@app.route('/add_invoice', methods=['POST'])
def add_invoice():
    conn = get_db_connection()
    conn.execute("INSERT INTO invoices (invoice_no, client_name, amount, invoice_date, status) VALUES (?,?,?,?,?)",
                 (request.form['invoice_no'], request.form['client_name'], request.form['amount'], request.form['invoice_date'], request.form['status']))
    conn.commit()
    conn.close()
    return redirect('/invoices')

@app.route('/edit_invoice/<int:id>')
def edit_invoice(id):
    conn = get_db_connection()
    i = conn.execute("SELECT * FROM invoices WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template('edit_invoice.html', invoice=i)

@app.route('/update_invoice/<int:id>', methods=['POST'])
def update_invoice(id):
    conn = get_db_connection()
    conn.execute("UPDATE invoices SET invoice_no=?, client_name=?, amount=?, invoice_date=?, status=? WHERE id=?",
                 (request.form['invoice_no'], request.form['client_name'], request.form['amount'], request.form['invoice_date'], request.form['status'], id))
    conn.commit()
    conn.close()
    return redirect('/invoices')

@app.route('/delete_invoice/<int:id>')
def delete_invoice(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM invoices WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/invoices')
@app.route('/employees')
def employees():

    if 'user' not in session:
        return "Access Denied"

    conn = get_db_connection()

    employees = conn.execute(
        "SELECT * FROM employees"
    ).fetchall()

    conn.close()

    return render_template(
    'employees.html',
    employees=employees,
    active='employees'
)
@app.route('/add_employee', methods=['POST'])
def add_employee():

    if 'user' not in session:
        return "Access Denied"

    conn = get_db_connection()

    conn.execute("""
    INSERT INTO employees
    (name, username, password)
    VALUES (?, ?, ?)
    """, (
        request.form['name'],
        request.form['username'],
        request.form['password']
    ))

    conn.commit()
    conn.close()

    return redirect('/employees') 

@app.route('/edit_employee/<int:id>')
def edit_employee(id):

    if 'user' not in session:
        return "Access Denied"

    conn = get_db_connection()

    employee = conn.execute(
        "SELECT * FROM employees WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        'edit_employee.html',
        employee=employee
    )
@app.route('/update_employee/<int:id>', methods=['POST'])
def update_employee(id):

    if 'user' not in session:
        return "Access Denied"

    conn = get_db_connection()

    conn.execute("""
    UPDATE employees
    SET name=?,
        username=?,
        password=?
    WHERE id=?
    """, (
        request.form['name'],
        request.form['username'],
        request.form['password'],
        id
    ))

    conn.commit()
    conn.close()

    return redirect('/employees')
@app.route('/delete_employee/<int:id>')
def delete_employee(id):

    if 'user' not in session:
        return "Access Denied"

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM employees WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/employees')            
@app.route('/create_employees_table')
def create_employees_table():

    conn = get_db_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        username TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

    return "Employees table created successfully"       
# --- CLIENTS ROUTES ---
@app.route('/clients')
def clients():

    if 'user' not in session:
        return "Access Denied"

    search = request.args.get('search', '')

    conn = get_db_connection()

    data = conn.execute(
        "SELECT * FROM clients WHERE company LIKE ? OR contact_person LIKE ? OR country LIKE ?",
        (f'%{search}%', f'%{search}%', f'%{search}%')
    ).fetchall()

    conn.close()

    return render_template(
        'clients.html',
        clients=data,
        search=search
    )

@app.route('/add_client', methods=['POST'])
def add_client():
    conn = get_db_connection()
    conn.execute("INSERT INTO clients (company, contact_person, phone, email, country) VALUES (?,?,?,?,?)",
                 (request.form['company'], request.form['contact_person'], request.form['phone'], request.form['email'], request.form['country']))
    conn.commit()
    conn.close()
    return redirect('/clients')

@app.route('/edit_client/<int:id>')
def edit_client(id):
    conn = get_db_connection()
    c = conn.execute("SELECT * FROM clients WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template('edit_client.html', client=c)

@app.route('/update_client/<int:id>', methods=['POST'])
def update_client(id):
    conn = get_db_connection()
    conn.execute("UPDATE clients SET company=?, contact_person=?, phone=?, email=?, country=? WHERE id=?",
                 (request.form['company'], request.form['contact_person'], request.form['phone'], request.form['email'], request.form['country'], id))
    conn.commit()
    conn.close()
    return redirect('/clients')

@app.route('/delete_client/<int:id>')
def delete_client(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM clients WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/clients')

# --- REPORTS ---
@app.route('/reports')
def reports():

    if 'user' not in session:
        return "Access Denied"

    conn = get_db_connection()

    revenue = conn.execute(
        "SELECT SUM(amount) FROM invoices WHERE status='Paid'"
    ).fetchone()[0] or 0

    pending = conn.execute(
        "SELECT COUNT(*) FROM invoices WHERE status='Unpaid'"
    ).fetchone()[0]

    paid = conn.execute(
        "SELECT COUNT(*) FROM invoices WHERE status='Paid'"
    ).fetchone()[0]

    total_clients = conn.execute(
        "SELECT COUNT(*) FROM clients"
    ).fetchone()[0]

    total_shipments = conn.execute(
        "SELECT COUNT(*) FROM shipments"
    ).fetchone()[0]

    total_invoices = conn.execute(
        "SELECT COUNT(*) FROM invoices"
    ).fetchone()[0]

    monthly = conn.execute("""
        SELECT
        strftime('%Y-%m', invoice_date) as month,
        COUNT(*) as count,
        SUM(amount) as revenue
        FROM invoices
        GROUP BY month
        ORDER BY month DESC
    """).fetchall()

    conn.close()

    return render_template(
        'reports.html',
        total_revenue=revenue,
        pending_count=pending,
        paid_count=paid,
        total_clients=total_clients,
        total_shipments=total_shipments,
        total_invoices=total_invoices,
        monthly_data=monthly
    )
@app.route('/change_admin_password')
def change_admin_password():

    if 'user' not in session:
        return redirect('/login')

    return render_template('change_admin_password.html')

@app.route('/update_admin_password', methods=['POST'])
def update_admin_password():

    if 'user' not in session:
        return redirect('/login')

    current_password = request.form['current_password']
    new_password = request.form['new_password']

    conn = get_db_connection()

    admin = conn.execute(
        """
        SELECT * FROM admins
        WHERE username=?
        AND password=?
        """,
        (session['user'], current_password)
    ).fetchone()

    if not admin:
        conn.close()
        return "Current Password Wrong"

    conn.execute(
        """
        UPDATE admins
        SET password=?
        WHERE username=?
        """,
        (new_password, session['user'])
    )

    conn.commit()
    conn.close()

    return "Password Updated Successfully"
@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['POST'])
def reset_password():

    username = request.form['username']
    new_password = request.form['new_password']
    secret_code = request.form['secret_code']

    if secret_code != "LOGISTICS2026":
        return "Invalid Secret Code"

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE admins
        SET password=?
        WHERE username=?
        """,
        (new_password, username)
    )

    conn.commit()
    conn.close()

    return "Password Reset Successfully"



@app.route('/create_admin_table')
def create_admin_table():

    conn = get_db_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    conn.execute("""
    INSERT INTO admins
    (username, password)
    SELECT 'admin', '1234'
    WHERE NOT EXISTS (
        SELECT 1 FROM admins
    )
    """)

    conn.commit()
    conn.close()

    return "Admin table created"   
if __name__ == '__main__':
    app.run(debug=True)