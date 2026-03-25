# main.py - Interface Gráfica Principal - SecureCrypt Pro
# UNISAL - Engenharia de Computação - 12G261 - 2026
# Projeto de Sistemas para Controle e Automação Robótica em Ambientes Distribuídos
# Tema: I - Confiabilidade e Segurança de Sistemas

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import time
from datetime import datetime

from crypto_sym  import CriptografiaSimetrica
from crypto_asym import CriptografiaAssimetrica
from stegano     import Esteganografia
from logger      import Logger

# ─── Paleta Catppuccin Mocha ─────────────────────────────────────────────────
C_BASE    = "#1e1e2e"
C_MANTLE  = "#181825"
C_CRUST   = "#11111b"
C_SURFACE = "#313244"
C_OVERLAY = "#45475a"
C_SUBTEXT = "#a6adc8"
C_TEXT    = "#cdd6f4"
C_BLUE    = "#89b4fa"
C_GREEN   = "#a6e3a1"
C_RED     = "#f38ba8"
C_YELLOW  = "#f9e2af"
C_MAUVE   = "#cba6f7"
C_PEACH   = "#fab387"
C_TEAL    = "#94e2d5"


class SecureCryptApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🔐 SecureCrypt Pro")
        self.root.geometry("980x700")
        self.root.minsize(820, 580)
        self.root.configure(bg=C_BASE)

        # Módulos
        self.logger = Logger()
        self.sym    = CriptografiaSimetrica()
        self.asym   = CriptografiaAssimetrica()
        self.steg   = Esteganografia()

        self._style()
        self._build_header()
        self._build_notebook()
        self._build_statusbar()

    # ─── ESTILOS ──────────────────────────────────────────────────────────────

    def _style(self):
        s = ttk.Style()
        s.theme_use("clam")

        s.configure("TFrame",       background=C_BASE)
        s.configure("TLabel",       background=C_BASE, foreground=C_TEXT,
                                    font=("Segoe UI", 9))
        s.configure("TEntry",       fieldbackground=C_SURFACE, foreground=C_TEXT,
                                    insertcolor=C_TEXT, borderwidth=0)
        s.configure("TCombobox",    fieldbackground=C_SURFACE, foreground=C_TEXT,
                                    selectbackground=C_BLUE, selectforeground=C_CRUST)
        s.map("TCombobox",          fieldbackground=[("readonly", C_SURFACE)])

        s.configure("TNotebook",            background=C_CRUST,  borderwidth=0)
        s.configure("TNotebook.Tab",        background=C_SURFACE, foreground=C_SUBTEXT,
                                            padding=[14, 7], font=("Segoe UI", 9, "bold"))
        s.map("TNotebook.Tab",
              background=[("selected", C_BLUE)],
              foreground=[("selected", C_CRUST)])

        s.configure("TLabelframe",          background=C_BASE,    foreground=C_BLUE,
                                            font=("Segoe UI", 9, "bold"), borderwidth=1)
        s.configure("TLabelframe.Label",    background=C_BASE,    foreground=C_BLUE,
                                            font=("Segoe UI", 9, "bold"))

        s.configure("Horizontal.TProgressbar",
                    troughcolor=C_SURFACE, background=C_BLUE, borderwidth=0)

        s.configure("Treeview",             background=C_SURFACE, foreground=C_TEXT,
                                            fieldbackground=C_SURFACE, rowheight=23,
                                            font=("Consolas", 8))
        s.configure("Treeview.Heading",     background=C_OVERLAY,  foreground=C_BLUE,
                                            font=("Segoe UI", 9, "bold"))
        s.map("Treeview",
              background=[("selected", C_BLUE)],
              foreground=[("selected", C_CRUST)])

        s.configure("TScrollbar",    background=C_OVERLAY, troughcolor=C_SURFACE, borderwidth=0)
        s.configure("TRadiobutton",  background=C_BASE, foreground=C_TEXT,
                                     font=("Segoe UI", 9))

    # ─── CABEÇALHO ────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=C_CRUST, pady=10)
        hdr.pack(fill="x")

        tk.Label(hdr, text="🔐  SecureCrypt Pro",
                 font=("Segoe UI", 17, "bold"), bg=C_CRUST, fg=C_BLUE).pack()
        tk.Label(hdr,
                 text="Criptografia Simétrica  •  Assimétrica  •  Esteganografia",
                 font=("Segoe UI", 8), bg=C_CRUST, fg=C_OVERLAY).pack()
        tk.Label(hdr,
                 text="UNISAL – Eng. de Computação – 12G261 – 7º Sem. 2026",
                 font=("Segoe UI", 7), bg=C_CRUST, fg="#45475a").pack()

    # ─── NOTEBOOK ─────────────────────────────────────────────────────────────

    def _build_notebook(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=12, pady=(8, 0))

        self.t_sim  = ttk.Frame(self.nb)
        self.t_asym = ttk.Frame(self.nb)
        self.t_steg = ttk.Frame(self.nb)
        self.t_log  = ttk.Frame(self.nb)

        self.nb.add(self.t_sim,  text="  🔒 Simétrica (AES-256)  ")
        self.nb.add(self.t_asym, text="  🗝️ Assimétrica (RSA-2048)  ")
        self.nb.add(self.t_steg, text="  👁️ Esteganografia  ")
        self.nb.add(self.t_log,  text="  📋 Log & Relatório  ")

        self._tab_sim()
        self._tab_asym()
        self._tab_steg()
        self._tab_log()

    # ─── STATUS BAR ───────────────────────────────────────────────────────────

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=C_CRUST, pady=4)
        bar.pack(fill="x", side="bottom")

        self._status_var = tk.StringVar(value="Pronto.")
        self._status_lbl = tk.Label(bar, textvariable=self._status_var,
                                     bg=C_CRUST, fg=C_OVERLAY,
                                     font=("Segoe UI", 8), anchor="w", padx=10)
        self._status_lbl.pack(side="left", fill="x", expand=True)

        tk.Label(bar,
                 text=f"v1.0  |  {datetime.now().strftime('%d/%m/%Y')}",
                 bg=C_CRUST, fg="#45475a", font=("Segoe UI", 8), padx=10).pack(side="right")

    def _status(self, msg: str, cor: str = None):
        self._status_var.set(msg)
        self._status_lbl.config(fg=cor or C_OVERLAY)
        self.root.update_idletasks()

    # ─── WIDGET HELPERS ───────────────────────────────────────────────────────

    def _btn(self, parent, text, cmd, bg=None, width=None, **kwargs):
        bg = bg or C_OVERLAY
        b = tk.Button(parent, text=text, command=cmd,
                      bg=bg, fg=C_TEXT, font=("Segoe UI", 9, "bold"),
                      relief="flat", activebackground=C_SURFACE,
                      activeforeground=C_TEXT, cursor="hand2",
                      pady=5, padx=10, bd=0, **kwargs)
        if width:
            b.config(width=width)
        b.bind("<Enter>", lambda e: b.config(bg=C_SURFACE))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _info_box(self, parent, texto: str):
        t = tk.Text(parent, width=26, bg=C_MANTLE, fg="#6c7086",
                    font=("Consolas", 8), relief="flat",
                    padx=8, pady=8, wrap="word", state="normal")
        t.pack(fill="both", expand=True)
        t.insert("end", texto)
        t.config(state="disabled")
        return t

    def _file_row(self, parent, var, label="📂 Arquivo", tipos=None, save=False):
        """Linha padrão com entry + botão de arquivo."""
        lf = ttk.LabelFrame(parent, text=label)
        lf.pack(fill="x", pady=(0, 8))
        row = ttk.Frame(lf)
        row.pack(fill="x", padx=8, pady=6)
        ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
        if save:
            cmd = lambda: self._save_as(var)
            txt = "Salvar como"
        else:
            ft = tipos or [("Todos", "*.*")]
            cmd = lambda ft=ft: self._open_file(var, ft)
            txt = "Buscar"
        self._btn(row, txt, cmd).pack(side="right", padx=(6, 0))
        return lf

    # ─── TAB: SIMÉTRICA ───────────────────────────────────────────────────────

    def _tab_sim(self):
        L = ttk.Frame(self.t_sim); L.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        R = ttk.Frame(self.t_sim); R.pack(side="right", fill="y", padx=(0, 12), pady=12)

        self.sym_in  = tk.StringVar()
        self.sym_out = tk.StringVar()
        self.sym_pwd = tk.StringVar()

        self._file_row(L, self.sym_in, "📂 Arquivo de Entrada")

        # Config
        cfg = ttk.LabelFrame(L, text="⚙️ Configuração")
        cfg.pack(fill="x", pady=(0, 8))
        ci = ttk.Frame(cfg); ci.pack(fill="x", padx=8, pady=6)
        ttk.Label(ci, text="Senha:").grid(row=0, column=0, sticky="w", pady=3)
        e = ttk.Entry(ci, textvariable=self.sym_pwd, show="●", width=32)
        e.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=3)
        ttk.Label(ci, text="Algoritmo:").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Combobox(ci, values=["AES-256-CBC"], state="readonly", width=29
                     ).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=3)
        ci.columnconfigure(1, weight=1)

        self._file_row(L, self.sym_out, "💾 Arquivo de Saída", save=True)

        self.sym_pb  = ttk.Progressbar(L, mode="indeterminate")
        self.sym_pb.pack(fill="x", pady=(2, 6))
        self.sym_res = tk.StringVar()
        ttk.Label(L, textvariable=self.sym_res, font=("Segoe UI", 9, "bold")).pack()

        bf = ttk.Frame(L); bf.pack(pady=8)
        self._btn(bf, "🔒  Criptografar",    self._sym_enc, bg="#1a3050", width=18).pack(side="left", padx=6)
        self._btn(bf, "🔓  Descriptografar", self._sym_dec, bg="#1a3a1a", width=18).pack(side="left", padx=6)

        self._info_box(R,
            "ℹ️  AES-256-CBC\n\n"
            "• Chave 256 bits\n"
            "• PBKDF2-HMAC-SHA256\n"
            "  100.000 iterações\n"
            "• Salt aleatório 16B\n"
            "• IV aleatório 16B\n"
            "• Padding PKCS7\n\n"
            "Suporta qualquer tipo:\n"
            "texto, imagem, áudio,\n"
            "vídeo, binários...\n\n"
            "⚠️  Guarde a senha!\n"
            "Sem ela é impossível\n"
            "recuperar os dados."
        )

    def _sym_run(self, enc: bool):
        entrada = self.sym_in.get().strip()
        saida   = self.sym_out.get().strip()
        senha   = self.sym_pwd.get()
        if not self._validar(entrada, saida, senha=senha): return

        def run():
            self.sym_pb.start(10); self.sym_res.set("")
            op = "Criptografando" if enc else "Descriptografando"
            self._status(f"{op} com AES-256-CBC...")
            try:
                if enc:
                    t, sz = self.sym.criptografar(entrada, saida, senha)
                    op_log = "ENCRYPT_SIM"
                else:
                    t, sz = self.sym.descriptografar(entrada, saida, senha)
                    op_log = "DECRYPT_SIM"
                self.sym_res.set(f"✅  Concluído em {t:.3f}s  |  {sz/1e6:.2f} MB")
                self.logger.registrar(op_log, entrada, saida, "AES-256-CBC", sz, t, "SUCESSO")
                self._status(f"Concluído em {t:.3f}s", C_GREEN)
                messagebox.showinfo("✅ Sucesso", f"Arquivo {'criptografado' if enc else 'descriptografado'}!\n\n"
                                    f"Tempo:   {t:.6f} s\nTamanho: {sz/1e6:.4f} MB")
            except Exception as err:
                self.sym_res.set(f"❌  {err}")
                self.logger.registrar("ENCRYPT_SIM" if enc else "DECRYPT_SIM",
                                      entrada, saida, "AES-256-CBC", 0, 0, "ERRO", str(err))
                self._status(f"Erro: {err}", C_RED)
                messagebox.showerror("❌ Erro", str(err))
            finally:
                self.sym_pb.stop()

        threading.Thread(target=run, daemon=True).start()

    def _sym_enc(self): self._sym_run(True)
    def _sym_dec(self): self._sym_run(False)

    # ─── TAB: ASSIMÉTRICA ─────────────────────────────────────────────────────

    def _tab_asym(self):
        L = ttk.Frame(self.t_asym); L.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        R = ttk.Frame(self.t_asym); R.pack(side="right", fill="y", padx=(0, 12), pady=12)

        self.asym_in      = tk.StringVar()
        self.asym_out     = tk.StringVar()
        self.asym_key     = tk.StringVar()
        self.asym_dir     = tk.StringVar(value=os.path.expanduser("~"))
        self.asym_prefix  = tk.StringVar(value="chave")
        self.asym_res_key = tk.StringVar()

        # Geração de chaves
        gp = ttk.LabelFrame(L, text="🗝️ Geração de Chaves RSA-2048")
        gp.pack(fill="x", pady=(0, 8))
        gi = ttk.Frame(gp); gi.pack(fill="x", padx=8, pady=6)

        ttk.Label(gi, text="Pasta:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(gi, textvariable=self.asym_dir, width=32).grid(row=0, column=1, sticky="ew", padx=(8,0))
        self._btn(gi, "Buscar", lambda: self._open_dir(self.asym_dir)).grid(row=0, column=2, padx=(6,0))

        ttk.Label(gi, text="Prefixo:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(gi, textvariable=self.asym_prefix, width=20).grid(row=1, column=1, sticky="w", padx=(8,0))

        self._btn(gi, "⚡  Gerar Par de Chaves", self._asym_gen,
                  bg="#3d2b00", width=22).grid(row=2, column=0, columnspan=3, pady=(8, 2))
        ttk.Label(gp, textvariable=self.asym_res_key,
                  font=("Consolas", 8), foreground=C_GREEN).pack(padx=8, pady=(0, 6))
        gi.columnconfigure(1, weight=1)

        self._file_row(L, self.asym_in, "📂 Arquivo de Entrada")
        self._file_row(L, self.asym_key, "🔑 Chave (.pem) – Pública p/ criptografar | Privada p/ decifrar",
                       tipos=[("PEM", "*.pem"), ("Todos", "*.*")])
        self._file_row(L, self.asym_out, "💾 Arquivo de Saída", save=True)

        self.asym_pb  = ttk.Progressbar(L, mode="indeterminate")
        self.asym_pb.pack(fill="x", pady=(2, 6))
        self.asym_res = tk.StringVar()
        ttk.Label(L, textvariable=self.asym_res, font=("Segoe UI", 9, "bold")).pack()

        bf = ttk.Frame(L); bf.pack(pady=8)
        self._btn(bf, "🔒  Criptografar",    self._asym_enc, bg="#1a3050", width=18).pack(side="left", padx=6)
        self._btn(bf, "🔓  Descriptografar", self._asym_dec, bg="#1a3a1a", width=18).pack(side="left", padx=6)

        self._info_box(R,
            "ℹ️  RSA-2048 Híbrido\n\n"
            "Cifragem:\n"
            "① Gera chave AES rand.\n"
            "② Cifra AES c/ RSA-OAEP\n"
            "③ Cifra dados c/ AES\n\n"
            "Decifragem:\n"
            "① Decifra chave AES\n"
            "   c/ chave privada RSA\n"
            "② Decifra dados c/ AES\n\n"
            "• Padding: OAEP/SHA-256\n"
            "• Suporta arquivos\n"
            "  de qualquer tamanho\n\n"
            "🔑 Gere as chaves antes\n"
            "de usar!\n\n"
            "📁 Guarde a chave\n"
            "privada em local seguro."
        )

    def _asym_gen(self):
        pasta  = self.asym_dir.get().strip()
        prefix = self.asym_prefix.get().strip() or "chave"
        if not pasta or not os.path.isdir(pasta):
            messagebox.showerror("Erro", "Selecione uma pasta válida."); return

        def run():
            self._status("Gerando par de chaves RSA-2048...")
            try:
                t0 = time.perf_counter()
                priv, pub = self.asym.gerar_chaves(pasta, prefix)
                t = time.perf_counter() - t0
                self.asym_res_key.set(f"✅  {os.path.basename(priv)}\n    {os.path.basename(pub)}")
                self.logger.registrar("GEN_KEYS", pasta, f"{priv}|{pub}", "RSA-2048", 0, t, "SUCESSO")
                self._status(f"Chaves RSA geradas em {t:.3f}s", C_GREEN)
                messagebox.showinfo("✅ Chaves Geradas",
                    f"Par de chaves RSA-2048 criado!\n\n"
                    f"🔒 Privada : {priv}\n"
                    f"🔓 Pública : {pub}\n\n"
                    f"Tempo: {t:.3f}s")
            except Exception as err:
                self.asym_res_key.set(f"❌ {err}")
                self._status(f"Erro: {err}", C_RED)
                messagebox.showerror("❌ Erro", str(err))

        threading.Thread(target=run, daemon=True).start()

    def _asym_run(self, enc: bool):
        entrada = self.asym_in.get().strip()
        chave   = self.asym_key.get().strip()
        saida   = self.asym_out.get().strip()
        if not self._validar(entrada, saida, chave=chave): return

        def run():
            self.asym_pb.start(10); self.asym_res.set("")
            self._status("Processando com RSA-2048 + AES-256...")
            try:
                if enc:
                    t, sz = self.asym.criptografar(entrada, saida, chave)
                    op = "ENCRYPT_ASYM"
                else:
                    t, sz = self.asym.descriptografar(entrada, saida, chave)
                    op = "DECRYPT_ASYM"
                self.asym_res.set(f"✅  Concluído em {t:.3f}s  |  {sz/1e6:.2f} MB")
                self.logger.registrar(op, entrada, saida, "RSA-2048+AES-256", sz, t, "SUCESSO")
                self._status(f"Concluído em {t:.3f}s", C_GREEN)
                messagebox.showinfo("✅ Sucesso",
                    f"Arquivo {'criptografado' if enc else 'descriptografado'}!\n\n"
                    f"Tempo:   {t:.6f} s\nTamanho: {sz/1e6:.4f} MB")
            except Exception as err:
                self.asym_res.set(f"❌  {err}")
                self.logger.registrar("ENCRYPT_ASYM" if enc else "DECRYPT_ASYM",
                                      entrada, saida, "RSA-2048+AES-256", 0, 0, "ERRO", str(err))
                self._status(f"Erro: {err}", C_RED)
                messagebox.showerror("❌ Erro", str(err))
            finally:
                self.asym_pb.stop()

        threading.Thread(target=run, daemon=True).start()

    def _asym_enc(self): self._asym_run(True)
    def _asym_dec(self): self._asym_run(False)

    # ─── TAB: ESTEGANOGRAFIA ──────────────────────────────────────────────────

    def _tab_steg(self):
        L = ttk.Frame(self.t_steg); L.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        R = ttk.Frame(self.t_steg); R.pack(side="right", fill="y", padx=(0, 12), pady=12)

        self.steg_tipo   = tk.StringVar(value="imagem")
        self.steg_cover  = tk.StringVar()
        self.steg_secret = tk.StringVar()
        self.steg_out    = tk.StringVar()

        # Tipo
        gp_tipo = ttk.LabelFrame(L, text="📎 Tipo de Mídia")
        gp_tipo.pack(fill="x", pady=(0, 8))
        rt = ttk.Frame(gp_tipo); rt.pack(fill="x", padx=8, pady=6)
        for lbl, val in [("🖼️ Imagem (PNG/BMP)", "imagem"),
                         ("🎵 Áudio (WAV)",       "audio"),
                         ("📝 Texto (TXT)",        "texto")]:
            tk.Radiobutton(rt, text=lbl, variable=self.steg_tipo, value=val,
                           bg=C_BASE, fg=C_TEXT, selectcolor=C_SURFACE,
                           activebackground=C_BASE, font=("Segoe UI", 9),
                           command=self._steg_update).pack(side="left", padx=10)

        # Cobertura
        gp_cov = ttk.LabelFrame(L, text="🖼️ Arquivo de Cobertura")
        gp_cov.pack(fill="x", pady=(0, 8))
        rc = ttk.Frame(gp_cov); rc.pack(fill="x", padx=8, pady=6)
        ttk.Entry(rc, textvariable=self.steg_cover).pack(side="left", fill="x", expand=True)
        self._btn(rc, "Buscar", self._steg_browse_cover).pack(side="right", padx=(6, 0))

        # Secreto
        self.steg_sec_lf = ttk.LabelFrame(L, text="🔐 Arquivo / Mensagem Secreta")
        self.steg_sec_lf.pack(fill="x", pady=(0, 8))
        rs = ttk.Frame(self.steg_sec_lf); rs.pack(fill="x", padx=8, pady=6)
        ttk.Entry(rs, textvariable=self.steg_secret).pack(side="left", fill="x", expand=True)
        self.steg_sec_btn = self._btn(rs, "Buscar",
                                       lambda: self._open_file(self.steg_secret))
        self.steg_sec_btn.pack(side="right", padx=(6, 0))

        # Saída
        gp_out = ttk.LabelFrame(L, text="💾 Arquivo de Saída")
        gp_out.pack(fill="x", pady=(0, 8))
        ro = ttk.Frame(gp_out); ro.pack(fill="x", padx=8, pady=6)
        ttk.Entry(ro, textvariable=self.steg_out).pack(side="left", fill="x", expand=True)
        self._btn(ro, "Salvar como", lambda: self._save_as(self.steg_out)).pack(side="right", padx=(6, 0))

        self.steg_pb  = ttk.Progressbar(L, mode="indeterminate")
        self.steg_pb.pack(fill="x", pady=(2, 6))
        self.steg_res = tk.StringVar()
        ttk.Label(L, textvariable=self.steg_res, font=("Segoe UI", 9, "bold")).pack()

        bf = ttk.Frame(L); bf.pack(pady=8)
        self._btn(bf, "👁️  Inserir",  self._steg_embed,   bg="#1a3050", width=16).pack(side="left", padx=6)
        self._btn(bf, "🔍  Extrair",  self._steg_extract, bg="#3a1e1e", width=16).pack(side="left", padx=6)

        self._info_box(R,
            "ℹ️  Esteganografia LSB\n\n"
            "🖼️ Imagem:\n"
            "• Modifica o bit menos\n"
            "  significativo de cada\n"
            "  canal RGB\n"
            "• Invisível ao olho\n"
            "• Saída sempre PNG\n\n"
            "🎵 Áudio WAV:\n"
            "• LSB nas amostras\n"
            "• Imperceptível ao\n"
            "  ouvido humano\n\n"
            "📝 Texto:\n"
            "• U+200B (bit 0) e\n"
            "  U+200C (bit 1)\n"
            "• Totalmente invisível\n"
            "  em editores comuns\n\n"
            "Para extrair, selecione\n"
            "o arquivo esteganografado\n"
            "no campo Cobertura."
        )

    def _steg_update(self):
        if self.steg_tipo.get() == "texto":
            self.steg_sec_lf.configure(text="✏️ Mensagem Secreta (escreva aqui)")
            self.steg_sec_btn.config(state="disabled")
        else:
            self.steg_sec_lf.configure(text="🔐 Arquivo Secreto")
            self.steg_sec_btn.config(state="normal")

    def _steg_browse_cover(self):
        t = self.steg_tipo.get()
        tipos = {"imagem": [("Imagens", "*.png *.bmp *.jpg *.jpeg"), ("Todos", "*.*")],
                 "audio":  [("WAV", "*.wav"), ("Todos", "*.*")],
                 "texto":  [("Texto", "*.txt"), ("Todos", "*.*")]}
        self._open_file(self.steg_cover, tipos.get(t, [("Todos", "*.*")]))

    def _steg_embed(self):
        cover  = self.steg_cover.get().strip()
        secret = self.steg_secret.get().strip()
        saida  = self.steg_out.get().strip()
        tipo   = self.steg_tipo.get()

        if not cover or not os.path.exists(cover):
            messagebox.showerror("Erro", "Selecione o arquivo de cobertura."); return
        if not secret:
            messagebox.showerror("Erro", "Informe o arquivo ou mensagem secreta."); return
        if tipo != "texto" and not os.path.exists(secret):
            messagebox.showerror("Erro", "Arquivo secreto não encontrado."); return
        if not saida:
            messagebox.showerror("Erro", "Informe o arquivo de saída."); return

        def run():
            self.steg_pb.start(10); self.steg_res.set("")
            try:
                if tipo == "imagem":
                    t, sz = self.steg.imagem_inserir(cover, secret, saida)
                    metodo = "LSB-Imagem"
                elif tipo == "audio":
                    t, sz = self.steg.audio_inserir(cover, secret, saida)
                    metodo = "LSB-Audio"
                else:
                    t, sz = self.steg.texto_inserir(cover, secret, saida)
                    metodo = "ZeroWidth-Texto"
                    sz = len(secret.encode())

                self.steg_res.set(f"✅  Inserido em {t:.3f}s")
                self.logger.registrar("STEG_EMBED", cover, saida, metodo, sz, t, "SUCESSO")
                self._status(f"Esteganografia concluída em {t:.3f}s", C_GREEN)
                messagebox.showinfo("✅ Sucesso", f"Dados inseridos!\n\nTempo: {t:.6f}s")
            except Exception as err:
                self.steg_res.set(f"❌  {err}")
                self.logger.registrar("STEG_EMBED", cover, saida, tipo, 0, 0, "ERRO", str(err))
                self._status(f"Erro: {err}", C_RED)
                messagebox.showerror("❌ Erro", str(err))
            finally:
                self.steg_pb.stop()

        threading.Thread(target=run, daemon=True).start()

    def _steg_extract(self):
        steg_file = self.steg_cover.get().strip()
        pasta     = os.path.dirname(self.steg_out.get().strip()) if self.steg_out.get().strip() else os.path.expanduser("~")
        tipo      = self.steg_tipo.get()

        if not steg_file or not os.path.exists(steg_file):
            messagebox.showerror("Erro", "Selecione o arquivo esteganografado no campo Cobertura."); return

        def run():
            self.steg_pb.start(10); self.steg_res.set("")
            try:
                if tipo == "imagem":
                    t, path = self.steg.imagem_extrair(steg_file, pasta)
                    self.steg_res.set(f"✅  Extraído: {os.path.basename(path)} ({t:.3f}s)")
                    messagebox.showinfo("✅ Extraído", f"Arquivo extraído:\n{path}\n\nTempo: {t:.6f}s")
                    metodo = "LSB-Imagem"
                elif tipo == "audio":
                    t, path = self.steg.audio_extrair(steg_file, pasta)
                    self.steg_res.set(f"✅  Extraído: {os.path.basename(path)} ({t:.3f}s)")
                    messagebox.showinfo("✅ Extraído", f"Arquivo extraído:\n{path}\n\nTempo: {t:.6f}s")
                    metodo = "LSB-Audio"
                else:
                    t, msg = self.steg.texto_extrair(steg_file)
                    self.steg_res.set(f"✅  Mensagem obtida ({t:.3f}s)")
                    messagebox.showinfo("✅ Mensagem Extraída",
                                        f"Mensagem secreta:\n\n{msg}\n\nTempo: {t:.6f}s")
                    path = steg_file
                    metodo = "ZeroWidth-Texto"

                self.logger.registrar("STEG_EXTRACT", steg_file, str(path),
                                      metodo, os.path.getsize(steg_file), t, "SUCESSO")
                self._status(f"Extração concluída em {t:.3f}s", C_GREEN)
            except Exception as err:
                self.steg_res.set(f"❌  {err}")
                self.logger.registrar("STEG_EXTRACT", steg_file, "", tipo, 0, 0, "ERRO", str(err))
                self._status(f"Erro: {err}", C_RED)
                messagebox.showerror("❌ Erro", str(err))
            finally:
                self.steg_pb.stop()

        threading.Thread(target=run, daemon=True).start()

    # ─── TAB: LOG ─────────────────────────────────────────────────────────────

    def _tab_log(self):
        # Toolbar
        tb = ttk.Frame(self.t_log); tb.pack(fill="x", padx=12, pady=(8, 4))
        self._btn(tb, "🔄 Atualizar",     self._log_refresh).pack(side="left", padx=(0, 4))
        self._btn(tb, "📄 Exportar CSV",  self._log_csv).pack(side="left", padx=4)
        self._btn(tb, "📝 Exportar TXT",  self._log_txt).pack(side="left", padx=4)
        self._btn(tb, "🗑️ Limpar Log",   self._log_clear, bg="#3a1e1e").pack(side="right")

        # Treeview
        cols = ("ID", "Timestamp", "Operação", "Arquivo", "Algoritmo", "MB", "Tempo(s)", "Status")
        tf = ttk.Frame(self.t_log); tf.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        self.tree = ttk.Treeview(tf, columns=cols, show="headings", height=18)
        for col, w in zip(cols, [38, 138, 115, 210, 115, 58, 68, 68]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, minwidth=35)

        sy = ttk.Scrollbar(tf, orient="vertical",   command=self.tree.yview)
        sx = ttk.Scrollbar(tf, orient="horizontal",  command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        tf.rowconfigure(0, weight=1); tf.columnconfigure(0, weight=1)

        self.log_stats = tk.StringVar()
        tk.Label(self.t_log, textvariable=self.log_stats,
                 bg=C_BASE, fg=C_OVERLAY, font=("Consolas", 8), anchor="w").pack(padx=12, anchor="w", pady=(0, 6))

        self._log_refresh()

    def _log_refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = self.logger.obter_todos()
        for r in rows:
            mb = f"{(r[6] or 0)/1e6:.3f}"
            tag = "ok" if r[8] == "SUCESSO" else ("err" if r[8] == "ERRO" else "")
            self.tree.insert("", "end",
                values=(r[0], r[1], r[2], os.path.basename(r[3] or ""),
                        r[5], mb, r[7], r[8]),
                tags=(tag,))
        self.tree.tag_configure("ok",  foreground=C_GREEN)
        self.tree.tag_configure("err", foreground=C_RED)
        s = self.logger.obter_estatisticas()
        self.log_stats.set(
            f"  Total: {s['total']}  |  ✅ {s['sucesso']}  |  ❌ {s['erro']}  "
            f"|  ⏱️ {s['tempo_total']}s total  |  DB: {self.logger.db_path}"
        )

    def _log_csv(self):
        p = filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV","*.csv")], title="Exportar CSV")
        if p:
            self.logger.exportar_csv(p)
            messagebox.showinfo("✅ Exportado", f"Log salvo em:\n{p}")

    def _log_txt(self):
        p = filedialog.asksaveasfilename(defaultextension=".txt",
            filetypes=[("Texto","*.txt")], title="Exportar Relatório TXT")
        if p:
            self.logger.exportar_txt(p)
            messagebox.showinfo("✅ Exportado", f"Relatório salvo em:\n{p}")

    def _log_clear(self):
        if messagebox.askyesno("Confirmar", "Deseja limpar todo o histórico de log?"):
            self.logger.limpar()
            self._log_refresh()
            self._status("Log limpo.", C_YELLOW)

    # ─── VALIDAÇÃO & HELPERS DE ARQUIVO ───────────────────────────────────────

    def _validar(self, entrada, saida, senha=None, chave=None) -> bool:
        if not entrada or not os.path.exists(entrada):
            messagebox.showerror("Erro", "Selecione um arquivo de entrada válido."); return False
        if not saida:
            messagebox.showerror("Erro", "Informe o arquivo de saída."); return False
        if senha is not None and not senha:
            messagebox.showerror("Erro", "Informe uma senha."); return False
        if chave is not None and (not chave or not os.path.exists(chave)):
            messagebox.showerror("Erro", "Selecione o arquivo de chave (.pem) válido."); return False
        return True

    def _open_file(self, var, tipos=None):
        p = filedialog.askopenfilename(filetypes=tipos or [("Todos","*.*")])
        if p: var.set(p)

    def _save_as(self, var):
        p = filedialog.asksaveasfilename()
        if p: var.set(p)

    def _open_dir(self, var):
        p = filedialog.askdirectory()
        if p: var.set(p)


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except Exception:
        pass
    app = SecureCryptApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
