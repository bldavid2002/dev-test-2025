import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_allergen_pdf(filename="teszt_suti_allerginek.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=15,
        textColor=colors.HexColor('#2c3e50')
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#34495e')
    )


    story.append(Paragraph("Termék Specifikáció és Allergén Tájékoztató", title_style))
    story.append(Paragraph("<b>Termék neve:</b> Csokoládés Házi Süti (Triple Choco Brownie)", normal_style))
    story.append(Paragraph("<b>Gyártó:</b> Teszt Cukrászda Kft.", normal_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Összetevők:</b> Cukor, étcsokoládé (kakaómassza, cukor, kakaóvaj, emulgeálószer: lecitin [szója]), búzaliszt (glutén), vaj (tej), tojás, kakaópor, mogyoró darabok.", normal_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Tápérték adatok (100g termékben):</b>", normal_style))
    

    nutri_data = [
        ["Tápanyag", "Mennyiség"],
        ["Energy [kJ]", "1850 kJ"],
        ["Energy [kcal]", "442 kcal"],
        ["Fat [g]", "22.5 g"],
        ["Carbohydrate [g]", "52.0 g"],
        ["Sugar [g]", "38.0 g"],
        ["Protein [g]", "6.5 g"],
        ["Sodium [g]", "0.12 g"]
    ]
    
    t_nutri = Table(nutri_data, colWidths=[200, 200])
    t_nutri.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#bdc3c7')),
        ('TEXTCOLOR', (0,0), (1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ecf0f1')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8f9f9')),
    ]))
    story.append(t_nutri)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Allergén Információk:</b>", normal_style))
    

    allergen_data = [
        ["Allergén (KNOWN_ALLERGENS)", "Jelenlét (Tartalmazza / Nem tartalmazza)", "Megjegyzés"],
        ["Gluten", "Igen", "Búzalisztet tartalmaz"],
        ["Egg", "Igen", "Friss tojás felhasználásával"],
        ["Crustaceans", "Nem", "-"],
        ["Fish", "Nem", "-"],
        ["Peanut", "Nem", "Nyomokban tartalmazhat"],
        ["Soy", "Igen", "Lecitin (szója) származék"],
        ["Milk", "Igen", "Tej és vaj alapú"],
        ["Tree nuts", "Igen", "Mogyoró darabokat tartalmazhat"],
        ["Celery", "Nem", "-"],
        ["Mustard", "Nem", "-"]
    ]
    
    t_allergen = Table(allergen_data, colWidths=[120, 160, 160])
    t_allergen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (2,0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0,0), (2,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bdc3c7')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
    ]))
    story.append(t_allergen)


    doc.build(story)
    print(f"Sikeresen létrejött a PDF: {filename}")

if __name__ == "__main__":
    create_allergen_pdf()