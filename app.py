from flask import Flask, render_template, request, send_file
import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepInFrame,
    Image
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

app = Flask(__name__)

# =========================
# FORMAT RUPIAH
# =========================
def format_rp(angka):
    return "Rp {:,}".format(int(angka)).replace(",", ".")

def clean_number(value):
    if not value:
        return 0
    return int(value.replace(".", "").replace(",", "").strip())

# =========================
# ROUTE
# =========================
@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        try:
            no_invoice = request.form["invoice"]
            tanggal = request.form["tanggal"]
            kota = request.form["kota"]
            terbilang = request.form["terbilang"]

            bulan = request.form["bulan"]
            tahun = request.form["tahun"]

            qty = clean_number(request.form["qty"])
            pokok = clean_number(request.form["pokok"])
            dpp = clean_number(request.form["dpp"])
            ppn = clean_number(request.form["ppn"])

            total = pokok + ppn

            safe_invoice = no_invoice.replace("/", "-")
            filename = f"/tmp/{safe_invoice}.pdf"  # 🔥 penting untuk server

            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                leftMargin=40,
                rightMargin=40,
                topMargin=30,
                bottomMargin=30
            )

            styles = getSampleStyleSheet()

            center_bold = ParagraphStyle(
                name="CenterBold",
                parent=styles['Normal'],
                alignment=TA_CENTER,
                fontSize=12,
                fontName="Helvetica-Bold"
            )

            center_normal = ParagraphStyle(
                name="CenterNormal",
                parent=styles['Normal'],
                alignment=TA_CENTER,
                fontSize=10
            )

            right_normal = ParagraphStyle(
                name="RightNormal",
                parent=styles['Normal'],
                alignment=TA_RIGHT,
                fontSize=10
            )

            invoice_title = ParagraphStyle(
                name="InvoiceTitle",
                parent=styles['Normal'],
                alignment=TA_CENTER,
                fontSize=11,
                fontName="Helvetica-Bold",
                spaceBefore=4,
                spaceAfter=6
            )

            elements = []

            # HEADER
            elements.append(Paragraph("PT. HAFSA UTAMA GAS", center_bold))
            elements.append(Paragraph("AGEN LPG PSO", center_normal))
            elements.append(Paragraph("Jl. Jend. Sudirman No.99 Wonomulyo Polewali Mandar", center_normal))
            elements.append(Paragraph("Polewali Mandar", center_normal))
            elements.append(Spacer(1, 6))

            line = Table([[""]], colWidths=[515])
            line.setStyle(TableStyle([
                ('LINEABOVE', (0,0), (-1,-1), 1.5, colors.black)
            ]))
            elements.append(line)

            elements.append(Paragraph("INVOICE", invoice_title))
            elements.append(Spacer(1, 10))

            # CUSTOMER
            customer_data = [
                ["Kepada", ": PT. PERTAMINA PATRA NIAGA", ""],
                ["Alamat", ": Gedung Wisma Tugu II Lt.2", ""],
                ["", ": Jl. HR Rasuna Said Kav C7-9 Setiabudi", ""],
                ["", ": Jakarta 12920 Indonesia", ""],
                ["Tanggal", f": {tanggal}", Paragraph(f"No. Invoice:<br/>{no_invoice}", styles['Normal'])]
            ]

            customer_table = Table(customer_data, colWidths=[70, 280, 165])
            customer_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (2,4), (2,4), 'RIGHT'),
            ]))
            elements.append(customer_table)

            elements.append(Spacer(1, 10))

            # NILAI
            nilai_data = [
                ["Pokok", format_rp(pokok)],
                ["Nilai DPP", format_rp(dpp)],
                ["PPN 12%", format_rp(ppn)],
                ["Total", format_rp(total)],
            ]

            nilai_table = Table(nilai_data, colWidths=[75, 110])
            nilai_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.7, colors.black),
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                ('FONTNAME', (0,3), (-1,3), 'Helvetica-Bold'),
            ]))

            nilai_wrapper = KeepInFrame(185, 95, [nilai_table], hAlign='RIGHT')

            data = [
                ["No", "Keterangan", "Quantity/Kg", "Nilai"],
                ["1", f"Transport Fee LPG 3 Kg ({bulan} {tahun})", f"{qty:,}".replace(",", "."), nilai_wrapper]
            ]

            table = Table(data, colWidths=[40, 200, 90, 185])
            table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 10))

            elements.append(Paragraph(f"Terbilang: {terbilang}", styles['Normal']))
            elements.append(Spacer(1, 15))

            elements.append(Paragraph("Bank: BRI Cabang Parepare", styles['Normal']))
            elements.append(Paragraph("No Rek: 0064-01-036105-50-1", styles['Normal']))
            elements.append(Spacer(1, 35))

            elements.append(Paragraph(f"{kota}, {tanggal}", right_normal))
            elements.append(Spacer(1, 10))

            # SIGNATURE
            ttd = Image("signature.png", width=170, height=70)
            ttd_table = Table([["", ttd]], colWidths=[320, 170])
            elements.append(ttd_table)

            doc.build(elements)

            return send_file(filename, as_attachment=True)

        except Exception as e:
            return f"Error: {e}"

    return render_template("index.html")

# =========================
# RUN (FIX UNTUK HOSTING)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)