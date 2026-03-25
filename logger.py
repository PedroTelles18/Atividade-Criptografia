# logger.py - Sistema de Log com SQLite
# SecureCrypt Pro - UNISAL Engenharia de Computação 2026

import sqlite3
import csv
import os
from datetime import datetime


class Logger:
    """Registra todas as operações em banco SQLite e permite exportação."""

    COLUNAS = [
        "ID", "Timestamp", "Operação", "Arquivo Entrada",
        "Arquivo Saída", "Algoritmo", "Tamanho (bytes)",
        "Tempo (s)", "Status", "Detalhes"
    ]

    def __init__(self, db_path: str = "securecrypt_log.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS operacoes (
                    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp           TEXT    NOT NULL,
                    operacao            TEXT    NOT NULL,
                    arquivo_entrada     TEXT,
                    arquivo_saida       TEXT,
                    algoritmo           TEXT,
                    tamanho_bytes       INTEGER DEFAULT 0,
                    tempo_processamento REAL    DEFAULT 0,
                    status              TEXT,
                    detalhes            TEXT
                )
            """)

    def registrar(
        self,
        operacao: str,
        arquivo_entrada: str,
        arquivo_saida: str,
        algoritmo: str,
        tamanho_bytes: int,
        tempo_processamento: float,
        status: str,
        detalhes: str = ""
    ):
        """Insere um registro no banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO operacoes
                   (timestamp, operacao, arquivo_entrada, arquivo_saida,
                    algoritmo, tamanho_bytes, tempo_processamento, status, detalhes)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    operacao,
                    arquivo_entrada,
                    arquivo_saida,
                    algoritmo,
                    int(tamanho_bytes),
                    round(float(tempo_processamento), 6),
                    status,
                    detalhes
                )
            )

    def obter_todos(self) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT * FROM operacoes ORDER BY id DESC")
            return cur.fetchall()

    def obter_estatisticas(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM operacoes").fetchone()[0]
            sucesso = conn.execute(
                "SELECT COUNT(*) FROM operacoes WHERE status='SUCESSO'"
            ).fetchone()[0]
            erro = conn.execute(
                "SELECT COUNT(*) FROM operacoes WHERE status='ERRO'"
            ).fetchone()[0]
            tempo_total = conn.execute(
                "SELECT SUM(tempo_processamento) FROM operacoes WHERE status='SUCESSO'"
            ).fetchone()[0] or 0.0
        return {
            "total": total,
            "sucesso": sucesso,
            "erro": erro,
            "tempo_total": round(tempo_total, 4)
        }

    def exportar_csv(self, path: str):
        rows = self.obter_todos()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.COLUNAS)
            writer.writerows(rows)

    def exportar_txt(self, path: str):
        rows = self.obter_todos()
        stats = self.obter_estatisticas()
        sep = "=" * 80
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{sep}\n")
            f.write("RELATÓRIO DE OPERAÇÕES - SecureCrypt Pro\n")
            f.write(f"UNISAL - Engenharia de Computação - 12G261\n")
            f.write(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{sep}\n\n")
            f.write(f"RESUMO ESTATÍSTICO\n")
            f.write(f"  Total de operações : {stats['total']}\n")
            f.write(f"  Bem-sucedidas      : {stats['sucesso']}\n")
            f.write(f"  Com erro           : {stats['erro']}\n")
            f.write(f"  Tempo total (s)    : {stats['tempo_total']}\n\n")
            f.write(f"{sep}\n\n")
            for row in rows:
                f.write(f"  ID               : {row[0]}\n")
                f.write(f"  Timestamp        : {row[1]}\n")
                f.write(f"  Operação         : {row[2]}\n")
                f.write(f"  Arquivo Entrada  : {row[3]}\n")
                f.write(f"  Arquivo Saída    : {row[4]}\n")
                f.write(f"  Algoritmo        : {row[5]}\n")
                tam = row[6] or 0
                f.write(f"  Tamanho          : {tam:,} bytes  ({tam/1024/1024:.2f} MB)\n")
                f.write(f"  Tempo            : {row[7]} s\n")
                f.write(f"  Status           : {row[8]}\n")
                if row[9]:
                    f.write(f"  Detalhes         : {row[9]}\n")
                f.write(f"  {'-'*40}\n")

    def limpar(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM operacoes")
