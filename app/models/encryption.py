import os
from base64 import b64encode, b64decode
from cryptography.fernet import Fernet

class CredentialEncryption:
    def __init__(self):
        # Get or generate master key (store this securely, perhaps as an environment variable)
        self.master_key = os.getenv('MASTER_KEY')
        if not self.master_key:
            self.master_key = Fernet.generate_key()
            print(f"Generated new master key: {self.master_key.decode()}")
        
        self.cipher_suite = Fernet(self.master_key)

    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt an API key"""
        encrypted_key = self.cipher_suite.encrypt(api_key.encode())
        return b64encode(encrypted_key).decode()

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt an API key"""
        try:
            decrypted_key = self.cipher_suite.decrypt(b64decode(encrypted_key))
            return decrypted_key.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt API key: {e}")
