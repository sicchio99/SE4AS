#!/bin/bash

# Avvia il server Redis
redis-server --daemonize yes

# Attendi che il server Redis sia pronto
until redis-cli ping >/dev/null 2>&1; do
    echo "Attendo il server Redis..."
    sleep 1
done

echo "Il server Redis è pronto."

# Estrai il nome del file JSON
filename=$(basename /Configuration.json)

# Leggi il contenuto del file JSON
json_data=$(cat /Configuration.json)

# Inserisci nel database Redis
redis-cli SET "$filename" "$json_data"

echo "Dati JSON importati con successo nel database Redis."

# Mantieni lo script in esecuzione in background
tail -f /dev/null





