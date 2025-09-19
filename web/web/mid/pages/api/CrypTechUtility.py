def encrypt(plaintext: str, password: str) -> bytes:
    if not password:
        raise ValueError("You need a password")
    text_bytes = plaintext.encode("utf-8")
    pass_bytes = password.encode("utf-8")
    cipher = bytearray()
    for i in range(len(text_bytes)):
        cipher.append(text_bytes[i] ^ pass_bytes[i % len(pass_bytes)])
    return bytes(cipher)

def decrypt(cipher: bytes, password: str) -> str:
    if not password:
        raise ValueError("You need a password")
    pass_bytes = password.encode("utf-8")
    plain_bytes = bytearray()
    for i in range(len(cipher)):
        plain_bytes.append(cipher[i] ^ pass_bytes[i % len(pass_bytes)])
    return plain_bytes.decode("utf-8")

if __name__ == "__main__":
    choice = input("Select an option\n1. Encrypt\n2. Decrypt\n> ")
    if choice == "1":
        plaintext = input("Enter text: ")
        password = input("Enter password: ")
        cipher = encrypt(plaintext, password)
        print("Ciphertext (hex):", cipher.hex())
    elif choice == "2":
        password = input("Enter password: ")
        cipher_hex = input("Enter ciphertext (hex): ")
        try:
            cipher = bytes.fromhex(cipher_hex)
        except ValueError:
            raise SystemExit("Ciphertext must be a valid hex string.")
        decrypted = decrypt(cipher, password)
        print("Decrypted text: ", decrypted)
    else:
		print("Invalid choice")