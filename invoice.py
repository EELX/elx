import tkinter as tk
from tkinter import messagebox
from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

# =========================
# FORMAT RUPIAH
# =========================
def format_rp(angka):
    return "Rp {:,}".format(int(angka)).replace(",", ".")

# =========================
# BERSIHKAN INPUT ANGKA
# =========================
def clean_number(value):
    return int(value.replace(".", "").replace(",", "").strip())

# =========================
# GENERATE PDF
# =========================
def generate_pdf():
    try:
        # Ambil input
        no_invoice = entry_invoice.get()
        tanggal = entry_tanggal.get()
        kota = entry_kota.get()

        qty = clean_number(entry_qty.get())
        pokok = clean_number(entry_pokok.get())
        dpp = clean_number(entry_dpp.get())
        ppn = clean_number(entry_ppn.get())
        total = pokok + ppn

        # =========================
        # DOCUMENT
        # =========================
        doc = SimpleDocTemplate(
            "invoice.pdf",
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=30,
            bottomMargin=30
        )

        PAGE_WIDTH = 515
        styles = getSampleStyleSheet()

        center = ParagraphStyle(name="center", alignment=TA_CENTER)
        right = ParagraphStyle(name="right", alignment=TA_RIGHT)

        elements = []

        # =========================
        # HEADER
        # =========================
        elements.append(Paragraph("<b>PT. HAFSA UTAMA GAS</b>", center))
        elements.append(Paragraph("AGEN LPG PSO", center))
        elements.append(Paragraph("Jl. Jend. Sudirman No.99 Wonomulyo Polewali Mandar", center))
        elements.append(Paragraph("Polewali Mandar", center))

        elements.append(Spacer(1, 6))

        line = Table([[""]], colWidths=[PAGE_WIDTH])
        line.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,-1), 1.2, colors.black)
        ]))
        elements.append(line)

        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>INVOICE</b>", center))
        elements.append(Spacer(1, 12))

        # =========================
        # INFO
        # =========================
        elements.append(Paragraph(f"No Invoice: {no_invoice}", styles['Normal']))
        elements.append(Paragraph(f"Tanggal: {tanggal}", styles['Normal']))
        elements.append(Spacer(1, 10))

        # =========================
        # NESTED TABLE
        # =========================
        nilai_data = [
            ["Pokok", format_rp(pokok)],
            ["Nilai DPP", format_rp(dpp)],
            ["PPN 12%", format_rp(ppn)],
            ["Total", format_rp(total)],
        ]

        nilai_table = Table(nilai_data, colWidths=[75, 100])
        nilai_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ]))

        nilai_wrapper = KeepInFrame(180, 100, [nilai_table])

        # =========================
        # TABLE UTAMA
        # =========================
        data = [
            ["No", "Keterangan", "Quantity/Kg", "Nilai"],
            [
                "1",
                "Tagihan Transport Fee LPG 3 Kg Periode",
                f"{qty:,}".replace(",", "."),
                nilai_wrapper
            ]
        ]

        table = Table(data, colWidths=[30, 220, 80, 185])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.darkgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (2,1), (2,1), 'RIGHT'),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))

        # =========================
        # TERBILANG (INPUT USER)
        # =========================
        elements.append(Paragraph(
            f"<b>Terbilang:</b> {entry_terbilang.get()}",
            styles['Normal']
        ))

        elements.append(Spacer(1, 20))

        # =========================
        # FOOTER
        # =========================
        elements.append(Paragraph("Bank: BRI Cabang Parepare", styles['Normal']))
        elements.append(Paragraph("No Rek: 0064-01-036105-50-1", styles['Normal']))

        elements.append(Spacer(1, 50))

        elements.append(Paragraph(f"{kota}, {tanggal}", right))
        elements.append(Spacer(1, 60))
        elements.append(Paragraph("(............................)", right))
        elements.append(Paragraph("Owner", right))

        doc.build(elements)

        messagebox.showinfo("Sukses", "Invoice berhasil dibuat!")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# =========================
# GUI
# =========================
root = tk.Tk()
root.title("Invoice Generator")

labels = [
    "No Invoice", "Tanggal", "Kota",
    "Quantity", "Pokok", "DPP", "PPN", "Terbilang"
]

entries = []

for i, text in enumerate(labels):
    tk.Label(root, text=text).grid(row=i, column=0, sticky="w")
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1)
    entries.append(entry)

entry_invoice, entry_tanggal, entry_kota, entry_qty, entry_pokok, entry_dpp, entry_ppn, entry_terbilang = entries

tk.Button(root, text="Generate PDF", command=generate_pdf).grid(row=len(labels), column=0, columnspan=2, pady=10)

root.mainloop()
