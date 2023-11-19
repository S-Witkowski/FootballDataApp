import yaml
import os


class Config:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        
    def load_config(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.normpath(os.path.join(current_dir, '..', '..', self.file_path))

        with open(config_path, "r") as file:
            return yaml.safe_load(file)