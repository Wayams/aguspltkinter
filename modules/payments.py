# frontend/modules/payments.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from api_client import APIClient
import datetime
from modules.pdf_generator import generate_receipt
import calendar

class PaymentsWindow(ctk.CTkFrame): 
    def __init__(self, master, api_client: APIClient):
        super().__init__(master)
        self.api_client = api_client
        
        self.configure_treeview_style() 
        self.build_ui()
        self.load_users()
        self.load_payments()

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
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text='Registro de Pagos', font=('Segoe UI', 18, 'bold')).grid(row=0, column=0, sticky='w', padx=15, pady=(15, 5))

        # --- Contenedor del Formulario ---
        form_container = ctk.CTkFrame(self)
        form_container.grid(row=0, column=0, sticky='ew', padx=15, pady=(0, 10))
        
        form_container.grid_columnconfigure((0, 2, 4), weight=0)
        form_container.grid_columnconfigure((1, 3), weight=1)
        form_container.grid_columnconfigure(5, weight=0)

        # Variables de formulario
        self.users_dict = {}
        self.selected_user_id = None
        self.user_names = ['Cargando Usuarios...']
        self.selected_user_var = ctk.StringVar(value=self.user_names[0])
        
        self.fecha_var = ctk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.monto_var = ctk.StringVar()
        
        # Generar lista de meses
        self.generate_month_list()
        self.mes_var = ctk.StringVar(value=self.month_list[0])
        
        self.metodo_var = ctk.StringVar(value='Efectivo')
        self.observacion_var = ctk.StringVar()
        
        # Fila 0: Usuario y Monto
        ctk.CTkLabel(form_container, text="Suscriptor:", font=('Segoe UI', 12)).grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        self.user_dropdown = ctk.CTkOptionMenu(form_container, 
                                               values=self.user_names, 
                                               variable=self.selected_user_var,
                                               command=self.on_user_select,
                                               height=35)
        self.user_dropdown.grid(row=0, column=1, padx=(0, 15), pady=10, sticky="ew")

        ctk.CTkLabel(form_container, text="Monto (Q):", font=('Segoe UI', 12)).grid(row=0, column=2, padx=(10, 5), pady=10, sticky="w")
        ctk.CTkEntry(form_container, textvariable=self.monto_var, height=35).grid(row=0, column=3, padx=(0, 15), pady=10, sticky="ew")

        # Fila 1: Mes Pagado y Método de Pago
        ctk.CTkLabel(form_container, text="Mes Pagado:", font=('Segoe UI', 12)).grid(row=1, column=0, padx=(10, 5), pady=10, sticky="w")
        self.mes_dropdown = ctk.CTkOptionMenu(form_container, 
                                              values=self.month_list,
                                              variable=self.mes_var,
                                              height=35)
        self.mes_dropdown.grid(row=1, column=1, padx=(0, 15), pady=10, sticky="ew")

        ctk.CTkLabel(form_container, text="Método:", font=('Segoe UI', 12)).grid(row=1, column=2, padx=(10, 5), pady=10, sticky="w")
        ctk.CTkOptionMenu(form_container, 
                          values=['Efectivo', 'Crédito', 'Transferencia'], 
                          variable=self.metodo_var,
                          height=35).grid(row=1, column=3, padx=(0, 15), pady=10, sticky="ew")

        # Fila 2: Observaciones
        ctk.CTkLabel(form_container, text="Observación:", font=('Segoe UI', 12)).grid(row=2, column=0, padx=(10, 5), pady=10, sticky="w")
        ctk.CTkEntry(form_container, 
                     textvariable=self.observacion_var, 
                     placeholder_text="Notas, moras u otras observaciones...",
                     height=35).grid(row=2, column=1, columnspan=3, padx=(0, 15), pady=10, sticky="ew")

        # Botón de Acción (ocupa 3 filas)
        self.register_btn = ctk.CTkButton(form_container, 
                                          text='REGISTRAR\nPAGO', 
                                          command=self.add_payment, 
                                          fg_color="#00C853",
                                          hover_color="#00A040",
                                          height=105, 
                                          font=('Segoe UI', 14, 'bold'))
        self.register_btn.grid(row=0, column=5, rowspan=3, padx=(15, 10), pady=10, sticky="nsew")

        # --- Contenedor de la Tabla ---
        table_container = ctk.CTkFrame(self)
        table_container.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0, 15))
        table_container.grid_rowconfigure(1, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # Barra de Búsqueda
        search_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, 
                                         textvariable=self.search_var, 
                                         placeholder_text="Buscar Pago (ID o Mes)...",
                                         height=35,
                                         font=('Segoe UI', 12))
        self.search_entry.grid(row=0, column=0, sticky='ew', padx=(0, 8))
        
        ctk.CTkButton(search_frame, 
                      text="🔍 Buscar", 
                      command=lambda: self.load_payments(self.search_var.get()), 
                      width=100,
                      height=35,
                      fg_color="#3F51B5").grid(row=0, column=1, padx=8) 
        
        ctk.CTkButton(search_frame, 
                      text="🔄", 
                      command=lambda: self.load_payments(clear_search=True), 
                      width=40,
                      height=35,
                      fg_color="#FF9800").grid(row=0, column=2, padx=8) 

        # Tabla (Treeview)
        self.tree = ttk.Treeview(table_container, columns=('IdPago', 'Nombre', 'Paja', 'Fecha', 'Monto', 'Mes', 'Metodo', 'Observacion'), show='headings')
        self.tree.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        
        # Scrollbar
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        vsb.grid(row=1, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=vsb.set)

        # Definir encabezados
        self.tree.heading('IdPago', text='ID Pago')
        self.tree.heading('Nombre', text='Suscriptor')
        self.tree.heading('Paja', text='N° Paja')
        self.tree.heading('Fecha', text='Fecha Pago')
        self.tree.heading('Monto', text='Monto (Q)')
        self.tree.heading('Mes', text='Mes Pagado')
        self.tree.heading('Metodo', text='Método')
        self.tree.heading('Observacion', text='Observación')
        
        # Anchos de columna
        self.tree.column('IdPago', width=60, anchor='center')
        self.tree.column('Nombre', width=180)
        self.tree.column('Paja', width=70, anchor='center')
        self.tree.column('Fecha', width=90, anchor='center')
        self.tree.column('Monto', width=80, anchor='e')
        self.tree.column('Mes', width=110, anchor='center')
        self.tree.column('Metodo', width=90, anchor='center')
        self.tree.column('Observacion', width=180)
        
        # Binding para regenerar recibo
        self.tree.bind('<Double-1>', self.re_generate_receipt)

    def generate_month_list(self):
        """Genera una lista de meses desde hace 6 meses hasta 12 meses en el futuro."""
        self.month_list = []
        current_date = datetime.date.today()
        
        # Generar desde 6 meses atrás hasta 12 meses adelante
        for i in range(-6, 13):
            date = current_date + datetime.timedelta(days=30*i)
            month_name = date.strftime("%B %Y")
            # Traducir meses al español
            month_name = self.translate_month(month_name)
            if month_name not in self.month_list:
                self.month_list.append(month_name)

    def translate_month(self, month_str):
        """Traduce los nombres de meses del inglés al español."""
        months_translation = {
            'January': 'Enero',
            'February': 'Febrero',
            'March': 'Marzo',
            'April': 'Abril',
            'May': 'Mayo',
            'June': 'Junio',
            'July': 'Julio',
            'August': 'Agosto',
            'September': 'Septiembre',
            'October': 'Octubre',
            'November': 'Noviembre',
            'December': 'Diciembre'
        }
        
        for eng, esp in months_translation.items():
            month_str = month_str.replace(eng, esp)
        
        return month_str

    def load_users(self):
        """Carga los usuarios activos para el OptionMenu de registro usando la API."""
        try:
            users = self.api_client.get_users(active_only=True)
            
            self.users_dict = {}
            self.user_names = []
            
            for user in users:
                user_id = user['id_usuario']
                full_name = f"{user['nombre']} {user['apellido']} (Paja: {user['numero_paja']})"
                self.users_dict[full_name] = user_id
                self.user_names.append(full_name)

            if self.user_names:
                self.selected_user_var.set(self.user_names[0])
                self.user_dropdown.configure(values=self.user_names)
                self.on_user_select(self.user_names[0])
            else:
                self.user_names = ['No hay usuarios activos']
                self.selected_user_var.set('No hay usuarios activos')
                self.user_dropdown.configure(values=['No hay usuarios activos'])
                self.register_btn.configure(state="disabled")

        except Exception as e:
            error_msg = str(e)
            messagebox.showerror("Error", f"Error al cargar usuarios para pago: {error_msg}")

    def on_user_select(self, user_name):
        """Actualiza el ID del usuario seleccionado."""
        self.selected_user_id = self.users_dict.get(user_name)
        if self.selected_user_id:
            self.register_btn.configure(state="normal")
        else:
            self.register_btn.configure(state="disabled")

    def clear_form(self):
        """Limpia los campos del formulario de registro."""
        self.monto_var.set('')
        self.metodo_var.set('Efectivo')
        self.fecha_var.set(datetime.date.today().strftime("%Y-%m-%d"))
        self.observacion_var.set('')
        # Actualizar el mes al mes actual
        current_month = self.translate_month(datetime.date.today().strftime("%B %Y"))
        if current_month in self.month_list:
            self.mes_var.set(current_month)

    def load_payments(self, search_term=None, clear_search=False):
        """Carga los pagos desde la API y actualiza el Treeview."""
        if clear_search:
            self.search_var.set('')
            search_term = None
            
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            payments = self.api_client.get_payments(search=search_term)
            
            if not payments:
                self.tree.insert('', 'end', values=("", "No hay pagos", "o coincidencias", "", "", "", "", ""), tags=('empty',))
                self.tree.tag_configure('empty', foreground='gray')
                return

            for payment in payments:
                id_pago = payment['id_pago']
                nombre_completo = f"{payment['nombre']} {payment['apellido']}"
                paja = str(payment['numero_paja'])
                
                # Formatear fecha
                fecha_pago = payment['fecha_pago']
                if isinstance(fecha_pago, str):
                    try:
                        fecha_dt = datetime.datetime.fromisoformat(fecha_pago.replace('Z', '+00:00'))
                        fecha_str = fecha_dt.strftime('%Y-%m-%d')
                    except:
                        fecha_str = fecha_pago[:10] if len(fecha_pago) >= 10 else fecha_pago
                else:
                    fecha_str = str(fecha_pago)[:10]
                
                monto_str = f"Q {payment['monto']:.2f}"
                mes = payment['mes_pagado']
                metodo = payment['metodo_pago']
                observacion_str = payment.get('observacion', '') or ""
                
                tag = 'efectivo' if metodo.lower() == 'efectivo' else 'credito'
                
                self.tree.insert('', 'end', 
                                 values=(id_pago, nombre_completo, paja, fecha_str, monto_str, mes, metodo, observacion_str),
                                 tags=(tag,),
                                 iid=str(id_pago)) 
                
                self.tree.tag_configure('efectivo', foreground='#FFFFFF')
                self.tree.tag_configure('credito', foreground='#FF5722')

        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                messagebox.showerror("Error de Conexión", f"No se pudo conectar con el servidor: {error_msg}")
            else:
                messagebox.showerror("Error de Base de Datos", f"Error al cargar pagos: {error_msg}")
            
    def add_payment(self):
        """Guarda el nuevo pago usando la API y genera el recibo."""
        
        if self.selected_user_id is None:
            messagebox.showerror("Error", "Debe seleccionar un suscriptor válido.")
            return

        try:
            monto = float(self.monto_var.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El Monto debe ser un número válido.")
            return

        mes_pagado = self.mes_var.get().strip()
        metodo_pago = self.metodo_var.get().strip()
        fecha_pago_str = self.fecha_var.get().strip()
        observacion = self.observacion_var.get().strip()
        
        # Validaciones
        if not (monto > 0 and mes_pagado and metodo_pago):
            messagebox.showerror("Error", "Monto, Mes Pagado y Método de Pago son obligatorios.")
            return
            
        # Intentar convertir fecha
        try:
            fecha_pago = datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "El formato de fecha debe ser YYYY-MM-DD.")
            return

        try:
            # Crear pago usando la API
            payment_data = {
                "id_usuario": self.selected_user_id,
                "fecha_pago": fecha_pago.isoformat(),
                "monto": monto,
                "mes_pagado": mes_pagado,
                "metodo_pago": metodo_pago,
                "observacion": observacion if observacion else None
            }
            
            new_payment = self.api_client.create_payment(payment_data)
            
            messagebox.showinfo('Éxito', 'Pago registrado correctamente.')
            self.load_payments()

            # Generar Recibo usando los datos del pago creado
            payment_detail = self.api_client.get_payment(new_payment['id_pago'])
            
            if payment_detail:
                pago_info = {
                    'IdPago': payment_detail['id_pago'],
                    'Monto': payment_detail['monto'],
                    'MesPagado': payment_detail['mes_pagado'],
                    'FechaPago': payment_detail['fecha_pago'],
                    'MetodoPago': payment_detail['metodo_pago'],
                    'Observacion': payment_detail.get('observacion')
                }
                user_info = {
                    'Nombre': payment_detail['nombre'],
                    'Apellido': payment_detail['apellido'],
                    'Direccion': payment_detail.get('direccion', ''),
                    'NumeroPaja': str(payment_detail['numero_paja'])
                }
                generate_receipt(pago_info, user_info)
            
            self.clear_form()

        except Exception as e:
            error_msg = str(e)
            if "Ya existe" in error_msg or "duplicado" in error_msg.lower():
                messagebox.showerror('Error de Duplicidad', 
                                   f"Ya existe un pago registrado para este usuario en {mes_pagado}.\n\n"
                                   "No se pueden registrar dos pagos para el mismo mes.")
            elif "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                messagebox.showerror('Error de Conexión', f'No se pudo conectar con el servidor: {error_msg}')
            else:
                messagebox.showerror('Error', f'Error al guardar el pago: {error_msg}')

    def re_generate_receipt(self, event):
        """Regenera el recibo de un pago al hacer doble clic en la tabla."""
        selected_item = self.tree.focus()
        if not selected_item or self.tree.item(selected_item, 'tags') == ('empty',):
            return

        id_pago_str = self.tree.item(selected_item, 'values')[0]
        
        try:
            id_pago = int(id_pago_str)
        except (ValueError, IndexError):
            return
        
        if not messagebox.askyesno("Confirmar Regeneración", f"¿Desea generar nuevamente el recibo para el Pago ID {id_pago}?"):
            return
            
        try:
            payment_detail = self.api_client.get_payment(id_pago)
            
            if payment_detail:
                pago_info = {
                    'IdPago': payment_detail['id_pago'],
                    'Monto': payment_detail['monto'],
                    'MesPagado': payment_detail['mes_pagado'],
                    'FechaPago': payment_detail['fecha_pago'],
                    'MetodoPago': payment_detail['metodo_pago'],
                    'Observacion': payment_detail.get('observacion')
                }
                user_info = {
                    'Nombre': payment_detail['nombre'],
                    'Apellido': payment_detail['apellido'],
                    'Direccion': payment_detail.get('direccion', ''),
                    'NumeroPaja': str(payment_detail['numero_paja'])
                }
                generate_receipt(pago_info, user_info, is_regenerated=True)
            else:
                messagebox.showwarning("Advertencia", "No se encontraron detalles para este pago.")

        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                messagebox.showerror('Error de Conexión', f'No se pudo conectar con el servidor: {error_msg}')
            else:
                messagebox.showerror('Error', f'Error al regenerar recibo: {error_msg}')

