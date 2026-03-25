# 🔐 SecureCrypt Pro

**UNISAL – Engenharia de Computação – 12G261 – 7º Semestre Noturno 2026**
Projeto de Sistemas para Controle e Automação Robótica em Ambientes Distribuídos
*Tema I: Confiabilidade e Segurança de Sistemas*

---

## Funcionalidades

| Recurso | Detalhe |
|---|---|
| Criptografia Simétrica | AES-256-CBC com PBKDF2-HMAC-SHA256 (100k rounds) |
| Criptografia Assimétrica | RSA-2048 com criptografia híbrida (RSA cifra chave AES) |
| Esteganografia Imagem | LSB (Least Significant Bit) em arquivos PNG/BMP |
| Esteganografia Áudio | LSB nas amostras de arquivos WAV |
| Esteganografia Texto | Caracteres de largura zero (U+200B / U+200C) |
| Log de Operações | SQLite com timestamp, algoritmo, tempo, tamanho e status |
| Exportação de Relatório | CSV e TXT detalhado com estatísticas |
| Benchmark | Script para medir performance com arquivos de 10 MB a 500 MB |
| Interface Gráfica | Tkinter dark theme (Catppuccin Mocha) com abas |

---

## Pré-requisitos

- Python 3.9+
- Sistema operacional: Windows, Linux ou macOS

## Instalação

```bash
pip install -r requirements.txt
```

## Executar

```bash
python main.py
```

## Benchmark de Performance

```bash
python benchmark.py
```
Os resultados são salvos na pasta `benchmark_resultados/`.

---

## Estrutura dos Arquivos

```
securecrypt/
├── main.py          # Interface gráfica principal (Tkinter)
├── crypto_sym.py    # Criptografia AES-256-CBC
├── crypto_asym.py   # Criptografia RSA-2048 híbrida
├── stegano.py       # Esteganografia (imagem, áudio, texto)
├── logger.py        # Sistema de log SQLite
├── benchmark.py     # Script de análise de performance
└── requirements.txt
```

---

## Detalhes Técnicos

### Criptografia Simétrica – AES-256-CBC

Formato do arquivo cifrado:
```
[16 bytes: SALT aleatório]
[16 bytes: IV aleatório]
[N bytes: dados cifrados com PKCS7 padding]
```

A chave AES é derivada da senha via **PBKDF2-HMAC-SHA256** com 100.000 iterações,
garantindo resistência a ataques de força bruta.

### Criptografia Assimétrica – RSA-2048 Híbrida

Formato do arquivo cifrado:
```
[4 bytes: tamanho da chave AES cifrada]
[N bytes: chave AES de 256 bits cifrada com RSA-OAEP/SHA-256]
[16 bytes: IV do AES]
[M bytes: dados cifrados com AES-256-CBC + PKCS7]
```

Essa abordagem permite cifrar arquivos de qualquer tamanho com RSA.

### Esteganografia LSB

- **Imagem**: altera o bit menos significativo de cada canal RGB, suportando
  capacidade máxima de `(largura × altura × 3) / 8 − 4` bytes.
- **Áudio WAV**: altera o LSB de cada byte de amostra, suportando
  capacidade de `total_amostras / 8 − 4` bytes.
- **Texto**: insere caracteres Unicode invisíveis (U+200B = bit 0,
  U+200C = bit 1) após o primeiro espaço do texto.

### Log de Operações

Todas as operações são registradas em banco SQLite (`securecrypt_log.db`):
- Timestamp da operação
- Tipo de operação (ENCRYPT_SIM, DECRYPT_SIM, ENCRYPT_ASYM, etc.)
- Caminho dos arquivos de entrada e saída
- Algoritmo utilizado
- Tamanho do arquivo em bytes
- Tempo de processamento em segundos
- Status (SUCESSO ou ERRO) e detalhes

---

## Segurança

> ⚠️ Este software é um projeto acadêmico. Para uso em produção,
> recomenda-se auditoria de segurança e uso de bibliotecas homologadas.

---

*SecureCrypt Pro © 2026 – UNISAL Americana*
