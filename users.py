"""
Módulo de gestión de usuarios del portal cautivo.
Maneja la definición de cuentas y autenticación.
"""

import json
import hashlib
import os
from threading import Lock


class UserManager:
    """Gestiona las cuentas de usuario del portal cautivo."""
    
    def __init__(self, users_file="users.json"):
        """
        Inicializa el gestor de usuarios.
        
        Args:
            users_file: Ruta al archivo JSON con los usuarios
        """
        self.users_file = users_file
        self.lock = Lock()
        self._load_users()
    
    def _load_users(self):
        """Carga los usuarios desde el archivo JSON."""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            # Usuarios por defecto si no existe el archivo
            self.users = {
                "admin": self._hash_password("admin123"),
                "usuario1": self._hash_password("pass1234"),
                "usuario2": self._hash_password("pass5678")
            }
            self._save_users()
    
    def _save_users(self):
        """Guarda los usuarios en el archivo JSON."""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _hash_password(self, password):
        """
        Genera un hash SHA-256 de la contraseña.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash hexadecimal de la contraseña
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """
        Autentica un usuario con sus credenciales.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            True si las credenciales son válidas, False en caso contrario
        """
        with self.lock:
            if username not in self.users:
                return False
            
            password_hash = self._hash_password(password)
            return self.users[username] == password_hash
    
    def add_user(self, username, password):
        """
        Añade un nuevo usuario.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            True si se añadió exitosamente, False si el usuario ya existe
        """
        with self.lock:
            if username in self.users:
                return False
            
            self.users[username] = self._hash_password(password)
            self._save_users()
            return True
    
    def remove_user(self, username):
        """
        Elimina un usuario.
        
        Args:
            username: Nombre de usuario a eliminar
            
        Returns:
            True si se eliminó exitosamente, False si no existe
        """
        with self.lock:
            if username not in self.users:
                return False
            
            del self.users[username]
            self._save_users()
            return True
    
    def list_users(self):
        """
        Lista todos los usuarios registrados.
        
        Returns:
            Lista de nombres de usuario
        """
        with self.lock:
            return list(self.users.keys())
        

