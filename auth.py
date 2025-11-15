import json
import os
import hashlib
import secrets

USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')


def hash_password(password, salt=None):
    """
    Crea un hash de la contraseña usando SHA256 con salt.
    Usa 1000 iteraciones para seguridad básica.
    """
    if salt is None:
        salt = secrets.token_hex(8)  # 16 caracteres hexadecimales
    
    # Aplicar hash con iteraciones
    iterations = 1000
    hash_result = password.encode('utf-8')
    
    for _ in range(iterations):
        hash_result = hashlib.sha256(hash_result + salt.encode('utf-8')).digest()
    
    hash_hex = hash_result.hex()
    return f'sha256:{iterations}:{salt}:{hash_hex}'


def verify_password(password, stored_hash):
    """Verifica una contraseña contra su hash almacenado"""
    parts = stored_hash.split(':')
    
    if len(parts) == 4 and parts[0] == 'sha256':
        # Formato con salt: sha256:iterations:salt:hash
        _, iterations_str, salt, expected_hash = parts
        iterations = int(iterations_str)
        
        # Recalcular hash con el mismo salt
        hash_result = password.encode('utf-8')
        for _ in range(iterations):
            hash_result = hashlib.sha256(hash_result + salt.encode('utf-8')).digest()
        
        computed_hash = hash_result.hex()
        return computed_hash == expected_hash
    
    else:
        # Texto plano (solo para desarrollo)
        return password == stored_hash


def load_users():
    """Carga los usuarios del archivo JSON"""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    users = {}
    for u in data.get('users', []):
        users[u['username']] = u.get('password')
    return users


def verify_user(username, password):
    """Verifica las credenciales de un usuario"""
    users = load_users()
    stored = users.get(username)
    if stored is None:
        return False
    
    return verify_password(password, stored)


def add_user(username, password, use_hash=True):
    """Agrega un nuevo usuario al sistema"""
    users = load_users()
    if username in users:
        raise ValueError('User already exists')
    
    if use_hash:
        to_store = hash_password(password)
    else:
        # Solo para desarrollo/testing
        to_store = password
    
    # Escribir de vuelta al archivo
    data = {'users': []}
    for k, v in users.items():
        data['users'].append({'username': k, 'password': v})
    data['users'].append({'username': username, 'password': to_store})
    
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f'✓ User "{username}" added successfully')


def update_user_password(username, new_password):
    """Actualiza la contraseña de un usuario existente"""
    users = load_users()
    if username not in users:
        raise ValueError('User not found')
    
    users[username] = hash_password(new_password)
    
    # Escribir de vuelta
    data = {'users': []}
    for k, v in users.items():
        data['users'].append({'username': k, 'password': v})
    
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f'✓ Password updated for "{username}"')


# Script de utilidad para agregar usuarios desde línea de comandos
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print('User Management Utility')
        print('')
        print('Usage:')
        print('  python3 auth.py add <username> <password>    - Add user')
        print('  python3 auth.py update <username> <password> - Update password')
        print('  python3 auth.py list                        - List users')
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'add':
        if len(sys.argv) != 4:
            print('Error: username and password required')
            sys.exit(1)
        username, password = sys.argv[2], sys.argv[3]
        try:
            add_user(username, password)
        except ValueError as e:
            print(f'✗ Error: {e}')
    
    elif command == 'update':
        if len(sys.argv) != 4:
            print('Error: username and password required')
            sys.exit(1)
        username, password = sys.argv[2], sys.argv[3]
        try:
            update_user_password(username, password)
        except ValueError as e:
            print(f'✗ Error: {e}')
    
    elif command == 'list':
        users = load_users()
        print(f'Registered users: {len(users)}')
        for username in users.keys():
            print(f'  - {username}')
    
    else:
        print(f'Unknown command: {command}')
        sys.exit(1)

