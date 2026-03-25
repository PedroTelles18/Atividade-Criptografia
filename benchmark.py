#!/usr/bin/env python3
# benchmark.py - Análise de Performance dos Algoritmos
# SecureCrypt Pro - UNISAL Engenharia de Computação 2026
#
# Gera arquivos de 10MB a 500MB e mede o tempo de execução
# de cada algoritmo, produzindo relatório CSV e TXT.

import os
import sys
import time
import csv
import random
import tempfile
from datetime import datetime

from crypto_sym  import CriptografiaSimetrica
from crypto_asym import CriptografiaAssimetrica
from stegano     import Esteganografia

# ─── Configurações ────────────────────────────────────────────────────────────

TAMANHOS_MB = [10, 50, 100, 200, 500]   # Tamanhos dos arquivos de teste
SENHA_TESTE  = "BenchmarkSenha@2026#SecureCrypt"
REPETICOES   = 1                          # Repetições por tamanho (aumente para média)

OUTPUT_DIR   = "benchmark_resultados"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def gerar_arquivo_aleatorio(path: str, tamanho_mb: int):
    """Gera arquivo de bytes aleatórios com o tamanho indicado."""
    chunk = 1024 * 1024  # 1 MB
    with open(path, "wb") as f:
        for _ in range(tamanho_mb):
            f.write(random.randbytes(chunk))


def formatar_tempo(seg: float) -> str:
    if seg < 1:
        return f"{seg*1000:.1f} ms"
    return f"{seg:.3f} s"


def throughput_mb_s(tamanho_mb: float, tempo: float) -> str:
    if tempo <= 0:
        return "—"
    return f"{tamanho_mb / tempo:.1f} MB/s"


# ─── Benchmark ────────────────────────────────────────────────────────────────

