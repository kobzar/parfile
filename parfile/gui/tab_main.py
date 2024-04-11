# tab_main.py
from icecream import ic
import customtkinter as ct
from misc import cfg, fsize, log
from pathlib import Path
from rarfile import RarFile
import shutil
import threading


class TabFiles(ct.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)

        self.selected = False
        self.files_ext = cfg.App.files_ext
        self.command = command
        self.files = {}
        self.refresh()

        # Configure resizing behavior
        self.grid_columnconfigure(0, weight=0)  # Make column unresizable
        self.grid_columnconfigure(1, weight=1)  # Make column resizable

    def refresh(self):
        # Get currently selected files
        selected_files = [file_name for file_name, data in self.files.items() if data["checked"].get()]

        files = sorted(Path(cfg.App.data).glob(f"*.{self.files_ext}"), key=lambda file: file.name)
        # Flush
        for widget in self.winfo_children():
            widget.destroy()

        # col = {}
        # Sort iems by name
        row = 0
        for file in files:
            file_name = file.name
            # delete exist files from self.files

            file_size = fsize(file.stat().st_size)

            # Check if file was previously selected
            checked = ct.BooleanVar(value=file_name in selected_files)

            file_checkbox = ct.CTkCheckBox(
                self,
                text=file_name,
                onvalue=True,
                offvalue=False,
                variable=checked,
                font=("Arial", 18),
                text_color="light blue",
            )
            # Configure elements
            if self.command is not None:
                file_checkbox.configure(command=self.command)

            # Add label for file size (optional)
            size_label = ct.CTkLabel(self, text=f"{file_size}", font=("Arial", 16), text_color="light green")
            # Add progress lbl
            pgs_lbl = ct.CTkLabel(self, text="0/0", font=("Arial", 16), text_color="yellow")
            # Add progress bar
            # pgs_bar = ct.CTkProgressBar(self, orientation="horizontal", height=5)
            pgs_bar = ct.CTkProgressBar(self, orientation="vertical", height=30, progress_color="cyan")
            pgs_bar.set(0)
            # Add Del button
            btn_del = ct.CTkButton(
                self, text="Del", width=25, command=lambda file_data=file: self.del_button_event(file_data)
            )

            # Configure position
            # file_checkbox.grid(row=row, column=0, pady=(0, 10), sticky="nsew")
            file_checkbox.grid(row=row, column=0, pady=(0, 10), sticky="w")
            pgs_lbl.grid(row=row, column=1, padx=(10, 0), pady=(0, 10), sticky="e")
            pgs_bar.grid(row=row, column=2, padx=(10, 0), pady=(0, 10), sticky="e")
            size_label.grid(row=row, column=3, padx=(10, 0), pady=(0, 10), sticky="e")
            btn_del.grid(row=row, column=4, padx=(10, 0), pady=(0, 10), sticky="e")

            self.files[file_name] = {
                "path": file.as_posix(),
                "checked": file_checkbox,
                "pgs": pgs_lbl,
                "pgs_bar": pgs_bar,
                "name": file_name,
                "btn_del": btn_del,
            }

            row += 1

    def del_button_event(self, item):
        """Delete selected file"""
        item.unlink()
        self.refresh()
        log.info(f"File {item.name} was deleted")

    def select(self):
        """Select/uselect all files"""
        self.selected = not self.selected
        for file_data in self.files.values():
            if self.selected:
                file_data["checked"].select()
            else:
                file_data["checked"].deselect()

    def mask_files(self, arj_list):
        """
        Filters a list of files based on the configured mask extensions.
        Args:
        arj_list (list): A list of file names to be filtered.
        Returns:
        list: A filtered list of file names based on the configured mask extensions.
        """
        if not cfg.App.mask_ext:
            result = arj_list
        else:
            result = [f for f in arj_list if any(f.endswith(ft) for ft in cfg.App.mask_ext)]

        return result

    def clean_tmp(self):
        shutil.rmtree(cfg.Paths.tmp)
        Path(cfg.Paths.tmp).mkdir(parents=True)

    def update_progress(self, file_name, progress, progress_bar):
        # Update progress label and bar
        self.files[file_name]["pgs"].configure(text=progress)
        self.files[file_name]["pgs_bar"].set(progress_bar)

    def extract_file(self, file, progress_callback):
        """Extracts a single RAR file and logs its parts."""
        part_cnt = 0
        try:
            with RarFile(file["path"]) as arj:
                parts = self.mask_files(arj.namelist())
                for part in parts:
                    part_cnt += 1
                    arj.extract(part, cfg.Paths.tmp)
                    log.info(f"Extracted {file['name']} >> {part}")
                    progress = f"{part_cnt}/{len(parts)}"
                    progress_bar = part_cnt / len(parts)
                    progress_callback(file["name"], progress, progress_bar)
        except Exception as e:
            log.error(e)

    def run(self):
        """Starts the extraction process."""
        files = [file_data for file_data in self.files.values() if file_data["checked"].get()]
        # Clear TMP dir before run
        self.clean_tmp()
        # Disable Del buttons for selected files
        for file in files:
            file["btn_del"].configure(state="disabled")

        # Define progress callback
        def progress_callback(file_name, progress, progress_bar):
            self.master.after(0, lambda: self.update_progress(file_name, progress, progress_bar))

        # Start threads
        threads = []
        for file in files:
            thread = threading.Thread(target=self.extract_file, args=(file, progress_callback))
            thread.start()
            threads.append(thread)

        # Check threads after starting them
        self.check_threads(threads)

    def check_threads(self, threads):
        """Check if all threads are finished, update GUI if necessary."""
        if all(not thread.is_alive() for thread in threads):
            # Enable Del buttons for selected files
            for file_data in self.files.values():
                file_data["btn_del"].configure(state="normal")
            return
        else:
            # Schedule check after 100 milliseconds
            self.master.after(100, lambda: self.check_threads(threads))


