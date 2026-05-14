from flask import Flask, render_template, request, send_file

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

            # =========================
            # INPUT
            # =========================
            no_invoice = request.form["invoice"]
            tanggal = request.form["tanggal"]
            kota = request.form["kota"]
            terbilang = request.form["terbilang"]

            # INPUT BULAN & TAHUN
            bulan = request.form["bulan"]
            tahun = request.form["tahun"]

            qty = clean_number(request.form["qty"])
            pokok = clean_number(request.form["pokok"])
            dpp = clean_number(request.form["dpp"])
            ppn = clean_number(request.form["ppn"])

            # TOTAL
            total = pokok + ppn

            # =========================
            # NAMA FILE PDF
            # =========================
            safe_invoice = no_invoice.replace("/", "-")
            filename = f"{safe_invoice}.pdf"

            # =========================
            # DOCUMENT PDF
            # =========================
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                leftMargin=40,
                rightMargin=40,
                topMargin=30,
                bottomMargin=30
            )

            styles = getSampleStyleSheet()

            # =========================
            # STYLE
            # =========================
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

            # =========================
            # HEADER
            # =========================
            elements.append(Paragraph("PT. HAFSA UTAMA GAS", center_bold))
            elements.append(Paragraph("AGEN LPG PSO", center_normal))

            elements.append(
                Paragraph(
                    "Jl. Jend. Sudirman No.99 Wonomulyo Polewali Mandar",
                    center_normal
                )
            )

            elements.append(
                Paragraph(
                    "Polewali Mandar",
                    center_normal
                )
            )

            elements.append(Spacer(1, 6))

            # GARIS
            line = Table(
                [[""]],
                colWidths=[515]
            )

            line.setStyle(TableStyle([
                ('LINEABOVE', (0,0), (-1,-1), 1.5, colors.black)
            ]))

            elements.append(line)

            # =========================
            # TITLE
            # =========================
            elements.append(
                Paragraph(
                    "INVOICE",
                    invoice_title
                )
            )

            elements.append(Spacer(1, 10))

            # =========================
            # CUSTOMER
            # =========================
            customer_data = [

                ["Kepada", ": PT. PERTAMINA PATRA NIAGA", ""],

                ["Alamat", ": Gedung Wisma Tugu II Lt.2", ""],

                ["", ": Jl. HR Rasuna Said Kav C7-9 Setiabudi", ""],

                ["", ": Jakarta 12920 Indonesia", ""],

                [
                    "Tanggal",
                    f": {tanggal}",
                    Paragraph(
                        f"No. Invoice:<br/>{no_invoice}",
                        styles['Normal']
                    )
                ],
            ]

            customer_table = Table(
                customer_data,
                colWidths=[70, 280, 165]
            )

            customer_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (2,4), (2,4), 'RIGHT'),
                ('LEFTPADDING', (2,4), (2,4), 0),
            ]))

            elements.append(customer_table)

            elements.append(Spacer(1, 10))

            # =========================
            # NILAI TABLE
            # =========================
            nilai_data = [

                ["Pokok", format_rp(pokok)],

                ["Nilai DPP", format_rp(dpp)],

                ["PPN 12%", format_rp(ppn)],

                ["Total", format_rp(total)],
            ]

            nilai_table = Table(
                nilai_data,
                colWidths=[75, 110],
                rowHeights=[20, 20, 20, 22]
            )

            nilai_table.setStyle(TableStyle([

                # BORDER
                ('GRID', (0,0), (-1,-1), 0.7, colors.black),

                # ALIGN
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),

                # TOTAL BOLD
                ('FONTNAME', (0,3), (-1,3), 'Helvetica-Bold'),

                # PADDING
                ('LEFTPADDING', (0,0), (-1,-1), 4),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),

                # VERTICAL
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),

            ]))

            # WRAPPER
            nilai_wrapper = KeepInFrame(
                185,
                95,
                [nilai_table],
                hAlign='RIGHT'
            )

            # =========================
            # TABLE UTAMA
            # =========================
            data = [

                ["No", "Keterangan", "Quantity/Kg", "Nilai"],

                [
                    "1",
                    f"Transport Fee LPG 3 Kg ({bulan} {tahun})",
                    f"{qty:,}".replace(",", "."),
                    nilai_wrapper
                ]
            ]

            table = Table(
                data,
                colWidths=[40, 200, 90, 185]
            )

            table.setStyle(TableStyle([

                # BORDER
                ('GRID', (0,0), (-1,-1), 1, colors.black),

                # HEADER
                ('BACKGROUND', (0,0), (-1,0), colors.grey),

                ('TEXTCOLOR', (0,0), (-1,0), colors.white),

                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

                # ALIGN
                ('ALIGN', (2,1), (2,-1), 'RIGHT'),

                ('ALIGN', (3,1), (3,1), 'RIGHT'),

                # VERTICAL
                ('VALIGN', (0,0), (-1,-1), 'TOP'),

                # PADDING
                ('RIGHTPADDING', (3,1), (3,1), 6),

                ('LEFTPADDING', (3,1), (3,1), 2),

            ]))

            elements.append(table)

            elements.append(Spacer(1, 10))

            # =========================
            # TERBILANG
            # =========================
            elements.append(
                Paragraph(
                    f"Terbilang: {terbilang}",
                    styles['Normal']
                )
            )

            elements.append(Spacer(1, 15))

            # =========================
            # BANK
            # =========================
            elements.append(
                Paragraph(
                    "Bank: BRI Cabang Parepare",
                    styles['Normal']
                )
            )

            elements.append(
                Paragraph(
                    "No Rek: 0064-01-036105-50-1",
                    styles['Normal']
                )
            )

            elements.append(Spacer(1, 35))

            # =========================
            # TANDA TANGAN
            # =========================
            elements.append(
                Paragraph(
                    f"{kota}, {tanggal}",
                    right_normal
                )
            )

            elements.append(Spacer(1, 10))

            # IMAGE TANDA TANGAN
            ttd = Image(
                "signature.png",
                width=170,
                height=70
            )

            # POSISI KE KANAN
            ttd_table = Table(
                [["", ttd]],
                colWidths=[320, 170]
            )

            ttd_table.setStyle(TableStyle([
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ]))

            elements.append(ttd_table)

            # =========================
            # BUILD PDF
            # =========================
            doc.build(elements)

            return send_file(
                filename,
                as_attachment=True
            )

        except Exception as e:
            return f"Error: {e}"

    return render_template("index.html")

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)
