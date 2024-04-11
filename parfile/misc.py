# misc.py
from ast import literal_eval
from configparser import ConfigParser
from dataclasses import InitVar, asdict, dataclass, fields
from dataclasses import field as dfield
from pathlib import Path
from typing import Dict
import logging
from rich import print as cprint

ROOT = Path.cwd()


def fsize(file_size):
    # Format size based on value
    if file_size < (1024 * 1024):  # Less than 1 MB
        size = f"{file_size:.2f} KB"
    else:
        size = f"{file_size // (1024 * 1024):.2f} MB"

    return size


@dataclass
class Paths:
    tmp: Path = ROOT / "tmp"
    logs: Path = ROOT / "logs"

    # Descriptions
    _descr: InitVar[Dict[str, str]] = {
        "tmp": "Temporary files path",
        "logs": "Log files path",
    }


@dataclass
class App:
    width: int = 750
    height: int = 500
    auto_save: bool = True
    files_ext: str = "rar"
    mask_ext: list[str] = dfield(default_factory=lambda: [])
    data: Path = ROOT

    # Descriptions
    _descr: InitVar[Dict[str, str]] = {
        "width": "Window width",
        "height": "Window height",
        "auto_save": "Automatically save path's changes",
        "files_ext": "Type of archive files to work",
        "mask_ext": "Types of files to extract from archive",
        "data": "Path to data files directory",
    }


@dataclass
class Logs:
    rewrite: bool = True
    logfile: str = "parfile.log"
    level: str = "DEBUG"
    verbose: bool = True

    # Descriptions
    _descr: InitVar[Dict[str, str]] = {
        "rewrite": "Continiue to write log file or rewrite.",
        "logfile": "Log file name",
        "level": "Log level",
        "verbose": "Print message to console",
    }


class LogConf:
    _instances = {}

    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

    def __init__(self, loglevel="INFO", file_name=None):
        self.verbose = cfg.Logs.verbose
        self.log_path = cfg.Paths.logs
        self.file_name = file_name or cfg.Logs.logfile
        self.fresh = cfg.Logs.rewrite
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(str(id(self)))
            self._logger.setLevel(self.LOG_LEVELS.get(loglevel.upper(), logging.INFO))

            log_format = "%(asctime)s - [%(levelname)s] - %(message)s"
            formatter = logging.Formatter(log_format, "%Y-%m-%d %H:%M:%S")

            file_handler = logging.FileHandler(f"{self.log_path}/{self.file_name}", "a" if self.fresh else "w")
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

    def __print_message(self, level, message, color=None):
        if self.verbose:
            if color:
                cprint(f"[{color}]{message}")
            else:
                cprint(message)
        if self._logger.isEnabledFor(level):
            self._logger.log(level, message)

    def debug(self, message, color="magenta"):
        self.__print_message(logging.DEBUG, message, color)

    def info(self, message, color=None):
        self.__print_message(logging.INFO, message, color)

    def warning(self, message, color="yellow"):
        self.__print_message(logging.WARNING, message, color)

    def error(self, message, color="red"):
        self.__print_message(logging.ERROR, message, color)

    def critical(self, message, color="red"):
        self.__print_message(logging.CRITICAL, message, color)

    def __getattr__(self, name):
        if name.startswith("_"):
            return object.__getattribute__(self, name)
        return getattr(self._logger, name)


class Cfg:
    """Main config App"""

    # Use Singleton method for this class
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    # Init class
    def __init__(self, data_classes, file_path):
        if not hasattr(self, "initialized"):
            self.data_classes = data_classes
            self.file_path = Path().cwd() / file_path
            # Next setting needs for work with comments in config file
            self.config = ConfigParser(allow_no_value=True, comment_prefixes=";")
            self.loaded_data = {}
            self.comment_lines = {}
            self.initialized = True
            self.__load()
            self.__create_structure()

    # Save configuration in file
    def save(self):
        with open(self.file_path, "w") as config_file:
            for cls in self.data_classes:
                # Load data
                section = cls.__name__

                # Load comments from dataclass
                comments = getattr(cls, "_descr", {})

                # Write section header
                config_file.write(f"[{section}]\n")

                # Load data from config file if it exists
                if section in self.loaded_data:
                    instance = self.loaded_data[section]
                else:
                    instance = cls()

                obj_dict = asdict(instance)

                for field, value in obj_dict.items():
                    if field in comments:
                        # Write multiline comments
                        for line in comments[field].split("\n"):
                            config_file.write(f"; {line.strip()}\n")
                    if isinstance(value, bool):
                        config_file.write(f"{field} = {str(value).lower()}\n")
                    else:
                        config_file.write(f"{field} = {str(value)}\n")

                config_file.write("\n")
        log.info(f"Configuration saved to {self.file_path}")

    # Load data
    def __load(self):
        # Check if config is True
        try:
            self.config.read(self.file_path)
        except Exception as e:
            print(f"Error reading INI file: {e}")
            print("Loading default values instead.")
            self.loaded_data = {cls.__name__: cls() for cls in self.data_classes}
            return

        for cls in self.data_classes:
            section = cls.__name__

            # If config dont have data use default peremeters
            if not self.config.has_section(section):
                self.loaded_data[section] = cls()
                continue

            obj_dict = {}
            for field in fields(cls):
                field_name = field.name
                # Convert standart datatypes

                if self.config.has_option(section, field_name):
                    value = self.config.get(section, field_name)
                    if field.type is bool:
                        value = value.lower() in ["true", "yes", "1"]
                    elif field.type is int:
                        value = int(value)
                    elif field.type is float:
                        value = float(value)
                    elif field.type == list[str]:
                        value = literal_eval(value)
                    obj_dict[field_name] = value

            obj = cls(**obj_dict)
            self.loaded_data[section] = obj

    def __create_structure(self):
        # Check if the "Paths" dataclass is present
        for class_name in self.data_classes:
            if class_name == Paths:
                directories = [getattr(class_name, field.name) for field in fields(class_name)]

                for directory in directories:
                    if not directory.is_dir():
                        directory.mkdir(parents=True, exist_ok=True)

    def __getattr__(self, name):
        if name == "loaded_data":
            raise AttributeError(f"'Cfg' object has no attribute '{name}'")

        if name in self.loaded_data:
            return self.loaded_data[name]
        else:
            raise AttributeError(f"'Cfg' object has no attribute '{name}'")


# Init configuration
configurations = [App, Paths, Logs]
cfg = Cfg(configurations, "config.ini")
# Init logger
log = LogConf(loglevel=cfg.Logs.level)


if __name__ == "__main__":
    pass
