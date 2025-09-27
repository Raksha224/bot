import os
from datetime import datetime

KB_DIR = os.path.join(os.getcwd(), 'kb')
os.makedirs(KB_DIR, exist_ok=True)

CONTENT = (
    "PowerPro Electrical - Knowledge Pack\n"
    "Updated: " + datetime.now().strftime('%Y-%m-%d %H:%M') + "\n\n"
    "Company Basics\n"
    "- Phone: (555) 123-4567\n"
    "- Hours: Mon–Sat 8:00–18:00, Emergency 24/7\n"
    "- Service Area: Downtown, Northside, Eastview\n"
    "- Licenses & Insurance: Up-to-date; permits handled for panel work\n\n"
    "Services\n"
    "- Repairs: outlets, switches, lighting, breakers, diagnostics\n"
    "- Installations: lighting, outlets/switches, smart switches, dedicated circuits\n"
    "- Panel Work: upgrades 100A→200A, breaker replacement\n"
    "- Safety: GFCI/AFCI install, inspections, code corrections\n"
    "- Emergency: 24/7 electrical only (not HVAC/plumbing)\n\n"
    "FAQs\n"
    "- Do you install GFCI? Yes — kitchen, bath, outdoor; typical 45–90 min.\n"
    "- Do you upgrade panels? Yes — permits included; typical 1 day.\n"
    "- Do you serve my area? Downtown, Northside, Eastview; emergency 60–90 min.\n\n"
    "Troubleshooting & Safety\n"
    "1) Check breaker for trips and reset once.\n"
    "2) Test GFCI Reset/Test in kitchen/bath/outdoor.\n"
    "3) Flicker: tighten bulb, check fixture.\n"
    "4) Burning smell/sparks: turn off main breaker; call emergency line.\n\n"
    "Booking Script\n"
    "- Name, phone, address\n"
    "- Issue or installation details\n"
    "- Preferred date/time; access notes\n"
    "- Confirm and set expectations (on-site estimate, no hidden fees)\n\n"
    "Policies\n"
    "- Cancellation: free ≥24h; late cancellation fee may apply\n"
    "- Payment: card/cash; invoice on completion; permit fees disclosed\n"
)

# Write TXT for ingestion
txt_path = os.path.join(KB_DIR, 'knowledge_pack.txt')
with open(txt_path, 'w', encoding='utf-8') as f:
    f.write(CONTENT)

# Write PDF for sharing
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    pdf_path = os.path.join(KB_DIR, 'knowledge_pack.pdf')
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    x, y = 1*inch, height - 1*inch
    for line in CONTENT.split('\n'):
        if y < 1*inch:
            c.showPage()
            y = height - 1*inch
        c.drawString(x, y, line[:110])
        y -= 14
    c.save()
    print(f"Created: {pdf_path}")
except Exception as e:
    print(f"PDF generation skipped: {e}")

print(f"Created: {txt_path}")


