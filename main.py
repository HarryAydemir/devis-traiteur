from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask import Flask, render_template, request, send_file, session, redirect, url_for
import io
from datetime import datetime

import os
for _ext in ["logo.png", "logo.PNG", "logo.jpg", "logo.JPG", "logo.jpeg"]:
    if os.path.exists(_ext):
        LOGO_PATH = _ext
        break
else:
    LOGO_PATH = "logo.png"

GOLD  = (0.85, 0.7, 0.2)
BLACK = (0, 0, 0)
GRAY  = (0.5, 0.5, 0.5)
RED   = (0.75, 0.15, 0.15)

MOT_DE_PASSE = "2627"
FOOTER_TEXT  = "www.saladeandcake.com  —  contact@saladeandcake.com"

# =========================
# NUMÉROTATION
# =========================
def get_numero():
    return datetime.now().strftime("D-%Y%m%d-%H%M")

# =========================
# PRODUITS COMPLETS
# =========================
PRODUCTS = {
    # SALÉ
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

    # CROUSTILLANT
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

    # VERRINES / SALADES
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

    # SUCRÉ
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

# =========================
# HORS MIGNARDISES
# =========================
HORS = [
    "Plateau de Charcuterie",
    "Plateau de Fromage",
    "Plateau de Charcuterie/Fromage",
    "Plateau de Légumes à croquer",
    "Plateau de Fruits",
    "Assiette de Fruits",
    "Grande salade à composée",
    "Mezze",
    "Cocktail Avec Alcool",
    "Cocktail Sans Alcool",
    "Bonbonnière",
    "Percolateur"
]

# =========================
# TOTAL
# =========================
def calc_total(products, hors, supp, libres):
    total = 0
    for _, (q, p) in products.items():
        if p != "OFFERT":
            total += q * p
    for v in hors.values():
        if v[0] != "OFFERT":
            total += v[2]
    for v in supp.values():
        if v != "OFFERT":
            total += v
    for _, (q, pu) in libres:
        total += q * pu
    return total

# =========================
# PDF
# =========================
def generate_pdf_buffer(nom, adresse, personnes, products, hors, supp, libres,
                        total, buffer, numero, remise_pct, remise_euros):
    c = canvas.Canvas(buffer, pagesize=A4)
    page_width = A4[0]

    COL_NOM  = 50
    COL_QTE  = 330
    COL_PU   = 390
    COL_EURO = 510
    Y_MIN    = 45

    def draw_footer():
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(*GRAY)
        c.drawCentredString(page_width / 2, 25, FOOTER_TEXT)
        c.setFillColorRGB(*BLACK)

    def nouvelle_page():
        draw_footer()
        c.showPage()
        c.setFillColorRGB(*BLACK)
        c.setFont("Helvetica", 9)
        return 780

    def check_y(y, espace=12):
        if y < Y_MIN + espace:
            return nouvelle_page()
        return y

    # ---- LOGO ----
    try:
        c.drawImage(LOGO_PATH, 235, 690, width=130, height=130,
                    preserveAspectRatio=True, mask='auto')
    except:
        pass

    # ---- TITRE ----
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(*GOLD)
    c.drawCentredString(300, 678, "DEVIS TRAITEUR")

    # ---- NUMÉRO + DATE ----
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*GRAY)
    date_str = datetime.now().strftime("%d/%m/%Y")
    c.drawCentredString(300, 664, f"N° {numero}  —  {date_str}")

    # ---- INFOS CLIENT ----
    c.setFillColorRGB(*BLACK)
    c.setFont("Helvetica", 10)
    c.drawString(50, 648, f"Client : {nom}")
    c.drawString(50, 633, f"Adresse : {adresse}")
    c.drawString(50, 618, f"Personnes : {personnes}")

    y = 595

    # ---- EN-TÊTES ----
    c.setFont("Helvetica-Bold", 10)
    c.drawString(COL_NOM,  y, "Produit")
    c.drawRightString(COL_QTE,  y, "Qté")
    c.drawRightString(COL_PU,   y, "PU (€)")
    c.drawRightString(COL_EURO, y, "Total (€)")
    y -= 15
    c.line(50, y, 550, y)
    y -= 15

    # ---- PRODUITS ----
    c.setFont("Helvetica", 9)
    for p, (q, pr) in products.items():
        y = check_y(y)
        if pr == "OFFERT":
            c.drawString(COL_NOM, y, p[:50])
            c.drawRightString(COL_EURO, y, "OFFERT")
        else:
            c.drawString(COL_NOM, y, p[:50])
            c.drawRightString(COL_QTE,  y, str(q))
            c.drawRightString(COL_PU,   y, f"{pr:.2f}")
            c.drawRightString(COL_EURO, y, f"{q*pr:.2f}")
        y -= 12

    # ---- PRODUITS LIBRES ----
    if libres:
        for (intitule, (q, pu)) in libres:
            y = check_y(y)
            c.drawString(COL_NOM, y, intitule[:50])
            c.drawRightString(COL_QTE,  y, str(q))
            c.drawRightString(COL_PU,   y, f"{pu:.2f}")
            c.drawRightString(COL_EURO, y, f"{q*pu:.2f}")
            y -= 12

    # ---- HORS MIGNARDISES ----
    if hors:
        y -= 10
        y = check_y(y, 30)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(COL_NOM, y, "Hors Mignardises")
        c.drawRightString(COL_QTE,  y, "Qté")
        c.drawRightString(COL_PU,   y, "PU (€)")
        c.drawRightString(COL_EURO, y, "Total (€)")
        y -= 12
        c.line(50, y, 550, y)
        y -= 12

        c.setFont("Helvetica", 9)
        for k, v in hors.items():
            y = check_y(y)
            c.drawString(COL_NOM, y, k)
            if v[0] == "OFFERT":
                c.drawRightString(COL_EURO, y, "OFFERT")
            else:
                c.drawRightString(COL_QTE,  y, str(v[0]))
                c.drawRightString(COL_PU,   y, f"{v[1]:.2f}")
                c.drawRightString(COL_EURO, y, f"{v[2]:.2f}")
            y -= 12

    # ---- SUPPLÉMENTS ----
    if supp:
        y -= 10
        y = check_y(y, 30)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(COL_NOM, y, "Suppléments")
        c.drawRightString(COL_EURO, y, "Prix (€)")
        y -= 12
        c.line(50, y, 550, y)
        y -= 12

        c.setFont("Helvetica", 9)
        for k, v in supp.items():
            y = check_y(y)
            c.drawString(COL_NOM, y, k)
            if v == "OFFERT":
                c.drawRightString(COL_EURO, y, "OFFERT")
            else:
                c.drawRightString(COL_EURO, y, f"{v:.2f}")
            y -= 12

    # ---- TOTAUX ----
    y -= 15
    y = check_y(y, 100)
    c.line(50, y, 550, y)
    y -= 18

    has_remise = (remise_pct > 0) or (remise_euros > 0)

    if has_remise:
        c.setFont("Helvetica", 11)
        c.setFillColorRGB(*BLACK)
        c.drawString(COL_NOM, y, "Total")
        c.drawRightString(COL_EURO, y, f"{total:.2f} €")
        y -= 16

        if remise_pct > 0:
            montant_remise = total * remise_pct / 100
            libelle_remise = f"Remise ({remise_pct:.1f}%)"
        else:
            montant_remise = remise_euros
            libelle_remise = "Remise"

        c.setFillColorRGB(*RED)
        c.drawString(COL_NOM, y, libelle_remise)
        c.drawRightString(COL_EURO, y, f"- {montant_remise:.2f} €")
        y -= 16

        total_final = total - montant_remise
        c.setFillColorRGB(*BLACK)
        c.line(350, y - 3, 550, y - 3)
        y -= 16

        c.setFont("Helvetica-Bold", 14)
        c.setFillColorRGB(*GOLD)
        c.drawString(COL_NOM, y, "TOTAL")
        c.drawRightString(COL_EURO, y, f"{total_final:.2f} €")
    else:
        c.line(350, y - 3, 550, y - 3)
        y -= 16
        c.setFont("Helvetica-Bold", 14)
        c.setFillColorRGB(*GOLD)
        c.drawString(COL_NOM, y, "TOTAL")
        c.drawRightString(COL_EURO, y, f"{total:.2f} €")

    c.setFillColorRGB(*BLACK)

    # ---- PIED DE PAGE DERNIÈRE PAGE ----
    draw_footer()

    c.save()

