import os

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

def get_decrypted_env_value(encryption_key: str, encrypted_env_var_name: str, fallback_env_var_name: str = None) -> str:
    """
    Retrieve and decrypt an environment variable. If decryption fails or the encrypted 
    variable is not set, falls back to the unencrypted environment variable.
    """
    
    encrypted_val = os.environ.get(encrypted_env_var_name)
    
    if encrypted_val and encryption_key and Fernet:
        try:
            cipher_suite = Fernet(encryption_key.encode('utf-8'))
            return cipher_suite.decrypt(encrypted_val.encode('utf-8')).decode('utf-8')
        except Exception as e:
            print(f"Warning: Failed to decrypt {encrypted_env_var_name} - {e}")
            
    if fallback_env_var_name:
        return os.environ.get(fallback_env_var_name)
        
    return None