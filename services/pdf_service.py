from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from models.customer import CustomerModel
from utils.helpers import format_currency

class PDFService:
    @staticmethod
    def generate_invoice(sale_id: int, customer_id, cart_items, total_amount, output_path: str):
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Header
        elements.append(Paragraph("<b>Computer Shop Management System</b>", styles['Title']))
        elements.append(Paragraph("<b>INVOICE</b>", styles['Heading2']))
        elements.append(Paragraph(f"<b>Invoice #:</b> {sale_id}", styles['Normal']))
        elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        
        if customer_id:
            customer = CustomerModel.get_customer_by_id(customer_id)
            if customer:
                elements.append(Paragraph(f"<b>Customer:</b> {customer['name']}", styles['Normal']))
                elements.append(Paragraph(f"<b>Phone:</b> {customer['phone']}", styles['Normal']))
        else:
            elements.append(Paragraph("<b>Customer:</b> Guest", styles['Normal']))
            
        elements.append(Spacer(1, 20))

        # Table Data
        data = [["Item", "Price", "Qty", "Subtotal"]]
        for item in cart_items:
            subtotal = item['selling_price'] * item['quantity']
            data.append([
                item['name'],
                format_currency(item['selling_price']),
                str(item['quantity']),
                format_currency(subtotal)
            ])
            
        data.append(["", "", "Total:", format_currency(total_amount)])

        t = Table(data, colWidths=[250, 100, 50, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (2,-1), (-1,-1), 'Helvetica-Bold')
        ]))
        
        elements.append(t)
        
        # Footer
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("Thank you for your business!", styles['Normal']))

        doc.build(elements)
