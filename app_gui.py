import time
import os
from tkinter import *
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet
from PIL import Image

log_file = "log.txt"

def log(msg):
    with open(log_file, "a") as f:
        f.write(f"{time.ctime()} - {msg}\n")

selected_file = None

def choose_file():
    global selected_file
    selected_file = filedialog.askopenfilename()
    label_file.config(text=selected_file)

# ---------------- CRIPTOGRAFAR ----------------
def encrypt_file():
    if not selected_file:
        messagebox.showerror("Erro", "Selecione um arquivo")
        return

    start = time.time()
    key = Fernet.generate_key()
    fernet = Fernet(key)

    with open(selected_file, "rb") as f:
        data = f.read()

    encrypted = fernet.encrypt(data)

    # pasta inicial = mesma do arquivo original
    initial_dir = os.path.dirname(selected_file)

    # salvar arquivo criptografado
    save_path = filedialog.asksaveasfilename(
        initialdir=initial_dir,
        defaultextension=".enc",
        filetypes=[("Arquivo criptografado", "*.enc")]
    )

    if not save_path:
        messagebox.showwarning("Aviso", "Salvamento cancelado")
        return

    with open(save_path, "wb") as f:
        f.write(encrypted)

    # salvar chave
    key_path = filedialog.asksaveasfilename(
        initialdir=initial_dir,
        defaultextension=".key",
        filetypes=[("Chave", "*.key")]
    )

    if key_path:
        with open(key_path, "wb") as k:
            k.write(key)
    else:
        messagebox.showwarning("Aviso", "Chave não salva!")

    log(f"Encrypt {selected_file} -> {save_path} tempo={time.time()-start}")
    messagebox.showinfo("Sucesso", "Arquivo criptografado!")

# ---------------- DESCRIPTOGRAFAR ----------------
def decrypt_file():
    enc_path = filedialog.askopenfilename(title="Selecione arquivo criptografado")
    key_path = filedialog.askopenfilename(title="Selecione a chave (.key)")

    if not enc_path or not key_path:
        messagebox.showerror("Erro", "Selecione arquivo e chave")
        return

    try:
        with open(key_path, "rb") as k:
            key = k.read()

        fernet = Fernet(key)

        with open(enc_path, "rb") as f:
            encrypted_data = f.read()

        decrypted = fernet.decrypt(encrypted_data)

        initial_dir = os.path.dirname(enc_path)

        save_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            title="Salvar arquivo descriptografado"
        )

        if save_path:
            with open(save_path, "wb") as f:
                f.write(decrypted)

            log(f"Decrypt {enc_path} -> {save_path}")
            messagebox.showinfo("Sucesso", "Arquivo descriptografado!")
        else:
            messagebox.showwarning("Aviso", "Salvamento cancelado")

    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao descriptografar: {e}")

# ---------------- ESTEGANOGRAFIA (ESCONDER) ----------------
def hide_text():
    img_path = filedialog.askopenfilename()
    text = entry_text.get()

    if not img_path or not text:
        messagebox.showerror("Erro", "Selecione imagem e digite texto")
        return

    img = Image.open(img_path)
    
    # marcador de fim consistente
    end_marker = '11111110'

    binary = ''.join(format(ord(i), '08b') for i in text) + end_marker
    pixels = list(img.getdata())

    new_pixels = []
    idx = 0

    for pixel in pixels:
        if idx < len(binary):
            r = pixel[0] & ~1 | int(binary[idx])
            idx += 1
            new_pixels.append((r, pixel[1], pixel[2]))
        else:
            new_pixels.append(pixel)

    img.putdata(new_pixels)

    initial_dir = os.path.dirname(img_path)

    save_path = filedialog.asksaveasfilename(
        initialdir=initial_dir,
        defaultextension=".png",
        filetypes=[("Imagem PNG", "*.png")]
    )

    if save_path:
        img.save(save_path)
        log(f"Esteganografia -> {save_path}")
        messagebox.showinfo("Sucesso", "Texto escondido na imagem!")
    else:
        messagebox.showwarning("Aviso", "Salvamento cancelado")

# ---------------- ESTEGANOGRAFIA (REVELAR) ----------------
def reveal_text():
    img_path = filedialog.askopenfilename()

    if not img_path:
        messagebox.showerror("Erro", "Selecione uma imagem")
        return

    img = Image.open(img_path)
    pixels = list(img.getdata())

    binary = ""

    for pixel in pixels:
        binary += str(pixel[0] & 1)

    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]

    text = ""
    for c in chars:
        if c == '11111110':  # mesmo marcador usado ao esconder
            break
        text += chr(int(c, 2))

    messagebox.showinfo("Texto encontrado", text)

# ---------------- INTERFACE ----------------
root = Tk()
root.title("Sistema de Segurança")

Button(root, text="Selecionar Arquivo", command=choose_file).pack(pady=5)
label_file = Label(root, text="Nenhum arquivo")
label_file.pack()

Button(root, text="Criptografar Arquivo", command=encrypt_file).pack(pady=5)
Button(root, text="Descriptografar Arquivo", command=decrypt_file).pack(pady=5)

Label(root, text="Texto para esconder na imagem:").pack()
entry_text = Entry(root, width=40)
entry_text.pack()

Button(root, text="Esconder texto em imagem", command=hide_text).pack(pady=5)
Button(root, text="Revelar texto da imagem", command=reveal_text).pack(pady=5)

root.mainloop()
