
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA1
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad


class CryptoFile:
    text = "u8DurGE2"
    text1 = "6BBGizHE"

    @classmethod
    def _derive_key_iv(cls):
        salt = cls.text1.encode("utf-8")
        key_iv = PBKDF2(
            cls.text,
            salt,
            dkLen=32,  # 16 for key + 16 for IV, in one continuous derivation
            count=1000,
            prf=lambda p, s: HMAC.new(p, s, SHA1).digest(),
        )
        return key_iv[:16], key_iv[16:32]

    @classmethod
    def decrypt(cls, encrypted_data: bytes) -> bytes:
        key, iv = cls._derive_key_iv()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(encrypted_data)
        return unpad(decrypted_data, AES.block_size)

    @classmethod
    def encrypt(cls, plaintext_data: bytes) -> bytes:
        key, iv = cls._derive_key_iv()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded = pad(plaintext_data, AES.block_size)
        return cipher.encrypt(padded)
