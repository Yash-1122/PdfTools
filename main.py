import os
import PyPDF2
import subprocess
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES

class PDFEditor:
    def __init__(self, root):
        self.window = root
        self.window.geometry("800x600")
        self.window.title('PDF Editor')
        #root.iconbitmap("pdfe.ico")

        # Style configuration
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 12), padding=10)
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 12))
        style.configure('TText', font=('Helvetica', 12))

        # Create labels and buttons
        self.create_label("PDF Editor", 20, 'bold').pack(pady=10)

        self.extract_text_button = self.create_button("Extract Text from PDF", self.extract_text)
        self.extract_text_button.pack(pady=10)

        self.save_text_button = self.create_button("Save Extracted Text", self.save_text)
        self.save_text_button.pack(pady=10)

        self.merge_pdfs_button = self.create_button("Merge PDFs", self.merge_pdfs)
        self.merge_pdfs_button.pack(pady=10)

        self.split_pdf_button = self.create_button("Split PDF", self.split_pdf)
        self.split_pdf_button.pack(pady=10)

        self.preview_pdf_button = self.create_button("Preview PDF", self.preview_pdf)
        self.preview_pdf_button.pack(pady=10)

        self.password_button = self.create_button("Add/Remove Password", self.password_protect)
        self.password_button.pack(pady=10)

        self.search_button = self.create_button("Search Text", self.search_text)
        self.search_button.pack(pady=10)

        self.text_area = Text(self.window, wrap='word', height=10, font=('Helvetica', 12))
        self.text_area.pack(pady=10, padx=10, fill=BOTH, expand=True)

        self.progress = ttk.Progressbar(self.window, orient=HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=10)

        self.window.drop_target_register(DND_FILES)
        self.window.dnd_bind('<<Drop>>', self.drop)

    def create_button(self, text, command):
        return ttk.Button(self.window, text=text, command=command)

    def create_label(self, text, size=12, weight='normal'):
        return ttk.Label(self.window, text=text, font=('Helvetica', size, weight))

    def extract_text(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                reader = PyPDF2.PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                self.text_area.delete(1.0, END)
                self.text_area.insert(1.0, text)
                messagebox.showinfo("Success", "Text extracted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract text: {e}")

    def save_text(self):
        text = self.text_area.get(1.0, END)
        if text.strip():
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(text)
                messagebox.showinfo("Success", "Text saved successfully!")
        else:
            messagebox.showwarning("Warning", "No text to save!")

    def merge_pdfs(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if files:
            self.progress['value'] = 0
            self.window.update_idletasks()
            try:
                merger = PyPDF2.PdfMerger()
                for i, pdf in enumerate(files):
                    merger.append(pdf)
                    self.progress['value'] += (100 / len(files))
                    self.window.update_idletasks()
                output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
                if output_path:
                    merger.write(output_path)
                    merger.close()
                    messagebox.showinfo("Success", "PDFs merged successfully!")
                    self.progress['value'] = 0
            except Exception as e:
                messagebox.showerror("Error", f"Failed to merge PDFs: {e}")

    def split_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                reader = PyPDF2.PdfReader(file_path)
                for i, page in enumerate(reader.pages):
                    writer = PyPDF2.PdfWriter()
                    writer.add_page(page)
                    output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=f"page_{i+1}.pdf")
                    if output_path:
                        with open(output_path, 'wb') as output_pdf:
                            writer.write(output_pdf)
                messagebox.showinfo("Success", "PDF split successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to split PDF: {e}")

    def preview_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                if os.name == 'nt':  # For Windows
                    os.startfile(file_path)
                elif os.name == 'posix':  # For macOS and Linux
                    subprocess.call(('open', file_path) if sys.platform == 'darwin' else ('xdg-open', file_path))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to preview PDF: {e}")

    def password_protect(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                reader = PyPDF2.PdfReader(file_path)
                writer = PyPDF2.PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                password = simpledialog.askstring("Password", "Enter password:")
                if password:
                    writer.encrypt(password)
                    output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
                    if output_path:
                        with open(output_path, 'wb') as output_pdf:
                            writer.write(output_pdf)
                    messagebox.showinfo("Success", "Password added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add password: {e}")

    def search_text(self):
        search_term = simpledialog.askstring("Search", "Enter text to search:")
        if search_term:
            text = self.text_area.get(1.0, END)
            occurrences = text.lower().count(search_term.lower())
            messagebox.showinfo("Search Results", f"Found {occurrences} occurrences of '{search_term}'")

    def drop(self, event):
        files = self.window.tk.splitlist(event.data)
        for file in files:
            if file.endswith('.pdf'):
                self.text_area.insert(END, f"Dropped file: {file}\n")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFEditor(root)
    root.mainloop()
