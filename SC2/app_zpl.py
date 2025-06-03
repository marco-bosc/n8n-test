from flask import Flask, render_template, request, redirect, url_for, flash  # type: ignore
import os
from data_source import get_articoli
import importData
import socket
import csv
from werkzeug.utils import secure_filename # type: ignore

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Imposta una chiave segreta per utilizzare 'flash'

# Cartella per salvare i file ZPL
ZPL_FOLDER = "static/zpl"
os.makedirs(ZPL_FOLDER, exist_ok=True)

# Configurazione stampante Zebra
PRINTER_IP = "192.168.1.100"  # Sostituisci con l'IP della stampante Zebra
PRINTER_PORT = 9100           # Porta standard per stampanti Zebra via rete
ENABLE_PRINT = False  

USE_SOURCE = "odoo"  # Cambia tra "odoo" e "airtable"

UPLOAD_FOLDER = './static/uploaded'
TEMPLATE_PATH = './templates/template.zpl'

# Template ZPL con segnaposto per i dati dinamici
ZPL_TEMPLATE = """
^XA
^CF0,60
^FO50,50^FD{nome}^FS
^FO50,120^FD{prezzo} EUR^FS
^FO50,190^BY3^BCN,100,Y,N,N^FD{barcode}^FS
^PQ{copie}
^XZ
"""

# Funzione per generare cartellini ZPL
def genera_cartellino_zpl(articolo, quantita):
    nome, prezzo, barcode_source = articolo["nome"], articolo["prezzo"], articolo["barcode_source"]
    prezzo = f"{prezzo:.2f}"  # Formatta il prezzo con due decimali

    if not barcode_source:
        flash("Errore: l'articolo selezionato non ha un codice a barre valido.", "danger")
        return None, None        

    zpl_code = ZPL_TEMPLATE.format(nome=nome, prezzo=prezzo, barcode=barcode_source, copie=quantita)

    # Rimuovi tutti i file nella cartella
    
    for file_name in os.listdir(ZPL_FOLDER):
        file_path = os.path.join(ZPL_FOLDER, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

    file_name = f"{ZPL_FOLDER}/cartellino_{barcode_source}.zpl"
    with open(file_name, "w") as file:
        file.write(zpl_code)

    return file_name, zpl_code  # Restituisce sia il file salvato che il contenuto ZPL

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/visualizza_cartellini_zpl")
def visualizza_cartellini_zpl():
    cartellini_zpl = []
    for file in os.listdir(ZPL_FOLDER):
        if file.endswith(".zpl"):
            with open(os.path.join(ZPL_FOLDER, file), "r") as f:
                cartellini_zpl.append(f.read())
    return render_template("visualizza_cartellini_zpl.html", cartellini=cartellini_zpl)

@app.route("/stampa_etichette", methods=["GET", "POST"])
def stampa_etichette():
    articoli = get_articoli(USE_SOURCE)
    if request.method == "POST":
        articolo_id = request.form["articolo"]
        quantita = int(request.form["quantita"])
        articolo = next(a for a in articoli if a["id"] == articolo_id)

        _, zpl_code = genera_cartellino_zpl(articolo, quantita)
        
        if zpl_code is None:
            return redirect(url_for("stampa_etichette"))

        try:
            invia_a_stampante(zpl_code)
            flash("Stampa inviata con successo!", "success")
        except Exception as e:
            flash(f"Errore nella stampa: {e}", "danger")
        
        ### Per visualizzare zpl su pagina Web
        # return redirect(url_for("visualizza_cartellini_zpl"))
    return render_template("stampa_etichette.html", articoli=articoli)

@app.route("/scansione_e_stampa", methods=["GET", "POST"])
def scansione_e_stampa():
    articoli = get_articoli(USE_SOURCE)
    if request.method == "POST":
        barcode = request.form["barcode"]
        quantita = 1
        # articolo = next(a for a in articoli if a["barcode_source"] == barcode)

        articolo = next((a for a in articoli if a["barcode_source"] == barcode), None)

        if articolo is None:
            flash(f"Nessun articolo trovato con il barcode '{barcode}'", "danger")
            return redirect(url_for("scansione_e_stampa"))  # nome della route

        _, zpl_code = genera_cartellino_zpl(articolo, quantita)

        if zpl_code is None:
            return redirect(url_for("stampa_etichette"))

        try:
            invia_a_stampante(zpl_code)
            flash("Stampa inviata con successo!", "success")
        except Exception as e:
            flash(f"Errore nella stampa: {e}", "danger")
        
        ### Per visualizzare zpl su pagina Web
        # return redirect(url_for("visualizza_cartellini_zpl"))
    return render_template("scansione_e_stampa.html", articoli=articoli)

@app.route("/stampa_batch", methods=["GET", "POST"])
def stampa_batch():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Nessun file caricato', 400

        file = request.files['file']
        if file.filename == '':
            return 'Nome file mancante', 400

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(file.filename)
        path_csv = os.path.join(UPLOAD_FOLDER, 'ultimo.csv')
        file.save(path_csv)

        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template = f.read()

        delimiter = request.form.get('delimiter', ';')  # di default punto e virgola

        zpl_batch = ''
        with open(path_csv, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            for row in reader:
                zpl = template
                for chiave, valore in row.items():
                    chiave = chiave.strip()
                    valore = valore.strip()
                    zpl = zpl.replace(f"{{{{{chiave}}}}}", valore)
                zpl_batch += zpl.strip() + '\n'

        try:
            invia_a_stampante(zpl_batch)
            flash("Stampa inviata con successo!", "success")
        except Exception as e:
            flash(f"Errore nella stampa: {e}", "danger")
        
        ### Per visualizzare testo ZPL
        # return zpl_batch

    return render_template('stampa_batch.html')

@app.route("/aggiorna_archivio")
def aggiorna_archivio():
    try:
        importData.main(USE_SOURCE)
        flash("Archivio aggiornato con successo!", "success")
        return redirect(url_for('home'))
    except Exception as e:
        flash(f"Si è verificato un errore durante l'aggiornamento dell'archivio: {e}", "danger")
        return redirect(url_for('home'))

# Invia il codice ZPL a una stampante Zebra via rete.
def invia_a_stampante(zpl):
    if not ENABLE_PRINT:
        print("Modalità test attiva. Questo è il codice ZPL generato:\n")
        print(zpl)
        return zpl

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((PRINTER_IP, PRINTER_PORT))
            s.sendall(zpl.encode('utf-8'))
        print("Stampa inviata con successo!")
    except Exception as e:
        print(f"Errore durante l'invio alla stampante: {e}")

if __name__ == "__main__":
    app.run(debug=True)
