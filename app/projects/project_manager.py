import json
import os

class ProjectManager:
    @staticmethod
    def save_project(file_path: str, project_data: dict):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=4)
            return True, ""
        except Exception as e:
            return False, str(e)

    @staticmethod
    def load_project(file_path: str):
        try:
            if not os.path.exists(file_path):
                return False, None, "Project file does not exist."
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return True, data, ""
        except Exception as e:
            return False, None, str(e)