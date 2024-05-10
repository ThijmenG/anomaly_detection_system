import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # for styled widgets
from load_file import load_file  # Assuming load_file function is in load_file.py

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("File Loader")
        self.configure(bg="#f0f0f0")

        self.create_widgets()
        self.center_window(600, 300)

    def center_window(self, width=300, height=200):
        # Update the geometry of the window for center placement
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 12), padding=10)
        style.configure('TLabel', background="#f0f0f0", font=('Helvetica', 12))

        frame = ttk.Frame(self, padding="30 15 30 15")
        frame.pack(fill=tk.BOTH, expand=True)

        load_button = ttk.Button(frame, text="Load File", command=self.load_and_display_file)
        load_button.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)

        self.filepath_entry = tk.Entry(frame, font=('Helvetica', 10), state='readonly', readonlybackground='#f0f0f0', fg='black')
        self.filepath_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)

        run_button = ttk.Button(frame, text="Run Model", command=self.run_model, state=tk.DISABLED)
        run_button.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        self.run_button = run_button  # keep a reference

    def load_and_display_file(self):
        filepath, df = load_file()
        if filepath:
            self.filepath_entry.configure(state='normal')
            self.filepath_entry.delete(0, tk.END)
            self.filepath_entry.insert(0, filepath)
            self.filepath_entry.configure(state='readonly')
            self.run_button.config(state=tk.NORMAL)

    def run_model(self):
        messagebox.showinfo("Success", "Model run successfully.")