# =========================
# FLASK APP
# =========================
app = Flask(__name__)
app.secret_key = "salade_and_cake_secret_2627"

@app.route("/login", methods=["GET", "POST"])
def login():
    erreur = ""
    if request.method == "POST":
        mdp = request.form.get("mdp", "").strip()
        if mdp == MOT_DE_PASSE:
            session["connecte"] = True
            return redirect(url_for("index"))
        else:
            erreur = "Mot de passe incorrect."
    return render_template("login.html", erreur=erreur)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not session.get("connecte"):
        return redirect(url_for("login"))
    return render_template("form.html", products=PRODUCTS, hors=HORS)

@app.route("/generer", methods=["POST"])
def generer():
    if not session.get("connecte"):
        return redirect(url_for("login"))

    nom       = request.form.get("nom")
    adresse   = request.form.get("adresse")
    personnes = int(request.form.get("personnes"))

    remise_pct   = float(request.form.get("remise_pct",   "0") or "0")
    remise_euros = float(request.form.get("remise_euros", "0") or "0")

    numero = get_numero()

    products = {}
    for name, price in PRODUCTS.items():
        val = request.form.get(f"prod_{name}", "0").strip()
        if val.lower() == "offert":
            products[name] = (0, "OFFERT")
        elif val != "0" and val != "":
            products[name] = (int(val), price)

    hors = {}
    for item in HORS:
        qte_val = request.form.get(f"hors_qte_{item}", "0").strip()
        pu_val  = request.form.get(f"hors_pu_{item}", "0").strip()
        if pu_val.lower() == "offert":
            hors[item] = ("OFFERT", 0, 0)
        elif qte_val not in ("0", "") and pu_val not in ("0", ""):
            qte = int(qte_val)
            pu  = float(pu_val)
            hors[item] = (qte, pu, qte * pu)

    supp = {}
    for item in ["Livraison", "Installation", "Service"]:
        val = request.form.get(f"supp_{item}", "0").strip()
        if val.lower() == "offert":
            supp[item] = "OFFERT"
        elif val != "0" and val != "":
            supp[item] = float(val)

    libres = []
    i = 1
    while True:
        intitule = request.form.get(f"libre_nom_{i}", "").strip()
        qte_val  = request.form.get(f"libre_qte_{i}", "0").strip()
        pu_val   = request.form.get(f"libre_pu_{i}", "0").strip()
        if not intitule:
            break
        if qte_val not in ("0", "") and pu_val not in ("0", ""):
            libres.append((intitule, (int(qte_val), float(pu_val))))
        i += 1

    total = calc_total(products, hors, supp, libres)

    buffer = io.BytesIO()
    generate_pdf_buffer(nom, adresse, personnes, products, hors, supp, libres,
                        total, buffer, numero, remise_pct, remise_euros)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"devis_{numero}_{nom}.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)