# crypto_asym.py - Criptografia Assimétrica RSA-2048 (Criptografia Híbrida)
# SecureCrypt Pro - UNISAL Engenharia de Computação 2026

import os
import time
import struct

from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend


class CriptografiaAssimetrica:
    """
    Criptografia híbrida RSA-2048 + AES-256-CBC.

    Estratégia:
        • Gera chave AES aleatória de 256 bits por operação.
        • Cifra a chave AES com RSA-OAEP (chave pública).
        • Cifra o arquivo inteiro com AES-CBC.

    Formato do arquivo cifrado:
        [4 bytes: tamanho da chave RSA-cifrada]
        [N bytes: chave AES cifrada com RSA-OAEP]
        [16 bytes: IV do AES]
        [resto: dados cifrados com AES-256-CBC + PKCS7]
    """

    KEY_BITS = 2048
    ALGORITMO = "RSA-2048+AES-256-CBC"

    # ── Geração de chaves ────────────────────────────────────────────────────

    def gerar_chaves(self, pasta: str, prefixo: str = "chave") -> tuple:
        """
        Gera par de chaves RSA-2048 e salva como PEM.

        Retorna: (caminho_privada, caminho_publica)
        """
        priv = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.KEY_BITS,
            backend=default_backend()
        )
        pub = priv.public_key()

        priv_path = os.path.join(pasta, f"{prefixo}_privada.pem")
        pub_path  = os.path.join(pasta, f"{prefixo}_publica.pem")

        with open(priv_path, "wb") as f:
            f.write(priv.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(pub_path, "wb") as f:
            f.write(pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

        return priv_path, pub_path

    # ── Helpers de carregamento ──────────────────────────────────────────────

    @staticmethod
    def _carregar_publica(path: str):
        with open(path, "rb") as f:
            return serialization.load_pem_public_key(f.read(), backend=default_backend())

    @staticmethod
    def _carregar_privada(path: str):
        with open(path, "rb") as f:
            return serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )

    # ── Operações principais ─────────────────────────────────────────────────

    def criptografar(self, arquivo_entrada: str, arquivo_saida: str,
                     chave_publica_path: str) -> tuple:
        """
        Cifra arquivo com criptografia híbrida RSA+AES.

        Retorna: (tempo_seg, tamanho_original_bytes)
        """
        inicio = time.perf_counter()
        tamanho = os.path.getsize(arquivo_entrada)

        # 1. Gerar chave AES e IV aleatórios
        aes_key = os.urandom(32)   # 256 bits
        iv      = os.urandom(16)   # 128 bits

        # 2. Cifrar chave AES com RSA-OAEP
        chave_pub = self._carregar_publica(chave_publica_path)
        aes_key_enc = chave_pub.encrypt(
            aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 3. Cifrar arquivo com AES-256-CBC
        with open(arquivo_entrada, "rb") as f:
            dados = f.read()

        padder = PKCS7(128).padder()
        dados_padded = padder.update(dados) + padder.finalize()

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        enc = cipher.encryptor()
        dados_enc = enc.update(dados_padded) + enc.finalize()

        # 4. Gravar arquivo de saída
        with open(arquivo_saida, "wb") as f:
            f.write(struct.pack(">I", len(aes_key_enc)))   # 4 bytes: tamanho da chave RSA
            f.write(aes_key_enc)                            # chave AES cifrada com RSA
            f.write(iv)                                     # IV do AES
            f.write(dados_enc)                              # dados cifrados com AES

        tempo = time.perf_counter() - inicio
        return tempo, tamanho

    def descriptografar(self, arquivo_entrada: str, arquivo_saida: str,
                        chave_privada_path: str) -> tuple:
        """
        Decifra arquivo com criptografia híbrida RSA+AES.

        Retorna: (tempo_seg, tamanho_cifrado_bytes)
        """
        inicio = time.perf_counter()
        tamanho = os.path.getsize(arquivo_entrada)

        chave_priv = self._carregar_privada(chave_privada_path)

        with open(arquivo_entrada, "rb") as f:
            rsa_key_len = struct.unpack(">I", f.read(4))[0]
            aes_key_enc = f.read(rsa_key_len)
            iv          = f.read(16)
            dados_enc   = f.read()

        # 1. Decifrar chave AES com RSA privada
        aes_key = chave_priv.decrypt(
            aes_key_enc,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 2. Decifrar dados com AES-CBC
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        dec = cipher.decryptor()
        dados_padded = dec.update(dados_enc) + dec.finalize()

        unpadder = PKCS7(128).unpadder()
        dados_orig = unpadder.update(dados_padded) + unpadder.finalize()

        with open(arquivo_saida, "wb") as f:
            f.write(dados_orig)

        tempo = time.perf_counter() - inicio
        return tempo, tamanho
