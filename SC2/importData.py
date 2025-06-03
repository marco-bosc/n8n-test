import json
import os
import requests
import importOdoo
from pathlib import Path

# Configurazione
BASE_ID = "appRB7XZwAF7YeXnp"  # Sostituiscilo con il tuo Base ID
TABLE_NAME = "Articoli"  # Sostituiscilo con il nome della tabella
API_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
API_TOKEN = "patN0jOi0o0WwpGTX.e32d9fcc966c2149e468191b81989700bc9f879c5b4af1d70cb88b0d80a4d965"  # Sostituiscilo con il tuo token
STORICO_FILE = "storico.json"

def scarica_dati():
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("records", [])  # Ritorna solo la lista di record
    else:
        print("Errore:", response.text)
        return []

def salva_storico(data):
    """Salva i dati correnti come storico."""
    with open(STORICO_FILE, "w") as f:
        json.dump(data, f, indent=4)

def carica_storico():
    """Carica lo storico precedente."""
    if Path(STORICO_FILE).exists():
        with open(STORICO_FILE, "r") as f:
            return json.load(f)
    return []

def confronta_storico(nuovi_dati, storico):
    storico_ids = {item["id"] for item in storico}  # Confrontiamo con "id"
    nuovi_articoli = [item for item in nuovi_dati if item["id"] not in storico_ids]
    return nuovi_articoli

def trasforma_elenco(input_file, output_file):
    with open(input_file, 'r') as f:
        dati = json.load(f)

    articoli = []
    
    for item in dati:
        fields = item.get("fields", {})
        articolo = {
            "id": item["id"],
            "nome": fields.get("Name", ""),
            "prezzo": fields.get("Prezzo di Vendita", []),
            "barcode_source": fields.get("Barcode", []) if fields.get("Barcode", []) else ""
        }
        articoli.append(articolo)

    with open(output_file, 'w') as f:
        json.dump(articoli, f, indent=4)

def update_from_airtable():
    print("Inizio del programma")
    
    # Step 1: Scarica i dati
    nuovi_dati = scarica_dati()

    # Step 2: Confronta con lo storico
    storico = carica_storico()
    nuovi_articoli = confronta_storico(nuovi_dati, storico)

    if nuovi_articoli:
        print(f"Nuovi articoli trovati: {len(nuovi_articoli)}")
        salva_storico(nuovi_dati)  # Aggiorna lo storico
    else:
        print("Nessun nuovo articolo trovato.")
        return

    # Step 3: Trasforma e salva i dati
    trasforma_elenco(STORICO_FILE, 'articlesAirTable.json')
    print("Dati trasformati e salvati in 'articlesAirTable.json'.")

def update_from_odoo():
    importOdoo.main()

def main(USE_SOURCE):
    if USE_SOURCE == "airtable":
        update_from_airtable()
    if USE_SOURCE == "odoo":
        return update_from_odoo()
    else:
        raise ValueError("Sorgente non valida")



if __name__ == "__main__":
    main()