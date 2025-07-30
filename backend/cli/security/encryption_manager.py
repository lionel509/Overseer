"""
Encryption Manager

This module provides encryption and key management for the Overseer system,
ensuring sensitive data is protected at rest and in transit.
"""

import os
import base64
import hashlib
import secrets
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from .security_config import SecurityConfig

class EncryptionManager:
    """Manages encryption and key management for sensitive data"""
    
    def __init__(self, security_config: SecurityConfig):
        self.security_config = security_config
        self.master_key = None
        self.fernet = None
        self.key_file = os.path.expanduser("~/.overseer/encryption.key")
        
        # Initialize encryption
        self._initialize_encryption()
    
    def _initialize_encryption(self) -> None:
        """Initialize encryption system"""
        if not self.security_config.encryption_settings.enabled:
            return
        
        # Load or generate master key
        if os.path.exists(self.key_file):
            self._load_master_key()
        else:
            self._generate_master_key()
        
        # Initialize Fernet cipher
        if self.master_key:
            self.fernet = Fernet(self.master_key)
    
    def _generate_master_key(self) -> None:
        """Generate a new master encryption key"""
        # Generate a random key
        self.master_key = Fernet.generate_key()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
        
        # Save key to file (in production, this should be more secure)
        with open(self.key_file, 'wb') as f:
            f.write(self.master_key)
        
        # Set restrictive permissions
        os.chmod(self.key_file, 0o600)
    
    def _load_master_key(self) -> None:
        """Load master key from file"""
        try:
            with open(self.key_file, 'rb') as f:
                self.master_key = f.read()
        except Exception as e:
            print(f"Warning: Could not load encryption key: {e}")
            self._generate_master_key()
    
    def encrypt_data(self, data: str) -> Optional[str]:
        """Encrypt data using the master key"""
        if not self.security_config.encryption_settings.enabled or not self.fernet:
            return data
        
        try:
            # Convert string to bytes
            data_bytes = data.encode('utf-8')
            
            # Encrypt the data
            encrypted_bytes = self.fernet.encrypt(data_bytes)
            
            # Return base64 encoded string
            return base64.b64encode(encrypted_bytes).decode('utf-8')
            
        except Exception as e:
            print(f"Error encrypting data: {e}")
            return None
    
    def decrypt_data(self, encrypted_data: str) -> Optional[str]:
        """Decrypt data using the master key"""
        if not self.security_config.encryption_settings.enabled or not self.fernet:
            return encrypted_data
        
        try:
            # Decode base64 string to bytes
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt the data
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            
            # Return as string
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return None
    
    def encrypt_file(self, file_path: str) -> bool:
        """Encrypt a file in place"""
        if not self.security_config.encryption_settings.enabled:
            return True
        
        try:
            # Read file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Encrypt content
            encrypted_content = self.encrypt_data(content)
            if encrypted_content is None:
                return False
            
            # Write encrypted content back to file
            with open(file_path, 'w') as f:
                f.write(encrypted_content)
            
            return True
            
        except Exception as e:
            print(f"Error encrypting file {file_path}: {e}")
            return False
    
    def decrypt_file(self, file_path: str) -> bool:
        """Decrypt a file in place"""
        if not self.security_config.encryption_settings.enabled:
            return True
        
        try:
            # Read encrypted content
            with open(file_path, 'r') as f:
                encrypted_content = f.read()
            
            # Decrypt content
            decrypted_content = self.decrypt_data(encrypted_content)
            if decrypted_content is None:
                return False
            
            # Write decrypted content back to file
            with open(file_path, 'w') as f:
                f.write(decrypted_content)
            
            return True
            
        except Exception as e:
            print(f"Error decrypting file {file_path}: {e}")
            return False
    
    def encrypt_config_data(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive configuration data"""
        if not self.security_config.encryption_settings.enabled:
            return config_data
        
        encrypted_config = config_data.copy()
        
        # Define sensitive fields to encrypt
        sensitive_fields = [
            'gemini_api_key', 'openai_api_key', 'password', 'token',
            'secret', 'key', 'credential', 'auth_token'
        ]
        
        for field in sensitive_fields:
            if field in encrypted_config and encrypted_config[field]:
                encrypted_value = self.encrypt_data(str(encrypted_config[field]))
                if encrypted_value:
                    encrypted_config[field] = encrypted_value
        
        return encrypted_config
    
    def decrypt_config_data(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive configuration data"""
        if not self.security_config.encryption_settings.enabled:
            return config_data
        
        decrypted_config = config_data.copy()
        
        # Define sensitive fields to decrypt
        sensitive_fields = [
            'gemini_api_key', 'openai_api_key', 'password', 'token',
            'secret', 'key', 'credential', 'auth_token'
        ]
        
        for field in sensitive_fields:
            if field in decrypted_config and decrypted_config[field]:
                decrypted_value = self.decrypt_data(str(decrypted_config[field]))
                if decrypted_value:
                    decrypted_config[field] = decrypted_value
        
        return decrypted_config
    
    def generate_secure_password(self, length: int = 32) -> str:
        """Generate a secure random password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """Hash a password with salt"""
        if salt is None:
            salt = os.urandom(16)
        
        # Use PBKDF2 for password hashing
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        return base64.b64encode(key).decode(), base64.b64encode(salt).decode()
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verify a password against its hash"""
        try:
            # Decode the stored hash and salt
            stored_key = base64.b64decode(hashed_password.encode())
            stored_salt = base64.b64decode(salt.encode())
            
            # Hash the provided password with the stored salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=stored_salt,
                iterations=100000,
                backend=default_backend()
            )
            
            key = kdf.derive(password.encode())
            
            # Compare the hashes
            return secrets.compare_digest(stored_key, key)
            
        except Exception:
            return False
    
    def rotate_keys(self) -> bool:
        """Rotate encryption keys"""
        if not self.security_config.encryption_settings.enabled:
            return True
        
        try:
            # Generate new master key
            new_master_key = Fernet.generate_key()
            new_fernet = Fernet(new_master_key)
            
            # Backup old key
            backup_file = f"{self.key_file}.backup"
            if os.path.exists(self.key_file):
                os.rename(self.key_file, backup_file)
            
            # Save new key
            with open(self.key_file, 'wb') as f:
                f.write(new_master_key)
            
            # Update instance variables
            self.master_key = new_master_key
            self.fernet = new_fernet
            
            # Set restrictive permissions
            os.chmod(self.key_file, 0o600)
            
            return True
            
        except Exception as e:
            print(f"Error rotating encryption keys: {e}")
            return False
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """Get encryption system status"""
        return {
            'enabled': self.security_config.encryption_settings.enabled,
            'algorithm': self.security_config.encryption_settings.algorithm,
            'key_rotation_days': self.security_config.encryption_settings.key_rotation_days,
            'encrypt_config': self.security_config.encryption_settings.encrypt_config,
            'encrypt_logs': self.security_config.encryption_settings.encrypt_logs,
            'key_file_exists': os.path.exists(self.key_file),
            'master_key_loaded': self.master_key is not None,
            'fernet_initialized': self.fernet is not None
        }
    
    def cleanup(self) -> None:
        """Clean up encryption resources"""
        # Clear sensitive data from memory
        if self.master_key:
            # Overwrite the key in memory
            self.master_key = b'\x00' * len(self.master_key)
            self.master_key = None
        
        if self.fernet:
            self.fernet = None 