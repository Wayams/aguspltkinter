# frontend/api_client.py
import requests
from typing import Optional, Dict, List
import json
from datetime import date, datetime

class APIClient:
    """Cliente para comunicarse con la API REST del backend."""
    
    def __init__(self, base_url: str = "https://aguaspl-production.up.railway.app"):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.user_data: Optional[Dict] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Obtiene los headers para las peticiones, incluyendo el token si existe."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _serialize_date(self, obj):
        """Serializa objetos date/datetime a string para JSON."""
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def login(self, usuario: str, clave: str) -> Dict:
        """Inicia sesión y guarda el token."""
        url = f"{self.base_url}/auth/login"
        data = {"usuario": usuario, "clave": clave}
        
        try:
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            
            result = response.json()
            self.token = result["access_token"]
            self.user_data = result["user_data"]
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error al iniciar sesión: {str(e)}")
    
    def logout(self):
        """Cierra la sesión y elimina el token."""
        self.token = None
        self.user_data = None
    
    # ========== USUARIOS ==========
    
    def get_users(self, active_only: bool = False) -> List[Dict]:
        """Obtiene todos los usuarios."""
        url = f"{self.base_url}/users/?active_only={'true' if active_only else 'false'}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_user(self, user_id: int) -> Dict:
        """Obtiene un usuario por ID."""
        url = f"{self.base_url}/users/{user_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def create_user(self, user_data: Dict) -> Dict:
        """Crea un nuevo usuario."""
        url = f"{self.base_url}/users/"
        response = requests.post(url, json=user_data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def update_user(self, user_id: int, user_data: Dict) -> Dict:
        """Actualiza un usuario."""
        url = f"{self.base_url}/users/{user_id}"
        response = requests.put(url, json=user_data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def toggle_user_status(self, user_id: int) -> Dict:
        """Cambia el estado de un usuario."""
        url = f"{self.base_url}/users/{user_id}/toggle-status"
        response = requests.patch(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    # ========== PAGOS ==========
    
    def get_payments(self, search: Optional[str] = None) -> List[Dict]:
        """Obtiene todos los pagos."""
        url = f"{self.base_url}/payments/"
        params = {}
        if search:
            params['search'] = search
        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_payment(self, payment_id: int) -> Dict:
        """Obtiene un pago por ID."""
        url = f"{self.base_url}/payments/{payment_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def create_payment(self, payment_data: Dict) -> Dict:
        """Crea un nuevo pago."""
        url = f"{self.base_url}/payments/"
        # Convertir fechas a string ISO
        if 'fecha_pago' in payment_data and isinstance(payment_data['fecha_pago'], (date, datetime)):
            payment_data['fecha_pago'] = payment_data['fecha_pago'].isoformat()
        
        response = requests.post(url, json=payment_data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    # ========== REPORTES ==========
    
    def get_morosos_report(self) -> Dict:
        """Obtiene el reporte de morosos."""
        url = f"{self.base_url}/reports/morosos"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_ingresos_report(self) -> Dict:
        """Obtiene el reporte de ingresos por mes."""
        url = f"{self.base_url}/reports/ingresos"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_pagos_usuario_report(self) -> Dict:
        """Obtiene el reporte de pagos por usuario."""
        url = f"{self.base_url}/reports/pagos-usuario"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    # ========== ADMINISTRADORES ==========
    
    def get_admins(self) -> List[Dict]:
        """Obtiene todos los administradores."""
        url = f"{self.base_url}/admins/"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_admin(self, admin_id: int) -> Dict:
        """Obtiene un administrador por ID."""
        url = f"{self.base_url}/admins/{admin_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def create_admin(self, admin_data: Dict) -> Dict:
        """Crea un nuevo administrador."""
        url = f"{self.base_url}/admins/"
        response = requests.post(url, json=admin_data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def update_admin(self, admin_id: int, admin_data: Dict) -> Dict:
        """Actualiza un administrador."""
        url = f"{self.base_url}/admins/{admin_id}"
        response = requests.put(url, json=admin_data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def change_admin_password(self, admin_id: int, nueva_clave: str) -> Dict:
        """Cambia la contraseña de un administrador."""
        url = f"{self.base_url}/admins/{admin_id}/change-password"
        data = {"nueva_clave": nueva_clave}
        response = requests.patch(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def delete_admin(self, admin_id: int) -> Dict:
        """Elimina un administrador."""
        url = f"{self.base_url}/admins/{admin_id}"
        response = requests.delete(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

