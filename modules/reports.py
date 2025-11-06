# frontend/modules/reports.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from api_client import APIClient
import datetime
from modules.pdf_generator import generate_report_pdf 
import openpyxl
import os

class ReportsWindow(ctk.CTkFrame): 
    def __init__(self, master, api_client: APIClient):
        super().__init__(master)
        self.api_client = api_client
        
        # Variables para capturar los datos y encabezados de la última consulta
        self.current_report_data = []
        self.current_report_title = ""
        self.current_report_headers = []
        
        self.configure_treeview_style()
        self.build_ui()
        self.show_welcome_message()

    def configure_treeview_style(self):
        """Configura el estilo visual de la tabla (Treeview) de Tkinter."""
        style = ttk.Style()
        style.theme_use("clam") 

        style.configure("Treeview", 
                        background="#2A2D2E",  
                        foreground="#DCE4EE",  
                        rowheight=25,
                        fieldbackground="#2A2D2E",
                        borderwidth=0)
        
        style.configure("Treeview.Heading", 
                        font=('Segoe UI', 11, 'bold'),
                        background="#3A7CB1", 
                        foreground="white",
                        relief="flat")
        
        style.map('Treeview', 
                  background=[('selected', '#1F6AA5')], 
                  foreground=[('selected', 'white')])

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(self, text='Generador de Reportes', font=('Segoe UI', 18, 'bold')).grid(row=0, column=0, sticky='w', padx=15, pady=(15, 5))

        # --- Fila 1: Contenedor de Botones de Reporte y Acciones ---
        control_frame = ctk.CTkFrame(self)
        control_frame.grid(row=1, column=0, sticky='ew', padx=15, pady=10)
        control_frame.grid_columnconfigure(0, weight=1)
        
        # Sub-contenedor para los botones de tipo de reporte
        btn_report_type_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_report_type_frame.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        ctk.CTkLabel(btn_report_type_frame, text="Tipo de Reporte:", font=('Segoe UI', 12, 'bold')).pack(side='left', padx=(0, 10))
        ctk.CTkButton(btn_report_type_frame, text='Morosos (>35 días)', command=self.report_morosos, fg_color="#F44336", hover_color="#D32F2F").pack(side='left', padx=6)
        ctk.CTkButton(btn_report_type_frame, text='Ingresos por Mes', command=self.report_ingresos).pack(side='left', padx=6)
        ctk.CTkButton(btn_report_type_frame, text='Pagos por Usuario', command=self.report_pagos_usuario).pack(side='left', padx=6)

        # Sub-contenedor para los botones de acción (Exportar)
        btn_action_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_action_frame.grid(row=0, column=1, sticky='e', padx=10, pady=5)
        
        ctk.CTkLabel(btn_action_frame, text="Exportar:", font=('Segoe UI', 12, 'bold')).pack(side='left', padx=(0, 10))
        
        self.btn_export_pdf = ctk.CTkButton(btn_action_frame, 
                                            text='Exportar PDF', 
                                            command=self.export_pdf, 
                                            fg_color="#E91E63",
                                            hover_color="#C2185B",
                                            state="disabled")
        self.btn_export_pdf.pack(side='left', padx=6)
        
        self.btn_export_excel = ctk.CTkButton(btn_action_frame, 
                                            text='Exportar Excel', 
                                            command=self.export_excel, 
                                            fg_color="#00C853",
                                            hover_color="#00A040",
                                            state="disabled")
        self.btn_export_excel.pack(side='left', padx=6)

        # --- Fila 2: Contenedor de Tabla y Mensaje de Bienvenida ---
        self.content_container = ctk.CTkFrame(self)
        self.content_container.grid(row=2, column=0, sticky='nsew', padx=15, pady=(0, 15))
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)
        
        # Label para el título del reporte
        self.title_label = ctk.CTkLabel(self.content_container, text="", font=('Segoe UI', 14, 'italic'))
        self.title_label.pack(side='top', fill='x', padx=10, pady=(10, 5))

        # Frame para el mensaje de bienvenida (se mostrará inicialmente)
        self.welcome_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        
        self.welcome_label = ctk.CTkLabel(
            self.welcome_frame, 
            text="📊 REPORTES 📊", 
            font=('Segoe UI', 48, 'bold'),
            text_color="#3A7CB1"
        )
        self.welcome_label.pack(expand=True)
        
        self.welcome_subtitle = ctk.CTkLabel(
            self.welcome_frame,
            text="Seleccione un tipo de reporte para comenzar",
            font=('Segoe UI', 16),
            text_color="#888888"
        )
        self.welcome_subtitle.pack(expand=True, pady=(10, 0))

        # Frame para la tabla (inicialmente oculto)
        self.table_frame = ctk.CTkFrame(self.content_container)
        
        # Configuración de Treeview (Tabla)
        self.tree = ttk.Treeview(self.table_frame, show='headings')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        vsb.place(relx=1.0, rely=0, relheight=1.0, width=20, anchor='ne')
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Mostrar mensaje de bienvenida al iniciar
        self.show_welcome_message()
        
    def show_welcome_message(self):
        """Muestra el mensaje de bienvenida y oculta la tabla."""
        # Limpiar cualquier dato anterior
        self.current_report_data = []
        self.current_report_title = ""
        self.current_report_headers = []
        
        # Limpiar la tabla completamente
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Ocultar tabla y mostrar mensaje
        self.table_frame.pack_forget()
        self.welcome_frame.pack(fill='both', expand=True)
        self.title_label.configure(text="")
        self.btn_export_pdf.configure(state="disabled")
        self.btn_export_excel.configure(state="disabled")
        
    def show_table(self):
        """Muestra la tabla y oculta el mensaje de bienvenida."""
        self.welcome_frame.pack_forget()
        self.table_frame.pack(fill='both', expand=True)
    
    def display_report(self, title, headers, rows, tag_logic=None):
        """Limpia la tabla y muestra los resultados, guardando los datos para exportación."""
        
        # Mostrar la tabla (ocultar mensaje de bienvenida)
        self.show_table()
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Configurar columnas y encabezados
        self.tree['columns'] = headers
        self.tree.config(show='headings') 
        
        for col in headers:
            self.tree.heading(col, text=col)
            # Ajustar el ancho y CENTRAR todas las columnas
            if col == 'ID' or col == 'ID Pago':
                self.tree.column(col, width=80, anchor='center')
            elif col == 'N° Paja':
                self.tree.column(col, width=100, anchor='center')
            elif col in ['Monto Total (Q)', 'Monto (Q)']:
                self.tree.column(col, width=120, anchor='center')
            elif col == 'Teléfono':
                self.tree.column(col, width=120, anchor='center')
            elif col == 'Días Mora':
                self.tree.column(col, width=100, anchor='center')
            elif col in ['Fecha Pago', 'Último Pago']:
                self.tree.column(col, width=120, anchor='center')
            elif col in ['Total Pagos', 'Método']:
                self.tree.column(col, width=110, anchor='center')
            else:
                self.tree.column(col, width=180, anchor='center')
                
        # Guardar datos para exportación
        self.current_report_title = title
        self.current_report_headers = headers
        self.current_report_data = rows
        
        # Insertar filas
        if not rows:
            self.tree.insert('', 'end', values=("No hay datos para este reporte.",), tags=('empty',))
            self.tree.tag_configure('empty', foreground='gray')
            self.btn_export_pdf.configure(state="disabled")
            self.btn_export_excel.configure(state="disabled")
        else:
            for row in rows:
                tag = tag_logic(row) if tag_logic else ''
                self.tree.insert('', 'end', values=row, tags=(tag,))
                
            self.btn_export_pdf.configure(state="normal")
            self.btn_export_excel.configure(state="normal")

        # Actualizar Título en la UI
        self.title_label.configure(text=f"Reporte Actual: {title}")

    # --- Reportes Específicos ---

    def report_morosos(self):
        """Genera el reporte de usuarios morosos (más de 35 días sin pagar) usando la API."""
        try:
            report_data = self.api_client.get_morosos_report()
            headers = report_data['encabezados']
            data = report_data['datos']
            
            # Configurar estilo especial para morosos (rojo)
            self.tree.tag_configure('debtor', foreground='#FF5722')
            tag_logic = lambda row: 'debtor'
            
            self.display_report("Morosos (Más de 35 días)", headers, data, tag_logic)
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                messagebox.showerror("Error de Conexión", f"No se pudo conectar con el servidor: {error_msg}")
            else:
                messagebox.showerror("Error de Base de Datos", f"Error al generar reporte: {error_msg}")

    def report_ingresos(self):
        """Genera el reporte de ingresos agrupados por mes de pago usando la API."""
        try:
            report_data = self.api_client.get_ingresos_report()
            headers = report_data['encabezados']
            data = report_data['datos']
            
            self.display_report("Ingresos por Mes", headers, data)
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                messagebox.showerror("Error de Conexión", f"No se pudo conectar con el servidor: {error_msg}")
            else:
                messagebox.showerror("Error de Base de Datos", f"Error al generar reporte: {error_msg}")

    def report_pagos_usuario(self):
        """Genera el reporte de todos los pagos realizados, detallando por usuario usando la API."""
        try:
            report_data = self.api_client.get_pagos_usuario_report()
            headers = report_data['encabezados']
            data = report_data['datos']
            
            # Colores para el método de pago
            self.tree.tag_configure('efectivo', foreground='#4CAF50')
            self.tree.tag_configure('credito', foreground='#FF5722')
            
            tag_logic = lambda row: 'efectivo' if len(row) > 6 and row[6].lower() == 'efectivo' else 'credito'
            
            self.display_report("Detalle de Pagos por Usuario", headers, data, tag_logic)
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                messagebox.showerror("Error de Conexión", f"No se pudo conectar con el servidor: {error_msg}")
            else:
                messagebox.showerror("Error de Base de Datos", f"Error al generar reporte: {error_msg}")

    # --- Funciones de Exportación ---

    def export_pdf(self):
        """Llama a la función del módulo pdf_generator para crear el PDF."""
        if not self.current_report_data:
            messagebox.showwarning("Advertencia", "No hay datos para exportar. Genere un reporte primero.")
            return
        
        generate_report_pdf(self.current_report_title, self.current_report_headers, self.current_report_data)

    def export_excel(self):
        """Exporta los datos del reporte actual a un archivo Excel (.xlsx)."""
        if not self.current_report_data:
            messagebox.showwarning("Advertencia", "No hay datos para exportar. Genere un reporte primero.")
            return

        # 1. Definir el nombre de archivo y carpeta
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        default_filename = f"{self.current_report_title.replace(' ', '_')}_{today_str}.xlsx"
        
        # Usar filedialog para que el usuario elija dónde guardar
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_filename,
            title="Guardar Reporte Excel",
            filetypes=(("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*"))
        )
        
        if not filepath:
            return

        try:
            # 2. Crear el libro y la hoja de trabajo
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = self.current_report_title[:31]  # Excel limita a 31 caracteres

            # 3. Escribir los encabezados (Headers)
            sheet.append(self.current_report_headers)

            # 4. Escribir los datos
            data_for_excel = []
            for row in self.current_report_data:
                cleaned_row = list(row)
                for i, item in enumerate(cleaned_row):
                    if isinstance(item, str):
                        # Limpiar formato de monto 'Q X,XXX.XX' a 'X.XX'
                        if item.startswith('Q '):
                            try:
                                cleaned_row[i] = float(item[2:].replace(',', ''))
                            except ValueError:
                                pass
                data_for_excel.append(cleaned_row)
                sheet.append(cleaned_row)
                
            # 5. Guardar el archivo
            workbook.save(filepath)
            
            # 6. Mensaje de éxito
            messagebox.showinfo("Exportación Exitosa", f"El reporte ha sido exportado correctamente.")
            
        except Exception as e:
            messagebox.showerror("Error de Exportación", f"Ocurrió un error al exportar a Excel: {e}")
    
    def reset_view(self):
        """Resetea la vista al mensaje de bienvenida. Útil al cambiar de módulo."""
        self.show_welcome_message()

