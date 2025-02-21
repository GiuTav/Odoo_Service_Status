# Odoo_Service_Status

Questa applicazione consente di monitorare e controllare lo stato di vari servizi sul tuo server. Fornisce un'interfaccia web per visualizzare i log, controllare l'utilizzo del disco e gestire lo stato dei servizi.

## Installazione

Per eseguire questa applicazione, è necessario installare le librerie richieste elencate nel file `requirements.txt`. Puoi installarle utilizzando il seguente comando:

```bash
pip install -r requirements.txt
```

## Configurazione

Prima di avviare l'applicazione, crea un file di configurazione (ad esempio, `config.cfg`) con il seguente contenuto:

```ini
[settings]
SECRET_KEY = your_secret_key
USERNAME = your_user
PASSWORD = your_password
```

## Utilizzo

Dopo aver creato il file di configurazione e installato le librerie richieste, puoi avviare l'applicazione specificando il file di configurazione come parametro:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 service_status:app /path/to/your/config.cfg
```

Sostituisci `/path/to/your/config.cfg` con il percorso effettivo del tuo file di configurazione e `service_status` con il nome del tuo modulo principale se è diverso.

## Funzionalità

- Monitorare lo stato di vari servizi
- Visualizzare i log dei servizi con aggiornamenti in tempo reale
- Controllare l'utilizzo del disco
- Controllare i servizi (avvia, ferma, riavvia)

## Licenza

Questo progetto è concesso in licenza sotto la Licenza MIT.