def rodar_benchmark():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="securecrypt_bench_")

    sym  = CriptografiaSimetrica()
    asym = CriptografiaAssimetrica()

    # Gerar par de chaves RSA (uma vez)
    print("Gerando par de chaves RSA-2048...")
    priv_path, pub_path = asym.gerar_chaves(tmp, "bench")
    print(f"  Privada : {priv_path}")
    print(f"  Pública : {pub_path}\n")

    resultados = []

    for tam_mb in TAMANHOS_MB:
        tam_bytes = tam_mb * 1024 * 1024
        print(f"{'='*60}")
        print(f" Testando {tam_mb} MB")
        print(f"{'='*60}")

        arq_orig = os.path.join(tmp, f"original_{tam_mb}mb.bin")
        print(f"  Gerando arquivo aleatório de {tam_mb} MB...", end=" ", flush=True)
        gerar_arquivo_aleatorio(arq_orig, tam_mb)
        print("OK")

        for rep in range(1, REPETICOES + 1):
            # ── AES-256-CBC Cifragem ──────────────────────────────────────
            arq_enc_sym = os.path.join(tmp, f"enc_sym_{tam_mb}mb.bin")
            t0 = time.perf_counter()
            tempo_enc_sym, _ = sym.criptografar(arq_orig, arq_enc_sym, SENHA_TESTE)
            print(f"  [AES] Encrypt : {formatar_tempo(tempo_enc_sym):>10}  ({throughput_mb_s(tam_mb, tempo_enc_sym)})")

            # ── AES-256-CBC Decifragem ────────────────────────────────────
            arq_dec_sym = os.path.join(tmp, f"dec_sym_{tam_mb}mb.bin")
            tempo_dec_sym, _ = sym.descriptografar(arq_enc_sym, arq_dec_sym, SENHA_TESTE)
            print(f"  [AES] Decrypt : {formatar_tempo(tempo_dec_sym):>10}  ({throughput_mb_s(tam_mb, tempo_dec_sym)})")

            # ── RSA+AES Cifragem ──────────────────────────────────────────
            arq_enc_asym = os.path.join(tmp, f"enc_asym_{tam_mb}mb.bin")
            tempo_enc_asym, _ = asym.criptografar(arq_orig, arq_enc_asym, pub_path)
            print(f"  [RSA] Encrypt : {formatar_tempo(tempo_enc_asym):>10}  ({throughput_mb_s(tam_mb, tempo_enc_asym)})")

            # ── RSA+AES Decifragem ────────────────────────────────────────
            arq_dec_asym = os.path.join(tmp, f"dec_asym_{tam_mb}mb.bin")
            tempo_dec_asym, _ = asym.descriptografar(arq_enc_asym, arq_dec_asym, priv_path)
            print(f"  [RSA] Decrypt : {formatar_tempo(tempo_dec_asym):>10}  ({throughput_mb_s(tam_mb, tempo_dec_asym)})\n")

            resultados.append({
                "tam_mb":         tam_mb,
                "repeticao":      rep,
                "aes_enc_s":      round(tempo_enc_sym,  6),
                "aes_dec_s":      round(tempo_dec_sym,  6),
                "rsa_enc_s":      round(tempo_enc_asym, 6),
                "rsa_dec_s":      round(tempo_dec_asym, 6),
                "aes_enc_mbps":   round(tam_mb / tempo_enc_sym,  2),
                "aes_dec_mbps":   round(tam_mb / tempo_dec_sym,  2),
                "rsa_enc_mbps":   round(tam_mb / tempo_enc_asym, 2),
                "rsa_dec_mbps":   round(tam_mb / tempo_dec_asym, 2),
            })

    # ─── Exportar resultados ──────────────────────────────────────────────────
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")

    # CSV
    csv_path = os.path.join(OUTPUT_DIR, f"benchmark_{agora}.csv")
    campos = ["tam_mb", "repeticao",
              "aes_enc_s", "aes_dec_s",
              "rsa_enc_s", "rsa_dec_s",
              "aes_enc_mbps", "aes_dec_mbps",
              "rsa_enc_mbps", "rsa_dec_mbps"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(resultados)

    # TXT
    txt_path = os.path.join(OUTPUT_DIR, f"benchmark_{agora}.txt")
    sep = "=" * 72
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"{sep}\n")
        f.write("RELATÓRIO DE BENCHMARK DE DESEMPENHO - SecureCrypt Pro\n")
        f.write("UNISAL - Engenharia de Computação - 12G261 - 2026\n")
        f.write(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{sep}\n\n")
        f.write(f"{'Tam(MB)':>8}  {'AES-Enc(s)':>12}  {'AES-Dec(s)':>12}  "
                f"{'RSA-Enc(s)':>12}  {'RSA-Dec(s)':>12}  "
                f"{'AES(MB/s)':>10}  {'RSA(MB/s)':>10}\n")
        f.write(f"{'-'*8}  {'-'*12}  {'-'*12}  {'-'*12}  {'-'*12}  {'-'*10}  {'-'*10}\n")
        for r in resultados:
            f.write(
                f"{r['tam_mb']:>8}  {r['aes_enc_s']:>12.6f}  {r['aes_dec_s']:>12.6f}  "
                f"{r['rsa_enc_s']:>12.6f}  {r['rsa_dec_s']:>12.6f}  "
                f"{r['aes_enc_mbps']:>10.1f}  {r['rsa_enc_mbps']:>10.1f}\n"
            )
        f.write(f"\n{sep}\n")
        f.write("ANÁLISE\n")
        f.write(f"{sep}\n\n")
        f.write("• AES-256-CBC é muito mais rápido que RSA para grandes volumes,\n")
        f.write("  pois é um algoritmo simétrico executado inteiramente em software.\n\n")
        f.write("• RSA-2048 no modo híbrido tem desempenho próximo ao AES,\n")
        f.write("  pois a parte lenta (RSA) opera apenas na chave AES (256 bits),\n")
        f.write("  e o restante dos dados é cifrado com AES.\n\n")
        f.write("• O gargalo do RSA híbrido está na derivação/operação de chaves,\n")
        f.write("  enquanto no AES puro está na derivação PBKDF2 (100k iterações).\n\n")
        f.write("• Throughput AES cresce de forma linear com o tamanho do arquivo.\n")

    print(f"\n{'='*60}")
    print(f"  Benchmark concluído!")
    print(f"  CSV : {csv_path}")
    print(f"  TXT : {txt_path}")
    print(f"{'='*60}")
    return csv_path, txt_path


if __name__ == "__main__":
    rodar_benchmark()
