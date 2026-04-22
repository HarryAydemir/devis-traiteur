from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask import Flask, render_template, request, send_file
import io
import json
import os
from datetime import datetime

LOGO_PATH = "logo.png"
COUNTER_FILE = "counters.json"

GOLD = (0.85, 0.7, 0.2)
BLACK = (0, 0, 0)
GRAY = (0.5, 0.5, 0.5)

# =========================
# INFOS SOCIÉTÉ
# =========================
SOCIETE = {
    "nom": "Salade And Cake",
    "forme": "SAS KYD",
    "adresse": "19 Avenue de Villars",
    "ville": "75007 Paris",
    "siret": "84521905400010",
    "tva": "FR59845219054",
    "rcs": "RCS Paris"
}

# =========================
# NUMÉROTATION
# =========================
def get_next_numero(type_doc):
    annee = datetime.now().year
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            counters = json.load(f)
    else:
        counters = {}

    key = f"{type_doc}_{annee}"
    counters[key] = counters.get(key, 0) + 1

    with open(COUNTER_FILE, "w") as f:
        json.dump(counters, f)

    prefix = "D" if type_doc == "devis" else "F"
    return f"{prefix}-{annee}-{counters[key]:03d}"

# =========================
# PRODUITS COMPLETS
# =========================
PRODUCTS = {
    "Mini Burger": 2.50,
    "Mini Hot Dog": 1.60,
    "Mini Kebab, Pain Pita": 2.50,
    "Mini Ciabatta Mozza, Tomate seché, Pesto": 2.50,
    "Mini Ciabatta Mozza, Tartare de Tomate, Serrano": 2.50,
    "Burritos de kefta": 2.50,
    "Club Suédois Saumon Fumé": 1.20,
    "Club Suédois Legumes Marinés": 1.20,
    "Club Suédois Rillete Poulet Rôti": 1.20,
    "Navette Saumon Fumé": 1.40,
    "Navette Thon": 1.40,
    "Navette Legumes Marinés": 1.40,
    "Navette Jambon": 1.40,
    "Club au Thon": 1.00,
    "Egg Muffin": 3.00,
    "Mini Croque Monsieur": 0.80,
    "Mini Croque Monsieur Suppl. Truffe": 1.80,
    "Mini Croque Monsieur Végétarien": 1.00,
    "Mini Croque Monsieur Végétarien Suppl. Truffe": 2.00,
    "Club Sandwich": 1.00,
    "Mini Wrap Poulet": 1.20,
    "Mini Wrap Jambon": 1.20,
    "Mini Wrap Saumon": 1.20,
    "Toast Avocado": 2.50,
    "Mini Cake Salé": 1.80,
    "Feuilleté Saucisse": 0.50,
    "Larmajoun": 3.00,
    "Mini Bruschetta": 1.00,
    "Bruschetta": 2.50,
    "Mini Foccacia": 1.50,
    "Brochette Tomate Mozzarella": 1.50,
    "Brochette Melon Serrano": 1.50,
    "Champignon à l'ail et fines herbes": 0.80,
    "Mini Quiche": 2.00,
    "Canape Blini": 1.00,
    "Ketlata": 1.60,
    "Nems Poulet": 1.20,
    "Nems Legumes": 1.20,
    "Nems Porc": 1.20,
    "Nems Crevette": 1.20,
    "Tempura Crevette": 1.60,
    "Berégué": 1.20,
    "Samoussa Boeuf": 1.20,
    "Samoussa Legumes": 1.20,
    "Samoussa Poulet Curry": 1.20,
    "Falafel": 1.00,
    "Tenders de Poulet": 2.00,
    "Verrine Poulet Tartare de tomate": 1.50,
    "Verrine Legumes Croquant": 1.20,
    "Verrine Legumes Marinés": 1.50,
    "Verrine Saumon Tzatziki": 1.50,
    "Verrine Serrano Ail & Fines Herbes": 1.50,
    "Verrine Crevette Cocktail": 1.50,
    "Verrine Coleslaw": 1.20,
    "Mini Salade": 2.00,
    "Coupelle Tomate ancienne Burrata Pesto": 2.00,
    "Roulé d'Aubergine Parmesan": 1.00,
    "Roulé de Courgette Parmesan": 1.00,
    "Tiramisu": 1.20,
    "Mousse Au Chocolat": 1.50,
    "Mini Donuts": 1.00,
    "Fromate Blanc Granola": 1.20,
    "Panacotta": 1.20,
    "Mousse de Mascarpone Pistache/Fraise": 1.20,
    "Mousse de Mascarpone Speculos/Pêche": 1.20,
    "Verrine façon Tarte au Citron": 1.50,
    "Brownie Crème Anglaise": 1.20,
    "Pancake/Gaufre": 1.00,
    "Salade de fruits": 1.20,
    "Mini Cookie": 1.00,
    "Muffin": 2.00,
    "Macaron": 2.00,
    "Mini Brochette de Fruit": 1.50,
    "Mini Tarte Tatin": 1.50,
    "Mini Patisserie": 1.50,
    "Mini Fondant au Chocolat": 2.00
}

