
import time
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

    with open(selected_file + ".enc", "wb") as f:
        f.write(encrypted)

    log(f"Encrypt {selected_file} tempo={time.time()-start}")
    messagebox.showinfo("Sucesso", "Arquivo criptografado!")

def hide_text():
    img_path = filedialog.askopenfilename()
    text = entry_text.get()

    if not img_path or not text:
        messagebox.showerror("Erro", "Selecione imagem e digite texto")
        return

    img = Image.open(img_path)
    binary = ''.join(format(ord(i), '08b') for i in text) + '1111111111111110'
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
    img.save("output.png")

    log("Esteganografia realizada")
    messagebox.showinfo("Sucesso", "Texto escondido na imagem!")

# --- INTERFACE ---
root = Tk()
root.title("Sistema de Segurança")

Button(root, text="Selecionar Arquivo", command=choose_file).pack(pady=5)
label_file = Label(root, text="Nenhum arquivo")
label_file.pack()

Button(root, text="Criptografar Arquivo", command=encrypt_file).pack(pady=5)

Label(root, text="Texto para esconder na imagem:").pack()
entry_text = Entry(root, width=40)
entry_text.pack()

Button(root, text="Esconder texto em imagem", command=hide_text).pack(pady=5)

root.mainloop()
