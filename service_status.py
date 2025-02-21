import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import subprocess
import bcrypt
import psutil
from flask_wtf.csrf import CSRFProtect
from configparser import ConfigParser

# Carica la configurazione
if len(sys.argv) > 1:
    config_file_path = sys.argv[1]
else:
    config_file_path = 'config.cfg'

config = ConfigParser()
config.read(config_file_path)

app = Flask(__name__)
app.secret_key = config.get('settings', 'SECRET_KEY')

csrf = CSRFProtect(app)

USERNAME = config.get('settings', 'USERNAME')
PASSWORD_HASH = bcrypt.hashpw(config.get('settings', 'PASSWORD').encode('utf-8'), bcrypt.gensalt(rounds=12))

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

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username or not password:
            return render_template('login.html', error="Username e password sono obbligatori")
        if username == USERNAME and bcrypt.checkpw(password, PASSWORD_HASH):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Credenziali errate")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    disk_usage = get_disk_usage()
    hostname = get_hostname()
    statuses = {service: get_service_status(service) for service in SERVICES}
    return render_template('dashboard.html', disk_usage=disk_usage, hostname=hostname, statuses=statuses)

@app.route('/status')
def status():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 403
    statuses = {service: get_service_status(service) for service in SERVICES}
    return jsonify(statuses)

@app.route('/disk_usage')
def disk_usage():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(get_disk_usage())

@app.route('/control', methods=['POST'])
def control_service():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 403
    service = request.json.get('service')
    action = request.json.get('action')
    sudo_password = request.json.get('password')
    if service in SERVICES:
        message = execute_service_command(action, service, sudo_password)
    else:
        message = "Servizio non valido"
    return jsonify({"message": message})

@app.route('/logs/<service>')
def logs(service):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('logs.html', service=service)

@app.route('/logs_data/<service>')
def logs_data(service):
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 403
    if service in SERVICES:
        log_output = get_service_logs(service)
    else:
        log_output = "Servizio non valido"
    return jsonify({"log_output": log_output})

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
