# stegano.py - Esteganografia LSB para Imagens, Áudio e Texto
# SecureCrypt Pro - UNISAL Engenharia de Computação 2026

import os
import time
import struct
import wave


# ─── Helpers de bits ────────────────────────────────────────────────────────

def _bytes_para_bits(dados: bytes) -> str:
    """Converte bytes em string de bits '010101...'"""
    return "".join(f"{byte:08b}" for byte in dados)


def _bits_para_bytes(bits: str) -> bytes:
    """Converte string de bits em bytes."""
    resultado = bytearray()
    for i in range(0, len(bits), 8):
        bloco = bits[i:i + 8]
        if len(bloco) == 8:
            resultado.append(int(bloco, 2))
    return bytes(resultado)


def _montar_payload(arquivo_secreto: str) -> bytes:
    """
    Empacota nome do arquivo + conteúdo em um payload binário.
    Formato: [2 bytes: len(nome)] [nome UTF-8] [conteúdo]
    """
    with open(arquivo_secreto, "rb") as f:
        conteudo = f.read()
    nome = os.path.basename(arquivo_secreto).encode("utf-8")
    return struct.pack(">H", len(nome)) + nome + conteudo


def _desempacotar_payload(payload: bytes) -> tuple:
    """Retorna (nome_arquivo, conteudo)."""
    nome_len = struct.unpack(">H", payload[:2])[0]
    nome = payload[2:2 + nome_len].decode("utf-8")
    conteudo = payload[2 + nome_len:]
    return nome, conteudo


def _prefixar_tamanho(payload: bytes) -> bytes:
    """Prefixa payload com 4 bytes indicando seu tamanho."""
    return struct.pack(">I", len(payload)) + payload


def _extrair_tamanho_e_payload(samples: bytes) -> bytes:
    """Extrai 32 bits de LSB para obter tamanho, depois extrai payload."""
    # Lê os 32 primeiros LSBs → tamanho do payload
    bits_tam = "".join(str(samples[i] & 1) for i in range(32))
    tamanho = int(bits_tam, 2)

    if tamanho <= 0 or tamanho > len(samples) // 8:
        raise ValueError("Nenhum dado oculto encontrado ou arquivo corrompido.")

    bits_payload = "".join(str(samples[i] & 1) for i in range(32, 32 + tamanho * 8))
    return _bits_para_bytes(bits_payload)


# ─── Classe principal ────────────────────────────────────────────────────────

