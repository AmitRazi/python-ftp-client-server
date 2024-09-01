import tkinter as tk
from tkinter import ttk
from client import FTPClient


def position_window_main(instance):
    screen_width = instance.winfo_screenwidth()
    screen_height = instance.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (400 / 2))
    y_coordinate = int((screen_height / 2) - (200 / 2))
    instance.geometry(f"+{x_coordinate}+{y_coordinate}")


class WelcomeScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FTP")
        self.create_window()
        self.position_window()
        self.create_widgets()

    def create_window(self):
        self.geometry("200x150")

    def position_window(self):
        position_window_main(self)

    def create_widgets(self):
        connect_button = ttk.Button(self, text="Connect",
                                    command=self.on_connect)
        connect_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        welcome_label = ttk.Label(self, text="Welcome to our FTP server")
        welcome_label.place(relx=0.5, rely=0.30, anchor=tk.CENTER)

    def on_connect(self):
        self.destroy()
        MainApp()


class MainApp(tk.Tk):
    def __init__(self):
        self.client = FTPClient()
        super().__init__()
        self.title("FTP")
        self.stringvar = tk.StringVar()
        self.create_window()
        self.position_window()
        self.create_widgets()
        self.langs_select = None
        self.status_label = None

    def create_window(self):
        self.geometry("580x500")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

    def position_window(self):
        position_window_main(self)

    def create_widgets(self):
        self.create_listbox()
        self.create_buttons()
        self.create_status_label()

        self.mainloop()

    def create_listbox(self):
        file_list = self.client.handle_list_cmd("LIST")
        langs = tk.StringVar(value=file_list)

        self.langs_select = tk.Listbox(self, listvariable=langs, height=6)
        self.langs_select.grid(column=0, row=0, sticky="NSEW", padx=5, pady=5)
        self.langs_select.bind("<Double-Button-1>", self.handle_double_click)
        self.langs_select.grid_columnconfigure(0, weight=1)
        self.langs_select.grid_rowconfigure(0, weight=1)

    def create_buttons(self):
        buttons_frame = ttk.Frame(self, padding=10)
        buttons_frame.grid(column=0, row=1, sticky="EW")

        select_button = ttk.Button(buttons_frame, text="Select", command=self.handle_select_button)
        select_button.grid(column=0, row=0, padx=5)

        download_button = ttk.Button(buttons_frame, text="Download", command=self.handle_download_button)
        download_button.grid(column=2, row=0, padx=5)

        back_button = ttk.Button(buttons_frame, text="Back", command=self.handle_back_button)
        back_button.grid(column=1, row=0, padx=5)

        delete_button = ttk.Button(buttons_frame, text="Delete", command=self.handle_delete_button)
        delete_button.grid(column=3, row=0, padx=5)

        quit_button = ttk.Button(buttons_frame, text="Quit", command=self.handle_quit_button)
        quit_button.grid(column=6, row=0, padx=5)

        upload_button = ttk.Button(buttons_frame, text="Upload", command=self.handle_select_button)
        upload_button.grid(column=4, row=0, padx=5)

    def create_status_label(self):
        self.status_label = ttk.Label(self, textvariable=self.stringvar)
        self.stringvar.set("Connected")
        self.status_label.grid(column=0, row=3, columnspan=3, sticky="ew", padx=2, pady=2)

    def update_status_label(self, text):
        self.stringvar.set(text)

    def handle_select_button(self):
        selected_langs = self.langs_select.curselection()
        file_name = self.langs_select.get(selected_langs[0])[1:]
        char = self.langs_select.get(selected_langs[0])[:1]
        if char == '+':
            self.client.handle_cwd_cmd(command=f"CWD {file_name}")
            self.update_list()
        else:
            self.handle_download_button()

    def update_list(self):
        self.create_listbox()

    def handle_double_click(self, *arg):
        selected_langs = self.langs_select.curselection()
        if selected_langs:
            self.handle_select_button()
        else:
            self.update_status_label("No item selected")

    def handle_download_button(self, *arg):
        selected_file = self.langs_select.curselection()
        if selected_file:
            file_name = self.langs_select.get(selected_file[0])
            if file_name[:1] == '+':
                self.update_status_label("Can't download directories")
            else:
                file_name = file_name[1:]
                self.update_status_label("Downloading...")
                popup = tk.Toplevel(self)
                popup.title("Download in progress")
                self.client.handle_retr_cmd(f"RETR {file_name}")
                self.update_status_label(f"File: {file_name}, was successfully downloaded")
                popup.destroy()
        else:
            self.update_status_label("No item selected")

    def handle_back_button(self):
        self.client.handle_cwd_cmd(command=f"CWD ..")
        self.update_list()

    def handle_quit_button(self):
        self.client.handle_quit_cmd()
        self.destroy()

    def handle_delete_button(self):
        selected_file = self.langs_select.curselection()
        if selected_file:
            file_name = self.langs_select.get(selected_file[0])
            if file_name[:1] == '+':
                self.update_status_label("Can't delete directories")
            else:
                file_name = file_name[1:]
                self.update_status_label("Deleting...")
                self.update_status_label(self.client.handle_dele_cmd(f"DEL {file_name}"))
                self.update_list()
        else:
            self.update_status_label("No item selected")


if __name__ == '__main__':
    root = WelcomeScreen()
    root.mainloop()
