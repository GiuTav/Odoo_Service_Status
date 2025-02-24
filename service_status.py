import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import subprocess
import bcrypt
import psutil
from flask_wtf.csrf import CSRFProtect
from configparser import ConfigParser, NoSectionError
from dotenv import load_dotenv

# Carica le variabili dal file .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
USERNAME = os.getenv("USERNAME")
PASSWORD_HASH = os.getenv("PASSWORD").encode('utf-8')  # Convertiamo la stringa in bytes

app = Flask(__name__, static_url_path='/service/static', static_folder='static', subdomain_matching=True)
app.config['APPLICATION_ROOT'] = '/service'
app.secret_key = SECRET_KEY
csrf = CSRFProtect(app)

# Trova tutti i servizi Odoo automaticamente
def get_odoo_services():
    try:
        result = subprocess.run(["systemctl", "list-unit-files", "--type=service", "--no-pager"], capture_output=True, text=True)
        services = [line.split()[0] for line in result.stdout.splitlines() if "odoo" in line]
        return services
    except Exception as e:
        return []

SERVICES = get_odoo_services() + ["postgresql"]  # Aggiunto PostgreSQL

def execute_service_command(command, service_name, sudo_password):
    try:
        result = subprocess.run(
            ["sudo", "-S", "systemctl", command, service_name],
            input=sudo_password + "\n", capture_output=True, text=True, check=True
        )
        return f"Servizio {service_name} {command} con successo"
    except Exception as e:
        return f"Errore: {str(e)}"

def get_service_status(service_name):
    try:
        result = subprocess.run(["systemctl", "is-active", service_name], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Errore: {str(e)}"

def get_service_logs(service_name):
    try:
        result = subprocess.run(["journalctl", "-u", service_name, "--no-pager", "-n", "200", "--output", "cat"],
                                capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Errore: {str(e)}"

def get_disk_usage():
    try:
        usage = psutil.disk_usage('/')
        return {"used": usage.used / (1024 ** 3), "total": usage.total / (1024 ** 3), "percent": usage.percent}
    except Exception as e:
        return {"error": str(e)}

def get_hostname():
    try:
        result = subprocess.run(["hostname"], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Errore: {str(e)}"

@app.route('/service/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('login.html', error="Username e password sono obbligatori")
        if username == USERNAME and bcrypt.checkpw(password.encode('utf-8'), PASSWORD_HASH):
            session['logged_in'] = True
            return redirect(url_for('dashboard', _external=True))
    return render_template('login.html')

@app.before_request
def fix_proxy_headers():
    if request.headers.get('X-Forwarded-Proto') == 'https':
        request.environ['wsgi.url_scheme'] = 'https'

app.config.update(
    SESSION_COOKIE_PATH="/service",
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    WTF_CSRF_TIME_LIMIT=None  # Disabilita il timeout del CSRF Token
)

@app.route('/service/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    disk_usage = get_disk_usage()
    hostname = get_hostname()
    statuses = {service: get_service_status(service) for service in SERVICES}
    return render_template('dashboard.html', disk_usage=disk_usage, hostname=hostname, statuses=statuses)

@app.route('/service/status')
def status():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 403
    statuses = {service: get_service_status(service) for service in SERVICES}
    return jsonify(statuses)

@app.route('/service/disk_usage')
def disk_usage():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(get_disk_usage())

@app.route('/service/control', methods=['POST'])
def control_service():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json(force=True)
    service = data.get('service')
    action = data.get('action')
    sudo_password = data.get('password')

    if not service or not action or not sudo_password:
        return jsonify({"error": "Dati mancanti"}), 400

    if service in SERVICES:
        message = execute_service_command(action, service, sudo_password)
    else:
        message = "Servizio non valido"

    return jsonify({"message": message})

@app.route('/service/logs/<service>')
def logs(service):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('logs.html', service=service)

@app.route('/service/logs_data/<service>')
def logs_data(service):
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 403
    if service in SERVICES:
        log_output = get_service_logs(service)
    else:
        log_output = "Servizio non valido"
    return jsonify({"log_output": log_output})

@app.route('/service/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
