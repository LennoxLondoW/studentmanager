import hashlib
class hash:
    def create_hash(self,input : str) -> str:
        # Encode the input string into bytes
        input_bytes = input.encode('utf-8')

        # Create a SHA-256 hash object
        sha256_hash = hashlib.sha256()
        
        # Update the hash object with the password bytes
        sha256_hash.update(input_bytes)
        
        # Get the hexadecimal representation of the hashed password
        hashed_input = sha256_hash.hexdigest()
        
        return hashed_input