class TabFilesButtonsTop(ct.CTkFrame):
    def __init__(self, master, tab_files_instance, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=0)
        self.tab_files_frame = tab_files_instance
        # Top buttons frame
        self.top_buttons_frame = ct.CTkFrame(self)

        # Buttons
        self.button_refresh = ct.CTkButton(self.top_buttons_frame, text="Refresh", command=self.tab_files_frame.refresh)
        self.button_select = ct.CTkButton(self.top_buttons_frame, text="Select", command=self.tab_files_frame.select)
        self.button_run = ct.CTkButton(self.top_buttons_frame, text="Run", command=self.tab_files_frame.run)

        # Arrange buttons horizontally in the top frame using grid
        self.button_refresh.grid(row=0, column=0, padx=5, pady=5)
        self.button_select.grid(row=1, column=0, padx=5, pady=5)
        self.button_run.grid(row=2, column=0, padx=5, pady=5)

        # Place the top buttons frame in the main frame using grid
        self.top_buttons_frame.grid(row=0, column=0, padx=5, pady=5, sticky="n")


class TabFilesButtonsBottom(ct.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Bottom buttons frame
        self.buttons_frame = ct.CTkFrame(self)

        # Exit button
        self.exit_button = ct.CTkButton(self.buttons_frame, text="Exit", command=self.quit)

        # Arrange exit button in the bottom frame using grid
        self.exit_button.grid(row=0, column=0, padx=5, pady=5)

        # Place the bottom buttons frame in the main frame using grid
        self.buttons_frame.grid(row=1, column=0, sticky="nsew")  # Optional: add padding

        # INFO: Bind Esc key to exit
        # Bind Esc key to exit
        self.master.bind("<Escape>", lambda _: self.quit())

    def quit(self):
        self.master.destroy()  # Close the window


if __name__ == "__main__":
    pass
