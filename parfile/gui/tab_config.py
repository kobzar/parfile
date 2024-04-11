from icecream import ic
import customtkinter as ct
from tkinter import filedialog
from misc import cfg, ROOT, log


class TabConfig(ct.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.font = ("Arial", 18)

        # Add mask field
        self.mask_descr = "txt,pdf,jpg (by default: all files)"
        self.files_mask_lbl = ct.CTkLabel(self, text="Extracted files mask:", text_color="light blue", font=self.font)
        self.mask = ct.StringVar(value=cfg.App.mask_ext, name="mask")
        self.files_mask_data = ct.CTkEntry(self, width=350, font=self.font)
        # Use description if mask isnt set
        if not cfg.App.mask_ext:
            self.files_mask_data.configure(textvariable=None, placeholder_text=self.mask_descr)
        else:
            self.files_mask_data.configure(textvariable=self.mask)

        self.files_mask_btn = ct.CTkButton(self, text="Save", command=self.save_mask)
        # Nask grid
        self.files_mask_lbl.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.files_mask_data.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.files_mask_btn.grid(row=1, column=1, padx=10, pady=10, sticky="e")

        # Create config field for select path where archive files is placed
        self.arj_path = ct.StringVar(value=cfg.App.data, name="arj")
        self.arj_path_lbl = ct.CTkLabel(self, text="Path to rar files:", text_color="light blue", font=self.font)
        self.arj_path_data = ct.CTkEntry(self, width=350, textvariable=self.arj_path, font=self.font)
        self.arj_path_btn = ct.CTkButton(self, text="Browse", command=lambda: self.browse_path(self.arj_path))
        # arj grid
        self.arj_path_lbl.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.arj_path_data.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.arj_path_btn.grid(row=3, column=1, padx=10, pady=10, sticky="e")

        # Create config field for select exract files by mask
        self.tmp_path = ct.StringVar(value=cfg.Paths.tmp, name="tmp")
        self.tmp_path_lbl = ct.CTkLabel(self, text="Path to unrar files:", text_color="light blue", font=self.font)
        self.tmp_path_data = ct.CTkEntry(self, width=350, textvariable=self.tmp_path, font=self.font)
        self.tmp_path_btn = ct.CTkButton(self, text="Browse", command=lambda: self.browse_path(self.tmp_path))
        # tmp grid
        self.tmp_path_lbl.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.tmp_path_data.grid(row=5, column=0, padx=10, pady=10, sticky="e")
        self.tmp_path_btn.grid(row=5, column=1, padx=10, pady=10, sticky="e")

    def browse_path(self, item):
        """
        Opens a file dialog for the user to select a directory path and updates the configuration settings accordingly.

        Parameters:
        item (object): The item object representing the configuration setting to be updated.
        """
        file_path = filedialog.askdirectory(initialdir=ROOT)
        if file_path:
            if item._name == "tmp":
                cfg.App.tmp = file_path
            if item._name == "arj":
                cfg.App.data = file_path

            item.set(file_path)
            cfg.save()
            log.info(f"Path for {item._name} was saved.")
            log.info(f"{item._name} >> {file_path}")

    def save_mask(self):
        """Save files mask"""
        mask = self.files_mask_data.get()
        cfg.App.mask_ext = mask.split()
        # If field is empty show description
        if mask == "":
            self.files_mask_data.configure(textvariable=None)
            self.files_mask_data.configure(placeholder_text=" as default", require_redraw=True)
            self.files_mask_data.update()

        cfg.save()
        log.info(f"Files mask was saved: {mask}")
