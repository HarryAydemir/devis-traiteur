from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask import Flask, render_template, request, send_file, session, redirect, url_for, jsonify
import io
from datetime import datetime
import requests as req

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
GREEN = (0.1, 0.55, 0.1)

MOT_DE_PASSE = "2627"
FOOTER_TEXT  = "www.saladeandcake.com  —  contact@saladeandcake.com"

SUPABASE_URL = "https://kzkavskhplvaigtewmhr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt6a2F2c2tocGx2YWlndGV3bWhyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzczNTY2MDQsImV4cCI6MjA5MjkzMjYwNH0.bdS8CW77a98v-YfAB3Z5sdWwunfi7r9RwwHXsZdY38U"
SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

SOCIETE = {
    "nom":     "Salade And Cake",
    "forme":   "SAS KYD",
    "adresse": "19 Avenue de Villars",
    "ville":   "75007 Paris",
    "siret":   "84521905400010",
    "tva":     "FR59845219054",
    "rcs":     "RCS Paris"
}

TVA_HORS         = {"Cocktail Avec Alcool": 0.20}
TVA_DEFAULT_HORS = 0.10
TVA_PRODUITS     = 0.10
TVA_LIBRES       = 0.10
TVA_SUPP         = 0.20

# =========================
# SUPABASE HELPERS
# =========================
def supabase_insert(numero, client, adresse, date_prestation):
    try:
        data = {
            "numero": numero,
            "client": client,
            "adresse": adresse,
            "date_prestation": date_prestation,
            "statut": "en_attente"
        }
        r = req.post(f"{SUPABASE_URL}/rest/v1/prestations",
                     json=data, headers=SUPABASE_HEADERS)
        return r.status_code in [200, 201]
    except:
        return False

def supabase_get_all():
    try:
        r = req.get(f"{SUPABASE_URL}/rest/v1/prestations?select=*&order=date_prestation.asc",
                    headers=SUPABASE_HEADERS)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def supabase_update_statut(numero, statut):
    try:
        r = req.patch(
            f"{SUPABASE_URL}/rest/v1/prestations?numero=eq.{numero}",
            json={"statut": statut},
            headers={**SUPABASE_HEADERS, "Prefer": "return=representation"}
        )
        return r.status_code in [200, 204]
    except:
        return False

def supabase_get_one(numero):
    try:
        r = req.get(
            f"{SUPABASE_URL}/rest/v1/prestations?numero=eq.{numero}&select=*",
            headers=SUPABASE_HEADERS
        )
        data = r.json()
        return data[0] if data else None
    except:
        return None

# =========================
# NUMÉROTATION
# =========================
def get_numero_devis():
    return datetime.now().strftime("D-%Y%m%d-%H%M")

def get_numero_facture():
    return datetime.now().strftime("F-%Y%m%d-%H%M")

# =========================
# PRODUITS
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
    "Grande salade à composée",
    "Mezze",
    "Cocktail Avec Alcool",
    "Cocktail Sans Alcool",
    "Bonbonnière",
    "Percolateur"
]

