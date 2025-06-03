# import json

# def get_articoli():
#     with open("articlesAirTable.json", "r", encoding="utf-8") as file:
#         return json.load(file)


# data_source.py
import json

# Config globale
# USE_SOURCE = "odoo"  # Cambia tra "odoo" e "airtable"

def get_articoli(USE_SOURCE):
    if USE_SOURCE == "odoo":
        return get_articoli_odoo()
    elif USE_SOURCE == "airtable":
        return get_articoli_airtable()
    else:
        raise ValueError("Sorgente non valida")

def get_articoli_airtable():
    with open("articlesAirTable.json", "r", encoding="utf-8") as f:
        dati = json.load(f)
        return [
            {
                "id": str(r["id"]),
                "nome": r["fields"].get("Nome", "Senza Nome"),
                "prezzo": r["fields"].get("Prezzo", 0.0),
                "barcode_source": r["fields"].get("Barcode", "N/A")
            }
            for r in dati
        ]

def get_articoli_odoo():
    with open("articlesOdoo.json", "r", encoding="utf-8") as f:
        prodotti = json.load(f)
        return [
            {
                "id": str(p["id"]),
                "nome": p["name"],
                "prezzo": p["list_price"],
                "barcode_source": p["barcode"]
            }
            for p in prodotti
        ]