class Esteganografia:
    """
    Implementa esteganografia LSB para:
      • Imagens  (PNG/BMP) via Pillow + NumPy
      • Áudio    (WAV)     via módulo wave
      • Texto    (TXT)     via caracteres de largura zero (U+200B / U+200C)
    """

    # ── IMAGEM ────────────────────────────────────────────────────────────────

    def imagem_inserir(self, img_cobertura: str, arquivo_secreto: str,
                       img_saida: str) -> tuple:
        """
        Insere um arquivo qualquer em uma imagem usando LSB.
        Saída sempre em PNG (sem compressão com perda).

        Retorna: (tempo_seg, tamanho_cobertura_bytes)
        """
        try:
            from PIL import Image
            import numpy as np
        except ImportError:
            raise ImportError("Instale: pip install Pillow numpy")

        inicio = time.perf_counter()

        img = Image.open(img_cobertura).convert("RGB")
        arr = np.array(img, dtype=np.uint8)

        payload = _montar_payload(arquivo_secreto)
        dados   = _prefixar_tamanho(payload)
        bits    = _bytes_para_bits(dados)

        capacidade = arr.size  # total de canais RGB
        if len(bits) > capacidade:
            raise ValueError(
                f"Arquivo muito grande para esta imagem.\n"
                f"Capacidade: {capacidade // 8 - 4:,} bytes  |  "
                f"Necessário: {len(bits) // 8:,} bytes"
            )

        flat = arr.flatten()
        for i, bit in enumerate(bits):
            flat[i] = (int(flat[i]) & 0xFE) | int(bit)

        arr_mod = flat.reshape(arr.shape)
        Image.fromarray(arr_mod).save(img_saida, format="PNG")

        tempo = time.perf_counter() - inicio
        return tempo, os.path.getsize(img_cobertura)

    def imagem_extrair(self, img_esteganografada: str, pasta_saida: str) -> tuple:
        """
        Extrai arquivo oculto de uma imagem esteganografada.

        Retorna: (tempo_seg, caminho_arquivo_extraido)
        """
        try:
            from PIL import Image
            import numpy as np
        except ImportError:
            raise ImportError("Instale: pip install Pillow numpy")

        inicio = time.perf_counter()

        img = Image.open(img_esteganografada).convert("RGB")
        flat = np.array(img, dtype=np.uint8).flatten()

        payload = _extrair_tamanho_e_payload(flat)
        nome, conteudo = _desempacotar_payload(payload)

        caminho_saida = os.path.join(pasta_saida, nome)
        with open(caminho_saida, "wb") as f:
            f.write(conteudo)

        tempo = time.perf_counter() - inicio
        return tempo, caminho_saida

    # ── ÁUDIO WAV ─────────────────────────────────────────────────────────────

    def audio_inserir(self, wav_cobertura: str, arquivo_secreto: str,
                      wav_saida: str) -> tuple:
        """
        Insere arquivo oculto em áudio WAV modificando o LSB das amostras.

        Retorna: (tempo_seg, tamanho_cobertura_bytes)
        """
        inicio = time.perf_counter()

        with wave.open(wav_cobertura, "rb") as wf:
            params = wf.getparams()
            frames = wf.readframes(wf.getnframes())

        samples = bytearray(frames)

        payload = _montar_payload(arquivo_secreto)
        dados   = _prefixar_tamanho(payload)
        bits    = _bytes_para_bits(dados)

        if len(bits) > len(samples):
            raise ValueError(
                f"Arquivo muito grande para este WAV.\n"
                f"Capacidade: {len(samples) // 8 - 4:,} bytes  |  "
                f"Necessário: {len(bits) // 8:,} bytes"
            )

        for i, bit in enumerate(bits):
            samples[i] = (samples[i] & 0xFE) | int(bit)

        with wave.open(wav_saida, "wb") as wf_out:
            wf_out.setparams(params)
            wf_out.writeframes(bytes(samples))

        tempo = time.perf_counter() - inicio
        return tempo, os.path.getsize(wav_cobertura)

    def audio_extrair(self, wav_esteganografado: str, pasta_saida: str) -> tuple:
        """
        Extrai arquivo oculto de um WAV esteganografado.

        Retorna: (tempo_seg, caminho_arquivo_extraido)
        """
        inicio = time.perf_counter()

        with wave.open(wav_esteganografado, "rb") as wf:
            frames = wf.readframes(wf.getnframes())

        samples = bytearray(frames)
        payload = _extrair_tamanho_e_payload(samples)
        nome, conteudo = _desempacotar_payload(payload)

        caminho_saida = os.path.join(pasta_saida, nome)
        with open(caminho_saida, "wb") as f:
            f.write(conteudo)

        tempo = time.perf_counter() - inicio
        return tempo, caminho_saida

    # ── TEXTO ─────────────────────────────────────────────────────────────────

    # U+200B = zero-width space  → bit 0
    # U+200C = zero-width non-joiner → bit 1
    _BIT0 = "\u200B"
    _BIT1 = "\u200C"

    def texto_inserir(self, txt_cobertura: str, mensagem_secreta: str,
                      txt_saida: str) -> tuple:
        """
        Oculta uma mensagem de texto usando caracteres de largura zero.
        Os caracteres são invisíveis em editores convencionais.

        Retorna: (tempo_seg, tamanho_mensagem_bytes)
        """
        inicio = time.perf_counter()

        with open(txt_cobertura, "r", encoding="utf-8") as f:
            cobertura = f.read()

        msg_bytes = mensagem_secreta.encode("utf-8")
        dados     = _prefixar_tamanho(msg_bytes)
        bits      = _bytes_para_bits(dados)

        oculto = "".join(self._BIT0 if b == "0" else self._BIT1 for b in bits)

        # Insere após o primeiro espaço (ou no início)
        if " " in cobertura:
            pos = cobertura.index(" ") + 1
            resultado = cobertura[:pos] + oculto + cobertura[pos:]
        else:
            resultado = oculto + cobertura

        with open(txt_saida, "w", encoding="utf-8") as f:
            f.write(resultado)

        tempo = time.perf_counter() - inicio
        return tempo, len(msg_bytes)

    def texto_extrair(self, txt_esteganografado: str) -> tuple:
        """
        Extrai mensagem oculta de um arquivo de texto.

        Retorna: (tempo_seg, mensagem_str)
        """
        inicio = time.perf_counter()

        with open(txt_esteganografado, "r", encoding="utf-8") as f:
            conteudo = f.read()

        bits = ""
        for ch in conteudo:
            if ch == self._BIT0:
                bits += "0"
            elif ch == self._BIT1:
                bits += "1"

        if len(bits) < 32:
            raise ValueError("Nenhuma mensagem oculta encontrada neste arquivo.")

        tamanho = int(bits[:32], 2)
        bits_msg = bits[32:32 + tamanho * 8]

        if len(bits_msg) < tamanho * 8:
            raise ValueError("Dados incompletos — arquivo pode estar corrompido.")

        mensagem = _bits_para_bytes(bits_msg).decode("utf-8")
        tempo = time.perf_counter() - inicio
        return tempo, mensagem