# =========================
# TOTAL DEVIS
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
# PDF DEVIS (inchangé)
# =========================
def generate_pdf_buffer(nom, adresse, personnes, date_prestation, products, hors, supp, libres,
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

    try:
        c.drawImage(LOGO_PATH, 235, 690, width=130, height=130,
                    preserveAspectRatio=True, mask='auto')
    except:
        pass

    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(*GOLD)
    c.drawCentredString(300, 678, "DEVIS TRAITEUR")

    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*GRAY)
    date_str = datetime.now().strftime("%d/%m/%Y")
    c.drawCentredString(300, 664, f"N° {numero}  —  Émis le {date_str}")

    c.setFillColorRGB(*BLACK)
    c.setFont("Helvetica", 10)
    c.drawString(50, 648, f"Client : {nom}")
    c.drawString(50, 633, f"Adresse : {adresse}")
    c.drawString(50, 618, f"Personnes : {personnes}")
    if date_prestation:
        try:
            dp = datetime.strptime(date_prestation, "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            dp = date_prestation
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(*GOLD)
        c.drawString(50, 603, f"Date de prestation : {dp}")
        c.setFillColorRGB(*BLACK)
        c.setFont("Helvetica", 10)
        y = 580
    else:
        y = 595

    c.setFont("Helvetica-Bold", 10)
    c.drawString(COL_NOM,  y, "Produit")
    c.drawRightString(COL_QTE,  y, "Qté")
    c.drawRightString(COL_PU,   y, "PU (€)")
    c.drawRightString(COL_EURO, y, "Total (€)")
    y -= 15
    c.line(50, y, 550, y)
    y -= 15

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

    if libres:
        for (intitule, (q, pu)) in libres:
            y = check_y(y)
            c.drawString(COL_NOM, y, intitule[:50])
            c.drawRightString(COL_QTE,  y, str(q))
            c.drawRightString(COL_PU,   y, f"{pu:.2f}")
            c.drawRightString(COL_EURO, y, f"{q*pu:.2f}")
            y -= 12

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
    draw_footer()
    c.save()

# =========================
# PDF FACTURE
# =========================
def generate_facture_buffer(nom, adresse, personnes, date_prestation, info_client,
                             products, hors, supp, libres,
                             buffer, numero,
                             remise_pct, remise_euros,
                             statut, acompte_pct, acompte_euros):
    c = canvas.Canvas(buffer, pagesize=A4)
    page_width = A4[0]

    COL_NOM  = 50
    COL_QTE  = 300
    COL_PU   = 370
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

    try:
        c.drawImage(LOGO_PATH, 235, 690, width=130, height=130,
                    preserveAspectRatio=True, mask='auto')
    except:
        pass

    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(*GOLD)
    c.drawCentredString(300, 678, "FACTURE")

    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*GRAY)
    date_str = datetime.now().strftime("%d/%m/%Y")
    c.drawCentredString(300, 664, f"N° {numero}  —  {date_str}")

    c.setFillColorRGB(*BLACK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, 645, SOCIETE["nom"])
    c.setFont("Helvetica", 8)
    c.drawString(50, 633, SOCIETE["forme"])
    c.drawString(50, 621, SOCIETE["adresse"])
    c.drawString(50, 609, SOCIETE["ville"])
    c.drawString(50, 597, f"SIRET : {SOCIETE['siret']}")
    c.drawString(50, 585, f"N° TVA : {SOCIETE['tva']}  —  {SOCIETE['rcs']}")

    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(550, 645, "CLIENT")
    c.setFont("Helvetica", 9)
    c.drawRightString(550, 633, nom)
    c.drawRightString(550, 621, adresse)
    c.drawRightString(550, 609, f"{personnes} personnes")
    if date_prestation:
        try:
            dp = datetime.strptime(date_prestation, "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            dp = date_prestation
        c.setFont("Helvetica-Bold", 9)
        c.setFillColorRGB(*GOLD)
        c.drawRightString(550, 597, f"Prestation : {dp}")
        c.setFillColorRGB(*BLACK)
        c.setFont("Helvetica", 9)
    if info_client:
        for i, ligne in enumerate(info_client.split("\n")[:2]):
            c.drawRightString(550, 585 - i*12, ligne.strip())

    y = 560

    c.setFont("Helvetica-Bold", 10)
    c.drawString(COL_NOM,  y, "Désignation")
    c.drawRightString(COL_QTE,  y, "Qté")
    c.drawRightString(COL_PU,   y, "PU HT (€)")
    c.drawRightString(COL_EURO, y, "Total HT (€)")
    y -= 15
    c.line(50, y, 550, y)
    y -= 15

    total_ht_10 = 0
    total_ht_20 = 0

    c.setFont("Helvetica", 9)
    for p, (q, pr) in products.items():
        y = check_y(y)
        if pr == "OFFERT":
            c.drawString(COL_NOM, y, p[:45])
            c.drawRightString(COL_EURO, y, "OFFERT")
        else:
            pu_ht  = pr / (1 + TVA_PRODUITS)
            tot_ht = q * pu_ht
            total_ht_10 += tot_ht
            c.drawString(COL_NOM, y, p[:45])
            c.drawRightString(COL_QTE,  y, str(q))
            c.drawRightString(COL_PU,   y, f"{pu_ht:.2f}")
            c.drawRightString(COL_EURO, y, f"{tot_ht:.2f}")
        y -= 12

    if libres:
        for (intitule, (q, pu)) in libres:
            y = check_y(y)
            pu_ht  = pu / (1 + TVA_LIBRES)
            tot_ht = q * pu_ht
            total_ht_10 += tot_ht
            c.drawString(COL_NOM, y, intitule[:45])
            c.drawRightString(COL_QTE,  y, str(q))
            c.drawRightString(COL_PU,   y, f"{pu_ht:.2f}")
            c.drawRightString(COL_EURO, y, f"{tot_ht:.2f}")
            y -= 12

    if hors:
        y -= 10
        y = check_y(y, 30)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(COL_NOM, y, "Hors Mignardises")
        c.drawRightString(COL_QTE,  y, "Qté")
        c.drawRightString(COL_PU,   y, "PU HT (€)")
        c.drawRightString(COL_EURO, y, "Total HT (€)")
        y -= 12
        c.line(50, y, 550, y)
        y -= 12
        c.setFont("Helvetica", 9)
        for k, v in hors.items():
            y = check_y(y)
            tva_rate = TVA_HORS.get(k, TVA_DEFAULT_HORS)
            c.drawString(COL_NOM, y, k)
            if v[0] == "OFFERT":
                c.drawRightString(COL_EURO, y, "OFFERT")
            else:
                pu_ht  = v[1] / (1 + tva_rate)
                tot_ht = v[0] * pu_ht
                if tva_rate == 0.20:
                    total_ht_20 += tot_ht
                else:
                    total_ht_10 += tot_ht
                c.drawRightString(COL_QTE,  y, str(v[0]))
                c.drawRightString(COL_PU,   y, f"{pu_ht:.2f}")
                c.drawRightString(COL_EURO, y, f"{tot_ht:.2f}")
            y -= 12

    if supp:
        y -= 10
        y = check_y(y, 30)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(COL_NOM, y, "Suppléments")
        c.drawRightString(COL_EURO, y, "Prix HT (€)")
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
                v_ht = v / (1 + TVA_SUPP)
                total_ht_20 += v_ht
                c.drawRightString(COL_EURO, y, f"{v_ht:.2f}")
            y -= 12

    total_ht  = total_ht_10 + total_ht_20
    tva_10    = total_ht_10 * 0.10
    tva_20    = total_ht_20 * 0.20
    total_ttc = total_ht + tva_10 + tva_20

    has_remise = (remise_pct > 0) or (remise_euros > 0)
    if has_remise:
        if remise_pct > 0:
            montant_remise_ttc = total_ttc * remise_pct / 100
            libelle_remise = f"Remise ({remise_pct:.1f}%)"
        else:
            montant_remise_ttc = remise_euros
            libelle_remise = "Remise"
        ratio_remise    = montant_remise_ttc / total_ttc if total_ttc > 0 else 0
        remise_ht       = total_ht * ratio_remise
        total_ht_apres  = total_ht - remise_ht
        tva_10_apres    = tva_10 * (1 - ratio_remise)
        tva_20_apres    = tva_20 * (1 - ratio_remise)
        total_ttc_final = total_ttc - montant_remise_ttc
    else:
        total_ht_apres  = total_ht
        tva_10_apres    = tva_10
        tva_20_apres    = tva_20
        total_ttc_final = total_ttc

    y -= 15
    y = check_y(y, 160)
    c.line(50, y, 550, y)
    y -= 14

    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*BLACK)

    if has_remise:
        c.drawString(COL_NOM, y, "Total HT avant remise")
        c.drawRightString(COL_EURO, y, f"{total_ht:.2f} €")
        y -= 13
        c.setFillColorRGB(*RED)
        c.drawString(COL_NOM, y, libelle_remise)
        c.drawRightString(COL_EURO, y, f"- {remise_ht:.2f} €")
        y -= 13
        c.setFillColorRGB(*BLACK)
        c.drawString(COL_NOM, y, "Total HT après remise")
        c.drawRightString(COL_EURO, y, f"{total_ht_apres:.2f} €")
        y -= 13
    else:
        c.drawString(COL_NOM, y, "Total HT")
        c.drawRightString(COL_EURO, y, f"{total_ht:.2f} €")
        y -= 13

    if total_ht_10 > 0:
        c.drawString(COL_NOM, y, "TVA 10%")
        c.drawRightString(COL_EURO, y, f"{tva_10_apres:.2f} €")
        y -= 13
    if total_ht_20 > 0:
        c.drawString(COL_NOM, y, "TVA 20%")
        c.drawRightString(COL_EURO, y, f"{tva_20_apres:.2f} €")
        y -= 13

    c.line(350, y - 3, 550, y - 3)
    y -= 16
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(*GOLD)
    c.drawString(COL_NOM, y, "TOTAL TTC")
    c.drawRightString(COL_EURO, y, f"{total_ttc_final:.2f} €")
    y -= 22

    c.setFillColorRGB(*BLACK)
    y = check_y(y, 60)

    if statut == "paye":
        c.setFont("Helvetica-Bold", 13)
        c.setFillColorRGB(*GREEN)
        c.drawString(COL_NOM, y, "✓  PAYÉ")
        c.setFillColorRGB(*BLACK)
    elif statut == "a_payer":
        c.setFont("Helvetica-Bold", 13)
        c.setFillColorRGB(0.8, 0.2, 0.1)
        c.drawString(COL_NOM, y, "À PAYER")
        c.setFillColorRGB(*BLACK)
    elif statut == "acompte":
        if acompte_pct > 0:
            montant_acompte = total_ttc_final * acompte_pct / 100
            lib = f"Acompte versé ({acompte_pct:.0f}%) : {montant_acompte:.2f} €"
            reste = total_ttc_final - montant_acompte
        else:
            montant_acompte = acompte_euros
            lib = f"Acompte versé : {montant_acompte:.2f} €"
            reste = total_ttc_final - montant_acompte
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(*GOLD)
        c.drawString(COL_NOM, y, lib)
        y -= 14
        c.setFillColorRGB(0.8, 0.2, 0.1)
        c.drawString(COL_NOM, y, f"Reste à payer : {reste:.2f} €")
        c.setFillColorRGB(*BLACK)

    draw_footer()
    c.save()

