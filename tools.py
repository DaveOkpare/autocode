import subprocess
import threading
from pathlib import Path


class BashSession:
    def __init__(self):
        self.proc = subprocess.Popen(
            ["/bin/bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def execute(self, command: str, timeout: float = 10.0) -> str:
        self.proc.stdin.write(f"{command}; echo '__DONE__'\n")
        self.proc.stdin.flush()
        output = []

        def read_output():
            while True:
                line = self.proc.stdout.readline()
                if not line:
                    break
                output.append(line)
                if "__DONE__" in line:
                    break

        thread = threading.Thread(target=read_output)
        thread.daemon = True
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            return "TIMEOUT"

        output_lines = "".join(output).splitlines()
        return "\n".join([line for line in output_lines if "__DONE__" not in line])


class Tools:
    def __init__(self, session: BashSession):
        self._session = session

    def read_file(self, filepath: str):
        try:
            with open(filepath, "r") as file:
                return file.read()
        except FileNotFoundError:
            return "FILE_NOT_FOUND"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def write_file(self, filepath: str, content: str):
        try:
            with open(filepath, "w") as file:
                file.write(content)
            return "File written successfully"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def list_files(
        self,
        directory: str = ".",
        pattern: str = "*",
    ):
        exclude = {".venv", "__pycache__", ".git"}
        files = [
            str(f)
            for f in Path(directory).rglob(pattern)
            if not any(part in exclude for part in f.parts) and f.is_file()
        ]
        return files

    def edit_file(self, filepath: str, old_str: str, new_str: str):
        try:
            with open(filepath, "r+") as f:
                content = f.read()
                f.seek(0)
                f.write(content.replace(old_str, new_str))
                f.truncate()
            return "File edited successfully"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def search_files(self, pattern: str, path: str = "."):
        try:
            result = self._session.execute(f"grep -r '{pattern}' '{path}'")
            return result.splitlines()
        except Exception as e:
            return f"ERROR: {str(e)}"

    def execute(self, command: str, timeout: float = 10.0) -> str:
        return self._session.execute(command, timeout)
