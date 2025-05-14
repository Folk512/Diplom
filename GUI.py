import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import threading
import os

SCRIPTS = {
    "Создание и шифрование БД": "Coder.exe",
    "Разделение и отправка долей": "SplitKeys.exe",
    "Сбор и восстановление ключа": "key_collect.exe",
    "Расшифровка базы данных": "Decrypt.exe",
    "Шифрование готовой БД": "ReadyDB.exe"
}

root = tk.Tk()
root.title("Система шифрования БД")
root.geometry("400x350")

output_win = tk.Toplevel(root)
output_win.title("Результат выполнения скриптов")
output_text = tk.Text(output_win, wrap=tk.WORD)
output_text.pack(expand=True, fill=tk.BOTH)
output_text.insert(tk.END, "--- Ожидание запуска ---\n")
output_text.config(state=tk.DISABLED)

def append_output(message):
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, message + "\n")
    output_text.see(tk.END)
    output_text.config(state=tk.DISABLED)

def run_splitkeys():
    def submit():
        ip_list = ip_entry.get()
        total_shares = total_entry.get()
        threshold = threshold_entry.get()

        if not ip_list or not total_shares or not threshold:
            messagebox.showwarning("Поля не заполнены", "Пожалуйста, заполните все поля.")
            return

        input_window.destroy()

        def target():
            try:
                append_output("--- Запуск SplitKeys.exe ---")
                args = [SCRIPTS["Разделение и отправка долей"], ip_list, total_shares, threshold]
                result = subprocess.run(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                append_output(result.stdout)
                append_output(result.stderr)
            except Exception as e:
                messagebox.showerror("Ошибка запуска", f"Не удалось запустить SplitKeys:\n{e}")

        threading.Thread(target=target).start()

    input_window = tk.Toplevel(root)
    input_window.title("Параметры для SplitKeys")
    input_window.geometry("350x200")

    tk.Label(input_window, text="IP-адреса (через запятую):").pack(pady=5)
    ip_entry = tk.Entry(input_window, width=40)
    ip_entry.pack()

    tk.Label(input_window, text="Общее количество долей:").pack(pady=5)
    total_entry = tk.Entry(input_window, width=10)
    total_entry.pack()

    tk.Label(input_window, text="Необходимое количество для восстановления:").pack(pady=5)
    threshold_entry = tk.Entry(input_window, width=10)
    threshold_entry.pack()

    tk.Button(input_window, text="Запустить", command=submit).pack(pady=10)

def run_script(script_path, db_path=None):
    def target():
        try:
            append_output(f"--- Запуск {script_path} ---")
            if db_path:
                result = subprocess.run(
                    [script_path, db_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
            else:
                result = subprocess.run(
                    [script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
            append_output(result.stdout)
            append_output(result.stderr)
        except Exception as e:
            messagebox.showerror("Ошибка запуска", f"Не удалось запустить скрипт:\n{e}")

    threading.Thread(target=target).start()

def run_readydb():
    db_path = filedialog.askopenfilename(title="Выберите базу данных для шифрования",
                                         filetypes=[("SQLite DB", "*.db *.sqlite *.sqlite3"), ("Все файлы", "*.*")])
    if not db_path:
        append_output("Операция отменена пользователем.")
        return

    run_script(SCRIPTS["Шифрование готовой БД"], db_path=db_path)

tk.Label(root, text="Выберите операцию:", font=("Helvetica", 14)).pack(pady=10)

tk.Button(root, text="Шифрование готовой БД", font=("Helvetica", 12), width=35,
          command=run_readydb).pack(pady=5)

for label, path in SCRIPTS.items():
    if label == "Разделение и отправка долей":
        tk.Button(root, text=label, font=("Helvetica", 12), width=35,
                  command=run_splitkeys).pack(pady=5)
    elif label != "Шифрование готовой БД":
        tk.Button(root, text=label, font=("Helvetica", 12), width=35,
                  command=lambda p=path: run_script(p)).pack(pady=5)

tk.Label(root, text="by mortis", font=("Helvetica", 8, "italic")).pack(side=tk.BOTTOM, pady=5)

root.mainloop()