# =========================
# FLASK APP
# =========================
app = Flask(__name__)
app.secret_key = "salade_and_cake_secret_2627"

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("connecte"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["GET", "POST"])
def login():
    erreur = ""
    if request.method == "POST":
        if request.form.get("mdp", "").strip() == MOT_DE_PASSE:
            session["connecte"] = True
            return redirect(url_for("index"))
        erreur = "Mot de passe incorrect."
    return render_template("login.html", erreur=erreur)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("form.html", products=PRODUCTS, hors=HORS)

@app.route("/facture")
@login_required
def facture_index():
    return render_template("facture.html", products=PRODUCTS, hors=HORS)

@app.route("/planning")
@login_required
def planning():
    prestations = supabase_get_all()
    return render_template("planning.html", prestations=prestations)

@app.route("/statut", methods=["GET", "POST"])
@login_required
def statut():
    message = ""
    prestation = None
    if request.method == "POST":
        numero = request.form.get("numero", "").strip()
        nouveau_statut = request.form.get("nouveau_statut", "").strip()
        if numero and nouveau_statut:
            ok = supabase_update_statut(numero, nouveau_statut)
            if ok:
                message = "success"
                prestation = supabase_get_one(numero)
            else:
                message = "error"
        elif numero:
            prestation = supabase_get_one(numero)
            if not prestation:
                message = "notfound"
    return render_template("statut.html", message=message, prestation=prestation)

