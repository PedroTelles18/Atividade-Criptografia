# crypto_sym.py - Criptografia Simétrica AES-256-CBC
# SecureCrypt Pro - UNISAL Engenharia de Computação 2026

import os
import time

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend


SALT_SIZE  = 16        # 128 bits
IV_SIZE    = 16        # 128 bits
KEY_SIZE   = 32        # 256 bits
ITERATIONS = 100_000   # PBKDF2 rounds


def _derivar_chave(senha: str, salt: bytes) -> bytes:
    """Deriva chave AES-256 a partir de senha usando PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(senha.encode("utf-8"))


class CriptografiaSimetrica:
    """
    Criptografia simétrica AES-256-CBC com derivação de chave PBKDF2.

    Formato do arquivo cifrado:
        [SALT  16 bytes]
        [IV    16 bytes]
        [DADOS cifrados com padding PKCS7]
    """

    ALGORITMO = "AES-256-CBC"

    def criptografar(self, arquivo_entrada: str, arquivo_saida: str, senha: str) -> tuple:
        """
        Cifra um arquivo com AES-256-CBC.

        Retorna: (tempo_seg, tamanho_original_bytes)
        """
        inicio = time.perf_counter()

        tamanho = os.path.getsize(arquivo_entrada)

        # Gerar salt e IV aleatórios
        salt = os.urandom(SALT_SIZE)
        iv   = os.urandom(IV_SIZE)
        chave = _derivar_chave(senha, salt)

        # Ler dados originais
        with open(arquivo_entrada, "rb") as f:
            dados = f.read()

        # Aplicar padding PKCS7
        padder = padding.PKCS7(128).padder()
        dados_padded = padder.update(dados) + padder.finalize()

        # Cifrar
        cipher = Cipher(algorithms.AES(chave), modes.CBC(iv), backend=default_backend())
        enc = cipher.encryptor()
        dados_cifrados = enc.update(dados_padded) + enc.finalize()

        # Gravar: salt | iv | dados_cifrados
        with open(arquivo_saida, "wb") as f:
            f.write(salt)
            f.write(iv)
            f.write(dados_cifrados)

        tempo = time.perf_counter() - inicio
        return tempo, tamanho

    def descriptografar(self, arquivo_entrada: str, arquivo_saida: str, senha: str) -> tuple:
        """
        Decifra um arquivo cifrado com AES-256-CBC.

        Retorna: (tempo_seg, tamanho_cifrado_bytes)
        """
        inicio = time.perf_counter()

        tamanho = os.path.getsize(arquivo_entrada)

        with open(arquivo_entrada, "rb") as f:
            salt         = f.read(SALT_SIZE)
            iv           = f.read(IV_SIZE)
            dados_cifrados = f.read()

        chave = _derivar_chave(senha, salt)

        # Decifrar
        cipher = Cipher(algorithms.AES(chave), modes.CBC(iv), backend=default_backend())
        dec = cipher.decryptor()
        dados_padded = dec.update(dados_cifrados) + dec.finalize()

        # Remover padding
        unpadder = padding.PKCS7(128).unpadder()
        dados_orig = unpadder.update(dados_padded) + unpadder.finalize()

        with open(arquivo_saida, "wb") as f:
            f.write(dados_orig)

        tempo = time.perf_counter() - inicio
        return tempo, tamanho
