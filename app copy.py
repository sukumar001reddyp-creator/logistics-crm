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
    if request.form['username'] == "admin" and request.form['password'] == "1234":
        session['user'] = "admin"
        return redirect('/')
    return "Invalid Username or Password."

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

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
    if 'user' not in session: return redirect('/login')
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM shipments").fetchall()
    conn.close()
    return render_template('shipments.html', shipments=data)

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
    if 'user' not in session: return redirect('/login')
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM invoices").fetchall()
    conn.close()
    return render_template('invoices.html', invoices=data)

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

# --- CLIENTS ROUTES ---
@app.route('/clients')
def clients():
    if 'user' not in session: return redirect('/login')
    search = request.args.get('search', '')
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM clients WHERE company LIKE ? OR contact_person LIKE ? OR country LIKE ?", 
                        (f'%{search}%', f'%{search}%', f'%{search}%')).fetchall()
    conn.close()
    return render_template('clients.html', clients=data, search=search)

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
        return redirect('/login')

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
if __name__ == '__main__':
    app.run(debug=True)