@app.route("/generer", methods=["POST"])
@login_required
def generer():
    nom             = request.form.get("nom")
    adresse         = request.form.get("adresse")
    personnes       = int(request.form.get("personnes"))
    date_prestation = request.form.get("date_prestation", "").strip()
    remise_pct      = float(request.form.get("remise_pct",   "0") or "0")
    remise_euros    = float(request.form.get("remise_euros", "0") or "0")
    numero          = get_numero_devis()

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
            hors[item] = (int(qte_val), float(pu_val), int(qte_val)*float(pu_val))

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

    # Sauvegarde dans Supabase
    if date_prestation:
        supabase_insert(numero, nom, adresse, date_prestation)

    buffer = io.BytesIO()
    generate_pdf_buffer(nom, adresse, personnes, date_prestation, products, hors, supp, libres,
                        total, buffer, numero, remise_pct, remise_euros)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name=f"devis_{numero}_{nom}.pdf",
                     mimetype="application/pdf")

@app.route("/generer_facture", methods=["POST"])
@login_required
def generer_facture():
    nom             = request.form.get("nom")
    adresse         = request.form.get("adresse")
    personnes       = int(request.form.get("personnes"))
    date_prestation = request.form.get("date_prestation", "").strip()
    info_client     = request.form.get("info_client", "").strip()
    remise_pct      = float(request.form.get("remise_pct",   "0") or "0")
    remise_euros    = float(request.form.get("remise_euros", "0") or "0")
    statut_val      = request.form.get("statut", "a_payer")
    acompte_pct     = float(request.form.get("acompte_pct",  "0") or "0")
    acompte_euros   = float(request.form.get("acompte_euros","0") or "0")
    numero          = get_numero_facture()

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
            hors[item] = (int(qte_val), float(pu_val), int(qte_val)*float(pu_val))

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

    # Sauvegarde dans Supabase
    if date_prestation:
        supabase_insert(numero, nom, adresse, date_prestation)

    buffer = io.BytesIO()
    generate_facture_buffer(nom, adresse, personnes, date_prestation, info_client,
                            products, hors, supp, libres,
                            buffer, numero,
                            remise_pct, remise_euros,
                            statut_val, acompte_pct, acompte_euros)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name=f"facture_{numero}_{nom}.pdf",
                     mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)