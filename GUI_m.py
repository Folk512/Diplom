import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import sys

root = tk.Tk()
root.title("Передача долей по TLS")
root.geometry("700x500")

output_text = tk.Text(root, wrap=tk.WORD, state=tk.DISABLED, bg="#1e1e1e", fg="#dcdcdc")
output_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

def append_output(text):
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, text)
    output_text.see(tk.END)
    output_text.config(state=tk.DISABLED)

def run_script_live(command_list):
    def target():
        append_output(f"\n[Запуск] {' '.join(command_list)}\n")
        try:
            process = subprocess.Popen(
                command_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                append_output(line)

            process.stdout.close()
            process.wait()
            append_output(f"[Завершено] Код: {process.returncode}\n")

        except Exception as e:
            append_output(f"[Ошибка запуска] {e}\n")

    threading.Thread(target=target, daemon=True).start()

def send_share():
    def send():
        ip = ip_entry.get()
        port = port_entry.get()
        file_path = file_entry.get()

        if not ip or not port or not file_path:
            messagebox.showwarning("Недостаточно данных", "Пожалуйста, укажите IP, порт и файл доли.")
            return

        run_script_live(["./Key_out", ip, port, file_path])
        send_win.destroy()

    send_win = tk.Toplevel(root)
    send_win.title("Отправка доли")

    tk.Label(send_win, text="IP сервера:").pack()
    ip_entry = tk.Entry(send_win)
    ip_entry.pack()

    tk.Label(send_win, text="Порт:").pack()
    port_entry = tk.Entry(send_win)
    port_entry.pack()

    tk.Label(send_win, text="Файл доли:").pack()
    file_entry = tk.Entry(send_win, width=40)
    file_entry.pack()

    def browse_file():
        file_path = filedialog.askopenfilename()
        if file_path:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)

    tk.Button(send_win, text="Обзор", command=browse_file).pack(pady=5)
    tk.Button(send_win, text="Отправить", command=send).pack(pady=10)

def receive_share():
    def start_receive():
        out_file = filename_entry.get()

        if not out_file:
            messagebox.showwarning("Недостаточно данных", "Укажите имя файла для сохранения.")
            return

        run_script_live(["./Key_in", out_file])
        recv_win.destroy()

    recv_win = tk.Toplevel(root)
    recv_win.title("Приём доли")

    tk.Label(recv_win, text="Файл для сохранения доли:").pack()
    filename_entry = tk.Entry(recv_win, width=40)
    filename_entry.pack(pady=5)

    tk.Button(recv_win, text="Начать приём", command=start_receive).pack(pady=10)


btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text=" Приём доли", command=receive_share, width=40).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text=" Отправка доли", command=send_share, width=40).grid(row=0, column=1, padx=10)

root.mainloop()
