# Odoo Service Status

## 📌 Descrizione
Questa applicazione web consente di monitorare e controllare lo stato dei servizi Odoo e PostgreSQL su un server Linux. Gli utenti possono avviare, arrestare e riavviare i servizi, nonché visualizzare i log direttamente dall'interfaccia web.

## 🚀 Installazione
Per installare l'applicazione, è **consigliato** creare un ambiente virtuale `virtualenv` per mantenere le dipendenze isolate.

### **1️⃣ Creazione di un ambiente virtuale**
```sh
python3 -m venv venv
source venv/bin/activate  # Per Linux/macOS
venv\Scripts\activate    # Per Windows
```

### **2️⃣ Installazione delle dipendenze**
```sh
pip install -r requirements.txt
```

## 🔑 Configurazione del file `.env`
Per far funzionare l'applicazione, è necessario creare un file `.env` nella directory principale del progetto con le seguenti variabili di ambiente:

```ini
SECRET_KEY=tuo_secret_key
USERNAME=tuo_username
PASSWORD=tuo_password_hash
```

⚠️ **Importante:** La password deve essere memorizzata come hash bcrypt per garantire la sicurezza.

### **🔐 Generazione dell'hash della password**
Per generare un hash della password, utilizza il seguente script Python:

```python
import bcrypt

password = "tua_password"
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(hashed_password.decode('utf-8'))
```

Copia l'output e incollalo nel file `.env` nella variabile `PASSWORD`.

## 🚀 Avvio dell'Applicazione
Una volta configurato tutto, avvia l'applicazione con:

```sh
python service_status.py
```

Ora puoi accedere all'applicazione tramite il browser all'indirizzo:
```
http://127.0.0.1:5000/
```

## 📜 Funzionalità Principali
✅ Monitoraggio dello stato dei servizi Odoo e PostgreSQL
✅ Avvio, Arresto e Riavvio dei servizi
✅ Visualizzazione dei log
✅ Protezione con autenticazione

---
Made with ❤️ by Giuseppe Tavormina 🚀
