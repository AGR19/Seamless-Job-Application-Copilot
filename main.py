import tkinter as tk
from tkinter import filedialog

def upload_file():
    file_path = filedialog.askopenfilename(title="Upload Resume", filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx"), ("All files", "*.*")])
    if file_path:
        file_label.config(text=f"Selected: {file_path}")

def submit_link():
    link = link_entry.get()
    link_label.config(text=f"Submitted Link: {link}")

# Create the main window
root = tk.Tk()
root.title("Seamless Job Application Copilot")

# Upload button
upload_button = tk.Button(root, text="Upload Resume", command=upload_file)
upload_button.pack(pady=10)

# Display selected file
file_label = tk.Label(root, text="No file selected")
file_label.pack()

# Entry for link
link_entry = tk.Entry(root, width=40)
link_entry.pack(pady=10)

submit_button = tk.Button(root, text="Submit Link", command=submit_link)
submit_button.pack()

# Display submitted link
link_label = tk.Label(root, text="No link submitted")
link_label.pack()

root.mainloop()