HORS = [
    "Plateau de Charcuterie",
    "Plateau de Fromage",
    "Plateau de Charcuterie/Fromage",
    "Plateau de Légumes à croquer",
    "Plateau de Fruits",
    "Assiette de Fruits",
    "Grande salade composée",
    "Mezze",
    "Cocktail Avec Alcool",
    "Cocktail Sans Alcool",
    "Bonbonnière",
    "Percolateur",
]

ANIMATIONS = [
    "Plancha",
    "Bar à Burrata",
    "Gaufrier",
    "Table de Cocktail",
    "Bar à cône sucré",
    "Bar à cône salé",
]

# =========================
# TOTAL TTC
# =========================
def calc_total(products, hors, animations, supp):
    total = 0
    for _, (q, p) in products.items():
        if p != "OFFERT":
            total += q * p
    for v in hors.values():
        if v[0] != "OFFERT":
            total += v[2]
    for v in animations.values():
        if v[0] != "OFFERT":
            total += v[2]
    for v in supp.values():
        if v != "OFFERT":
            total += v
    return total

# =========================
# PDF
# =========================
def generate_pdf_buffer(nom, adresse_client, personnes, products, hors, animations,
                         supp, total, buffer, type_doc, numero,
                         afficher_societe, remise, paiement, acompte_pct, tva_pct):

    c = canvas.Canvas(buffer, pagesize=A4)

    COL_NOM  = 50
    COL_QTE  = 310
    COL_PU   = 390
    COL_EURO = 510
    Y_MIN    = 60

    def nouvelle_page():
        c.showPage()
        c.setFillColorRGB(*BLACK)
        c.setFont("Helvetica", 9)
        return 780

    def check_y(y, espace=12):
        if y < Y_MIN + espace:
            return nouvelle_page()
        return y

    try:
        c.drawImage(LOGO_PATH, 230, 720, width=130, height=130,
                    preserveAspectRatio=True, mask='auto')
    except:
        pass

    titre = "FACTURE" if type_doc == "facture" else "DEVIS"
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(*GOLD)
    c.drawCentredString(300, 700, titre)

    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*GRAY)
    date_str = datetime.now().strftime("%d/%m/%Y")
    c.drawCentredString(300, 685, f"N° {numero}  —  {date_str}")

    y = 585

    # HEADERS TTC
    c.setFont("Helvetica-Bold", 10)
    c.drawString(COL_NOM,  y, "Désignation")
    c.drawString(COL_QTE,  y, "Qté")
    c.drawRightString(COL_PU,   y, "PU TTC (€)")
    c.drawRightString(COL_EURO, y, "Total TTC (€)")

    y -= 40
    total_ttc = total

    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(*GOLD)
    c.drawString(COL_NOM, y, "TOTAL TTC")
    c.drawRightString(COL_EURO, y, f"{total_ttc:.2f} €")

    c.save()

# =========================
# FLASK
# =========================
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("form.html", products=PRODUCTS, hors=HORS, animations=ANIMATIONS)

@app.route("/generer", methods=["POST"])
def generer():
    nom = request.form.get("nom")
    adresse_client = request.form.get("adresse")
    personnes = int(request.form.get("personnes"))
    type_doc = request.form.get("type_doc", "devis")

    numero = get_next_numero(type_doc)

    products = {}
    for name, price in PRODUCTS.items():
        val = request.form.get(f"prod_{name}", "0").strip()
        if val and val != "0":
            products[name] = (int(val), price)

    total = calc_total(products, {}, {}, {})

    buffer = io.BytesIO()
    generate_pdf_buffer(
        nom, adresse_client, personnes,
        products, {}, {}, {},
        total, buffer, type_doc, numero,
        True, 0, "aucun", 0, 0
    )

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"devis_{numero}.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)