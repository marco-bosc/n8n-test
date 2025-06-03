# import xmlrpc.client
# import json

# # Configurazione Odoo
# url = "http://localhost:8069"               # Da browser locale
# db = "odoo-18"                              # Come da docker-compose
# username = "caricospam+odoo18@gmail.com"    # Cambia con il tuo utente Odoo
# password = "password"                       # Cambia con la tua password

# # Connessione
# common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
# uid = common.authenticate(db, username, password, {})

# if not uid:
#     print("Errore: Autenticazione fallita")
#     exit()

# models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# # Scarica prodotti (product.product ha taglia e barcode, product.template no)
# prodotti = models.execute_kw(
#     db, uid, password,
#     'product.product', 'search_read',
#     [[]],  # Nessun filtro
#     {
#         'fields': ['id', 'name', 'barcode', 'list_price', 'default_code'],
#         'limit': 1000
#     }
# )

# # Salva in JSON
# with open("prodotti_odoo.json", "w") as f:
#     json.dump(prodotti, f, indent=4, ensure_ascii=False)

# print(f"{len(prodotti)} prodotti esportati da Odoo.")

import xmlrpc.client
import json

# Configurazione Odoo
url = "http://localhost:8069"
db = "odoo-18"
username = "caricospam+odoo18@gmail.com"
password = "password"

def main():
    # Connessione
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})

    if not uid:
        raise ValueError("Errore: Autenticazione fallita")
        exit()

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    # Step 1: Estrai prodotti
    prodotti = models.execute_kw(
        db, uid, password,
        'product.product', 'search_read',
        [[]],
        {
            'fields': [
                'id', 'name', 'barcode', 'list_price',
                'default_code', 'product_template_attribute_value_ids'
            ],
            'limit': 1000
        }
    )

    # Step 2: Estrai le varianti per ogni prodotto
    for prodotto in prodotti:
        variants_dict = {}

        ptav_ids = prodotto.get('product_template_attribute_value_ids', [])
        if ptav_ids:
            ptavs = models.execute_kw(
                db, uid, password,
                'product.template.attribute.value', 'read',
                [ptav_ids],
                {'fields': ['product_attribute_value_id']}
            )

            pav_ids = [ptav['product_attribute_value_id'][0] for ptav in ptavs]
            pavs = models.execute_kw(
                db, uid, password,
                'product.attribute.value', 'read',
                [pav_ids],
                {'fields': ['name', 'attribute_id']}
            )

            for pav in pavs:
                attribute_name = pav['attribute_id'][1]  # (id, name)
                value_name = pav['name']
                variants_dict[attribute_name] = value_name

        prodotto['variants'] = variants_dict
        # Rimuovo il campo tecnico
        prodotto.pop('product_template_attribute_value_ids', None)

    # Salva in JSON
    with open("articlesOdoo.json", "w") as f:
        json.dump(prodotti, f, indent=4, ensure_ascii=False)

    print(f"{len(prodotti)} prodotti esportati con varianti strutturate.")