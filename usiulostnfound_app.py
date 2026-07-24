import os                                                                                                                                                                                                                                                   Code:                                                                                                                                                                                                                                                                                                         .                                                                                                                                                                                                                                                                                      import os
import uuid
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, abort
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from usiulostnfound_database import init_db, get_connection

current_directory = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(current_directory, 'static', 'templates'),
            static_folder=os.path.join(current_directory, 'static'))

# Secret key comes from the environment in real deployments; the fallback keeps
# local development working out of the box.
app.secret_key = os.environ.get('SECRET_KEY', 'usiu_lost_n_found_secure_key_2026')

# Configure a folder to save uploaded item images
UPLOAD_FOLDER = os.path.join(current_directory, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Upload safety: only images, capped at 5 MB per request.
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Make sure the database file and tables exist before serving any request
init_db()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('role'):
            return redirect(url_for('report_form'))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            current = session.get('role')
            if not current:
                return redirect(url_for('report_form'))
            if current not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


def is_allowed_image(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


# ---------------------------------------------------------------------------
# Public / shared routes
# ---------------------------------------------------------------------------
@app.route('/')
def home():
    # Base URL just redirects to the main dashboard
    return redirect(url_for('report_form'))


@app.route('/report', methods=['GET'])
def report_form():
    # Grabs whoever is logged in. If no one is logged in, it will show the login/signup screen!
    current_role = session.get('role', None)
    current_user_name = session.get('user_name', 'Guest')

    conn = get_connection()
    if current_role == 'student':
        # Students only browse items still available to be claimed.
        found_items = conn.execute(
            "SELECT * FROM items WHERE status != 'Claimed' ORDER BY id DESC"
        ).fetchall()
    else:
        found_items = conn.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
    claims = conn.execute("SELECT * FROM claims ORDER BY id DESC").fetchall()
    conn.close()

    return render_template(
        'Lostandfound.html',
        found_items=found_items,
        claims=claims,
        role=current_role,
        user_name=current_user_name
    )


@app.route('/submit-item', methods=['POST'])
@role_required('student')
def handle_item_submission():
    item_category = request.form.get('category')
    item_description = request.form.get('description')
    unique_identifier = request.form.get('identifier')
    location = request.form.get('location')
    date_picked = request.form.get('date')
    contact = request.form.get('finder_contact')

    file = request.files.get('item_photo')
    image_path = None
    if file and file.filename != '':
        if not is_allowed_image(file.filename):
            return "❌ Upload Failed: Only image files (png, jpg, jpeg, webp, gif) are allowed.", 400
        # Give every upload a unique name so two files never overwrite each other.
        safe_name = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{safe_name}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
        image_path = f"uploads/{unique_name}"

    conn = get_connection()
    conn.execute(
        """INSERT INTO items (category, description, identifier, location, date, contact, image_path, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending Security')""",
        (item_category, item_description, unique_identifier, location, date_picked, contact, image_path),
    )
    conn.commit()
    conn.close()

    print(f"\n🤝 FOUND ITEM LOGGED: {item_description} ({item_category})\n")
    return redirect(url_for('report_form'))


@app.route('/submit-claim', methods=['POST'])
@role_required('student')
def handle_claim_submission():
    item_id = request.form.get('item_id') or None
    claimed_item = request.form.get('claimed_item')
    proof_identifier = request.form.get('proof_identifier')
    contact = request.form.get('owner_contact')

    conn = get_connection()
    conn.execute(
        """INSERT INTO claims (item_id, claimed_item, proof_identifier, contact, status)
           VALUES (?, ?, ?, ?, 'Pending')""",
        (item_id, claimed_item, proof_identifier, contact),
    )
    conn.commit()
    conn.close()

    print(f"\n🔍 NEW OWNER CLAIM SUBMITTED for item {item_id}: {claimed_item}\n")
    return redirect(url_for('report_form'))


# ---------------------------------------------------------------------------
# Security-only workflow routes
# ---------------------------------------------------------------------------
@app.route('/items/<int:item_id>/checkin', methods=['POST'])
@role_required('security')
def confirm_checkin(item_id):
    conn = get_connection()
    conn.execute(
        "UPDATE items SET status = 'Checked-In' WHERE id = ? AND status = 'Pending Security'",
        (item_id,),
    )
    conn.commit()
    conn.close()
    print(f"\n📦 ITEM CHECKED IN: item {item_id} secured in vault.\n")
    return redirect(url_for('report_form'))


@app.route('/claims/<int:claim_id>/decision', methods=['POST'])
@role_required('security')
def decide_claim(claim_id):
    decision = request.form.get('decision')
    if decision not in ('approve', 'deny'):
        abort(400)

    conn = get_connection()
    claim = conn.execute("SELECT * FROM claims WHERE id = ?", (claim_id,)).fetchone()
    if claim is None:
        conn.close()
        abort(404)

    if decision == 'approve':
        conn.execute("UPDATE claims SET status = 'Approved' WHERE id = ?", (claim_id,))
        # Releasing an item to its owner marks it as claimed.
        if claim['item_id']:
            conn.execute("UPDATE items SET status = 'Claimed' WHERE id = ?", (claim['item_id'],))
        print(f"\n✅ CLAIM APPROVED: claim {claim_id} released to owner.\n")
    else:
        conn.execute("UPDATE claims SET status = 'Denied' WHERE id = ?", (claim_id,))
        print(f"\n❌ CLAIM DENIED: claim {claim_id} rejected.\n")

    conn.commit()
    conn.close()
    return redirect(url_for('report_form'))


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.route('/logout')
def handle_logout():
    session.clear()  # This completely wipes out the active role!
    session['role'] = None  # Explicitly forces role to be hidden
    return redirect(url_for('report_form'))


# REWRITTEN ROUTE: Process Account Registration with Strict Digit Length Validation
@app.route('/signup', methods=['POST'])
def handle_signup():
    selected_role = request.form.get('role_selection')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    user_id = request.form.get('user_id').strip()
    password = request.form.get('password')

    # Strict Validation: accounts must use an official USIU-A email address
    if not email or not email.strip().lower().endswith('@usiu.ac.ke') \
            or len(email.strip()) <= len('@usiu.ac.ke'):
        return "❌ Registration Failed: Email must be a valid @usiu.ac.ke address.", 400

    # Strict Validation: Check ID lengths based on USIU-A policy
    if selected_role == 'student' and len(user_id) != 6:
        # Returns a basic browser warning if rules are broken
        return "❌ Registration Failed: Student IDs must be exactly 6 digits.", 400

    if selected_role == 'security' and len(user_id) != 9:
        return "❌ Registration Failed: Security Officer Badge IDs must be exactly 9 digits.", 400

    conn = get_connection()

    # Check if user already exists
    existing = conn.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if existing:
        conn.close()
        return "❌ User already exists! Go back and log in.", 400

    # Save user into the database with a hashed password
    conn.execute(
        "INSERT INTO users (user_id, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
        (user_id, full_name, email, generate_password_hash(password), selected_role),
    )
    conn.commit()
    conn.close()

    print(f"\n🔐 DATABASE COMMITTED: New account registered for {full_name} ({user_id})")

    # Log them in dynamically
    session['role'] = selected_role
    session['user_id'] = user_id
    session['user_name'] = full_name

    return redirect(url_for('report_form'))


# REWRITTEN ROUTE: Strict Portal Login Verification
@app.route('/login', methods=['POST'])
def handle_login():
    selected_role = request.form.get('role_selection')
    user_id = request.form.get('user_id').strip()
    password = request.form.get('password')

    conn = get_connection()
    account = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()

    # Verify the user exists, the password matches the stored hash, and the
    # chosen dashboard role matches the account role.
    if account and check_password_hash(account['password'], password) \
            and account['role'] == selected_role:
        session['role'] = selected_role
        session['user_id'] = user_id
        session['user_name'] = account['name']
        print(f"\n✅ ACCESS GRANTED: {account['name']} logged into {selected_role} view.")
        return redirect(url_for('report_form'))

    # If verification fails at any stage
    print(f"\n🚨 ACCESS DENIED: Invalid login attempt for ID {user_id}")
    return "❌ Authentication Failed: Invalid Credentials or unauthorized role selected.", 401


if __name__ == '__main__':
    app.run(debug=True)
