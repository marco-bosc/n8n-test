import socket

# Configurazione
PRINTER_IP = "172.19.18.58"  # Sostituisci con l'IP della stampante Zebra
# PRINTER_IP = "192.168.0.103"  # Sostituisci con l'IP della stampante Zebra
PRINTER_PORT = 9100           # Porta standard per stampanti Zebra via rete
NUM_COPIES = 1                # Numero di copie da stampare

# Template ZPL con segnaposto per i dati dinamici
ZPL_TEMPLATE = """
^XA
^CF0,60
^FO50,50^FD{nome}^FS
^FO50,120^FD{codice}^FS
^FO50,190^BY3^BCN,100,Y,N,N^FD{barcode}^FS
^PQ{copie}  ; Numero di copie
^XZ
"""

# ZPL_TEMPLATE = """
# CT~~CD,~CC^~CT~
# ^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR8,8~SD15^JUS^LRN^CI0^XZ
# ^XA
# ^MMT
# ^PW535
# ^LL0336
# ^LS0
# ^FT492,262^A0I,34,33^FH\^FD{nome}^FS
# ^FT492,211^A0I,28,28^FH\^FD{codice}^FS
# ^BY4,3,110^FT469,63^BCI,,Y,N
# ^FD>;123456789012^FS
# ^PQ1,0,1,Y^XZ
# """

# Dati variabili da sostituire
dati = {
    "nome": "Prodotto XYZ",
    "codice": "ABC123",
    "barcode": "123456789012",
    "copie": NUM_COPIES
}

# Genera il codice ZPL finale sostituendo i valori nel template
zpl_code = ZPL_TEMPLATE.format(**dati)

# Funzione per inviare il codice ZPL alla stampante
def invia_a_stampante(zpl, ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            s.sendall(zpl.encode('utf-8'))
        print("Stampa inviata con successo!")
    except Exception as e:
        print(f"Errore durante l'invio alla stampante: {e}")

# Invia il codice ZPL alla stampante
invia_a_stampante(zpl_code, PRINTER_IP, PRINTER_PORT)
