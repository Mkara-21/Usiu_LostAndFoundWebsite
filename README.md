# USIU-A Lost & Found System

A modern, secure web application designed for **United States International University - Africa (USIU-A)** to streamline the process of reporting lost items and reclaiming found belongings on campus.

The system bridges students and campus security officers, introducing digital tracking, vault check-ins, and verified claim approvals.

---

## 🌟 Features

### 1. Role-Based Dashboards
* **Students**:
  * View current list of unclaimed items.
  * Report found items (upload descriptions, locations, and images).
  * Submit ownership claims for lost items with proof identifiers.
* **Security Officers**:
  * Track all items (pending security, checked-in, and claimed).
  * Check items into the vault.
  * Review, approve, or deny student ownership claims.

### 2. Strict Access Control & Registration Validation
* **USIU-A Email Restriction**: Users must sign up with a valid `@usiu.ac.ke` email address.
* **ID Format Verification**:
  * **Students**: Must use a 6-digit Student ID.
  * **Security**: Must use a 9-digit Badge ID.
* **Password Complexity Policy**: Enforces strong passwords (minimum 8 characters, containing at least one uppercase letter, one lowercase letter, one digit, and one special character) on both client and server sides.

---

## 🛠️ Technology Stack

* **Backend**: Python 3, Flask framework
* **Database**: SQLite3
* **Frontend**: HTML5, Vanilla CSS, JavaScript
* **Security & Auth**: Werkzeug security hashing (`generate_password_hash` / `check_password_hash`)

---

## 🚀 Getting Started

### 1. Installation & Setup
Clone the repository and install dependencies (e.g., Flask, Werkzeug).

```bash
# Set up a Python virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install Flask
pip install Flask
```

### 2. Database Initialization
Run the database setup script to create the SQLite tables and seed the initial credentials:
```bash
python3 usiulostnfound_database.py
```
*Note: Due to a structural mix-up, the database initialization code currently resides in the same file as the Flask application. Running `usiulostnfound_database.py` initializes the database and launches the web application.*

### 3. Running the App
Run the Flask application:
```bash
python3 usiulostnfound_database.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser to access the portal.

---

## 🔒 Security Configuration Notes
* **Secret Key**: Ensure you define the `SECRET_KEY` environment variable in production.
* **Debug Mode**: The app runs in debug mode (`debug=True`) by default for local development. Make sure to turn off debugging (`debug=False`) when hosting public instances.
