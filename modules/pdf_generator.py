# frontend/modules/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from tkinter import messagebox
import os
import datetime
import platform
from fpdf import FPDF

def generate_report_pdf(title, headers, data):
    """Genera un reporte general a partir de los datos de un Treeview."""
    
    # 1. Preparar el entorno
    folder = os.path.join(os.getcwd(), 'Reportes_Generados')
    os.makedirs(folder, exist_ok=True)
    
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    filename = f"{title.replace(' ', '_')}_{today_str}.pdf"
    filepath = os.path.join(folder, filename)

    try:
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Título
        pdf.cell(0, 10, title, 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 5, f"Fecha de generación: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'R')
        pdf.ln(5)

        # 2. Configurar la tabla
        pdf.set_fill_color(200, 220, 255)
        pdf.set_font('Arial', 'B', 10)
        
        col_width = (pdf.w - 2 * pdf.l_margin) / len(headers)
        row_height = 7
        
        # Escribir encabezados
        for header in headers:
            pdf.cell(col_width, row_height, header, 1, 0, 'C', 1)
        pdf.ln()

        # 3. Escribir datos
        pdf.set_font('Arial', '', 9)
        fill = False
        
        for row in data:
            fill = not fill
            pdf.set_fill_color(240, 240, 240)
            
            for i, item in enumerate(row):
                align = 'R' if (i == len(row) - 1 and ('Q' in str(item) or str(item).isdigit())) else 'L'
                pdf.cell(col_width, row_height, str(item), 1, 0, align, fill)
            pdf.ln()

        # 4. Guardar y notificar
        pdf.output(filepath, 'F')
        messagebox.showinfo("Reporte Generado", f"El reporte '{title}' se ha guardado correctamente.")

    except Exception as e:
        messagebox.showerror("Error de PDF", f"Fallo al generar el reporte: {e}")

def generate_receipt(pago_info, user_info, is_regenerated=False):
    """
    Genera un recibo de pago en formato PDF.

    :param pago_info: Diccionario con detalles del pago (IdPago, Monto, MesPagado, FechaPago, Observacion).
    :param user_info: Diccionario con detalles del usuario (Nombre, Apellido, Direccion, NumeroPaja).
    :param is_regenerated: Boolean que indica si es una regeneración (para no mostrar mensaje).
    """
    try:
        # 1. Definir rutas y nombre del archivo
        receipt_dir = 'Recibos_Generados'
        if not os.path.exists(receipt_dir):
            os.makedirs(receipt_dir)

        receipt_number = f"REC-{pago_info['IdPago']:05d}"
        file_path = os.path.join(receipt_dir, f"{receipt_number}.pdf")
        
        # 2. Configurar el lienzo (Canvas)
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        
        # Posición inicial para dibujar
        y_pos = height - 50
        
        # 3. Encabezado del Recibo
        c.setFont('Helvetica-Bold', 18)
        c.drawCentredString(width / 2, y_pos, 'COMITÉ DE AGUA - ALDEA PANCHO DE LEÓN')
        y_pos -= 25
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(width / 2, y_pos, 'Recibo Oficial de Pago de Servicio de Agua')
        y_pos -= 35

        # 4. Información del Recibo
        c.setFont('Helvetica-Bold', 10)
        c.drawString(inch, y_pos, f"NÚMERO DE RECIBO: {receipt_number}")
        c.drawString(width - 2*inch, y_pos, f"Fecha de Emisión: {datetime.date.today().strftime('%d/%m/%Y')}")
        y_pos -= 25
        
        c.line(inch, y_pos, width - inch, y_pos)
        y_pos -= 20
        
        # 5. Datos del Usuario
        c.setFont('Helvetica-Bold', 11)
        c.drawString(inch, y_pos, 'DATOS DEL SUSCRIPTOR:')
        y_pos -= 15
        
        c.setFont('Helvetica', 10)
        c.drawString(inch + 0.2*inch, y_pos, f"Nombre Completo: {user_info['Nombre']} {user_info['Apellido']}")
        y_pos -= 15
        c.drawString(inch + 0.2*inch, y_pos, f"N° de Paja/Conexión: {user_info['NumeroPaja']}")
        y_pos -= 15
        c.drawString(inch + 0.2*inch, y_pos, f"Dirección: {user_info['Direccion']}")
        y_pos -= 30

        # 6. Detalles del Pago
        c.setFont('Helvetica-Bold', 11)
        c.drawString(inch, y_pos, 'DETALLES DEL PAGO:')
        y_pos -= 15
        
        c.setFont('Helvetica', 10)
        c.drawString(inch + 0.2*inch, y_pos, f"Mes Pagado: {pago_info['MesPagado']}")
        y_pos -= 15
        
        # Convertir FechaPago a string si es un objeto datetime/date
        fecha_pago = pago_info['FechaPago']
        if isinstance(fecha_pago, (datetime.datetime, datetime.date)):
            fecha_pago_str = fecha_pago.strftime('%d/%m/%Y')
        else:
            # Si ya es string, intentar parsearlo y reformatearlo
            try:
                fecha_temp = datetime.datetime.strptime(str(fecha_pago), '%Y-%m-%d')
                fecha_pago_str = fecha_temp.strftime('%d/%m/%Y')
            except:
                fecha_pago_str = str(fecha_pago)
        
        c.drawString(inch + 0.2*inch, y_pos, f"Fecha de Pago: {fecha_pago_str}")
        y_pos -= 15
        c.drawString(inch + 0.2*inch, y_pos, f"Método de Pago: {pago_info['MetodoPago']}")
        y_pos -= 20

        # 7. Observaciones (si existen)
        if pago_info.get('Observacion') and pago_info['Observacion'].strip():
            c.setFont('Helvetica-Bold', 10)
            c.drawString(inch + 0.2*inch, y_pos, "Observaciones:")
            y_pos -= 15
            c.setFont('Helvetica', 9)
            # Dividir texto largo en múltiples líneas si es necesario
            observacion_text = str(pago_info['Observacion'])
            max_width = width - 2.5*inch
            
            # Simple wrapping para observaciones largas
            if len(observacion_text) > 80:
                words = observacion_text.split()
                line = ""
                for word in words:
                    if len(line + word) < 80:
                        line += word + " "
                    else:
                        c.drawString(inch + 0.4*inch, y_pos, line.strip())
                        y_pos -= 12
                        line = word + " "
                if line:
                    c.drawString(inch + 0.4*inch, y_pos, line.strip())
                    y_pos -= 15
            else:
                c.drawString(inch + 0.4*inch, y_pos, observacion_text)
                y_pos -= 20
        
        y_pos -= 10

        # 8. Monto Total (Destacado)
        c.setFont('Helvetica-Bold', 14)
        c.drawString(inch, y_pos, "MONTO RECIBIDO:")
        
        # Asegurar que el monto sea un número válido
        try:
            monto_float = float(pago_info['Monto'])
            monto_str = f"Q {monto_float:.2f}"
        except (ValueError, TypeError):
            monto_str = f"Q {pago_info['Monto']}"
        
        c.drawString(width - 3*inch, y_pos, monto_str)
        y_pos -= 50

        # 9. Pie de página
        c.setFont('Helvetica-Oblique', 9)
        c.drawCentredString(width/2, inch, 'Gracias por contribuir al mantenimiento del servicio de agua potable.')
        
        # 10. Guardar el PDF
        c.showPage()
        c.save()
        
        # NO mostrar mensaje de confirmación, solo abrir el PDF
        # Abrir el PDF automáticamente
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':  # macOS
            os.system(f'open "{file_path}"')
        else:  # Linux
            os.system(f'xdg-open "{file_path}"')

    except Exception as e:
        messagebox.showerror("Error de PDF", f"No se pudo generar el recibo: {e}")

