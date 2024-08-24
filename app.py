import customtkinter as ctk
from tkinter import filedialog, messagebox, Listbox
import subprocess
import re
import os
from query_data import query_rag
from populate_database import main as populate_database, clear_database

class App():
    def __init__(self):

        self.root = ctk.CTk() # initialize main window

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # set window title and dimensions
        self.root.title("AI for PDFs")

        self.root.geometry("640x720+500+50") # basing off of 1280x720; but halving the width

        # mainframe setup
        self.mainframe = ctk.CTkFrame(self.root)
        self.mainframe.pack(fill="both", expand=True)

        # configure grid for mainframe
        self.mainframe.grid_columnconfigure(0, weight=5) # only 1 column
        self.mainframe.grid_rowconfigure(0, weight=5) # title
        self.mainframe.grid_rowconfigure(1, weight=5) # status 
        self.mainframe.grid_rowconfigure(2, weight=5) # server control buttons
        self.mainframe.grid_rowconfigure(3, weight=5) # document list
        self.mainframe.grid_rowconfigure(4, weight=5) # document management buttons
        self.mainframe.grid_rowconfigure(5, weight=5) # ask a question button
        self.mainframe.grid_rowconfigure(6, weight=150) # response display

        # title label
        self.text = ctk.CTkLabel(self.mainframe, text="Interact with your PDFs using Ollama AI", font=("Segoe UI Semilight", 20))
        self.text.grid(row=0, column=0, pady=5, padx=5, sticky="n")

        # status label
        self.status_label = ctk.CTkLabel(self.mainframe, text="Ollama Inactive", font=("Segoe UI", 16), text_color="tomato")
        self.status_label.grid(row=1, column=0, pady=5, padx=5, sticky="n")

        # buttons for ollama server control
        self.button_frame = ctk.CTkFrame(self.mainframe)
        self.button_frame.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="n")

        self.run_button = ctk.CTkButton(self.button_frame, text="Run Ollama Server", command=self.run_ollama)
        self.run_button.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        self.stop_button = ctk.CTkButton(self.button_frame, text="Stop Ollama Server", command=self.stop_ollama, state="disabled")
        self.stop_button.grid(row=2, column=1, pady=5, padx=5, sticky="e")

        # document frame
        self.docs_frame = ctk.CTkFrame(self.mainframe)
        self.docs_frame.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="n")

        self.docs_label = ctk.CTkLabel(self.docs_frame, text="Documents in Data Folder", font=("Segoe UI", 14))
        self.docs_label.grid(row=0, column=0, columnspan=2, pady=5, padx=5)

        # listbox to display documents
        self.docs_listbox = Listbox(self.docs_frame, height=5, width=60, font=("Segoe UI", 12), background="gray35", foreground="white")
        self.docs_listbox.grid(row=1, column=0, columnspan=2, pady=5, padx=5)

        # buttons to manage documents
        self.add_doc_button = ctk.CTkButton(self.docs_frame, text="Add Document", command=self.add_document)
        self.add_doc_button.grid(row=2, column=0, pady=5, padx=5)

        self.remove_doc_button = ctk.CTkButton(self.docs_frame, text="Remove Selected", command=self.remove_document)
        self.remove_doc_button.grid(row=2, column=1, pady=5, padx=5)

        # button to update chroma db
        self.update_chroma_button = ctk.CTkButton(self.docs_frame, text="Update Chroma DB", command=self.update_chroma)
        self.update_chroma_button.grid(row=3, column=0, columnspan=2, pady=5, padx=5)

        # button to clear chroma db
        self.clear_chroma_button = ctk.CTkButton(self.docs_frame, text="Clear Chroma DB", command=self.clear_chroma)
        self.clear_chroma_button.grid(row=4, column=0, columnspan=2, pady=5, padx=5)

        # entry area for prompt
        self.prompt_entry = ctk.CTkEntry(self.mainframe, width=600, placeholder_text="Ask me about your PDFs...")
        self.prompt_entry.grid(row=4, column=0, columnspan=2, pady=5, padx=5, sticky="n")

        # ask button
        self.ask_button = ctk.CTkButton(self.mainframe, text="Ask", command=self.ask_llm, state="disabled")
        self.ask_button.grid(row=5, column=0, columnspan=2, pady=5, padx=5, sticky="n")

        # response text area
        self.response_text = ctk.CTkTextbox(self.mainframe, wrap="word", height=250, width=600)
        self.response_text.grid(row=6, column=0, columnspan=2, pady=5, padx=5, sticky="n")
        

        # server process variable
        self.server_process = None

        # load documents initially
        self.load_documents()

        # main call
        self.root.mainloop()

    def load_documents(self):
        # load list of documents from data folder to listbox
        data_folder = 'data'  # path to folder where documents are stored
        self.docs_listbox.delete(0, ctk.END)  # clear whole listbox
        if os.path.exists(data_folder):
            for doc in os.listdir(data_folder):
                self.docs_listbox.insert(ctk.END, doc)  # insert document names into listbox
        else:
            messagebox.showerror("Error", f"The folder '{data_folder}' does not exist.")


    def add_document(self):
        # added new document to data folder
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                # copy selected file to data folder
                data_folder = 'data'
                os.makedirs(data_folder, exist_ok=True)  # ensure folder exists
                destination = os.path.join(data_folder, os.path.basename(file_path))
                with open(file_path, 'rb') as fsrc, open(destination, 'wb') as fdst:
                    fdst.write(fsrc.read())
                self.load_documents()  # reload documents list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add document: {e}")

    def remove_document(self):
        # remove selected document from data folder
        selected_index = self.docs_listbox.curselection()
        if selected_index:
            selected_doc = self.docs_listbox.get(selected_index)
            data_folder = 'data'
            doc_path = os.path.join(data_folder, selected_doc)
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{selected_doc}'?"):
                try:
                    os.remove(doc_path)
                    self.load_documents()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete document: {e}")


    def update_chroma(self):
        # update chroma db with documents in data folder
        try:
            populate_database()  # from populate_database.py
            messagebox.showinfo("Success", "Chroma database updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update Chroma database: {e}")
    
    def clear_chroma(self):
        # clear documents from chroma db
        try:
            clear_database()
            messagebox.showinfo("Success", "Documents cleared from Chroma DB successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear documents from Chroma DB: {e}")

    def run_ollama(self):
        if not self.server_process:
            # command to start the ollama server
            command = ["ollama", "serve"]
            self.server_process = subprocess.Popen(command)

            # ppdate status variable
            self.status_label.configure(text="Ollama Running", text_color="lawn green")
            self.run_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.ask_button.configure(state="normal")  # enable ask button when ollama is running

    def stop_ollama(self):
        if self.server_process:
            # powershell command to stop ollama server
            command = ["powershell", "-Command", "Get-Process | Where-Object {$_.ProcessName -like '*ollama*'} | Stop-Process"]
            subprocess.run(command, shell=True)
            self.server_process = None

            # update status variable
            self.status_label.configure(text="Ollama Inactive", text_color="tomato")
            self.run_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.ask_button.configure(state="disabled")  # disable ask button when ollama not running

    def ask_llm(self):
        prompt = self.prompt_entry.get()

        # validate prompt to only allow letters, numbers, and basic punctuation to avoid possible injections
        if re.match(r'^[a-zA-Z0-9\s]+$', prompt):
            self.response_text.delete("1.0", ctk.END)  # clear previous response
            result = query_rag(prompt)  # send query to ollama model
            self.response_text.insert(ctk.END, result)
        else:
            self.response_text.delete("1.0", ctk.END)
            self.response_text.insert(ctk.END, "Invalid prompt, no special characters allowed")

if __name__ == "__main__":
    App()
