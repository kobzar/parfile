# app.py
import customtkinter as ct
from parfile.gui.tab_main import TabFiles, TabFilesButtonsTop, TabFilesButtonsBottom
from parfile.gui.tab_config import TabConfig
from parfile.misc import cfg, log, ROOT


class Parfile(ct.CTk):
    def __init__(self):
        super().__init__()

        self.height = cfg.App.height
        self.width = cfg.App.width
        self.pos_x = cfg.App.pos_x
        self.pos_y = cfg.App.pos_y
        self.title("RAR Files Parser")
        self.geometry(f"{self.width}x{self.height}+{self.pos_x}+{self.pos_y}")
        # Make Tab view resizable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Tabs view
        self.tabs = ct.CTkTabview(master=self)
        self.tabs.add("Files")
        self.tabs.add("Configuration")
        self.tabs.grid(padx=20, pady=20, sticky="nsew")

        # Auto close app after 10 seconds (optional)
        # self.after(25000, self.quit)
        # NOTE: Open 2 ntab by default
        # self.tabs.set("Configuration")

        # Configure grid for Files tab
        self.tabs.tab("Files").grid_columnconfigure(0, weight=1)
        self.tabs.tab("Files").grid_rowconfigure(0, weight=1)

        # Create scrollable checkbox frame
        self.files_view = TabFiles(master=self.tabs.tab("Files"))
        self.files_view.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Create top buttons for the files tab
        self.files_view_buttons = TabFilesButtonsTop(master=self.tabs.tab("Files"), tab_files_instance=self.files_view)
        self.files_view_buttons.grid(row=0, column=1, padx=5, pady=5, sticky="n")

        # Create bottom buttons for the files tab
        self.files_view_bottom = TabFilesButtonsBottom(master=self)
        self.files_view_bottom.grid(row=1, column=0, padx=5, pady=5, sticky="nse")

        # Create configuration view
        self.config_view = TabConfig(master=self.tabs.tab("Configuration"))
        self.config_view.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")


def start():
    # Create config if not exists
    config = ROOT / "config.ini"
    if not config.is_file():
        cfg.save()
        log.info("Created config file")
    ct.set_appearance_mode("dark")
    app = Parfile()
    app.mainloop()


if __name__ == "__main__":
    # Start app
    start()
