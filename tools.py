import re
import subprocess
import threading
from pathlib import Path

from pydantic_ai import RunContext


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

    def _should_include_usage(self, ctx: RunContext) -> bool:
        """Check if usage info should be included (exclude for Claude 4.5+)."""
        model_name = str(ctx.model).lower()
        # Exclude Claude 4.5 and later versions
        if "claude" in model_name:
            # Match patterns like claude-sonnet-4-5, claude-opus-4-6, etc.
            match = re.search(r"claude-\w+-(\d+)-(\d+)", model_name)
            if match:
                major, minor = int(match.group(1)), int(match.group(2))
                if major > 4 or (major == 4 and minor >= 5):
                    return False
        return True

    def _get_usage_info(self, ctx: RunContext) -> str:
        """Get usage info in XML format if applicable."""
        if not self._should_include_usage(ctx):
            return ""
        return f"<system_warning>Token usage: {ctx.usage.total_tokens} total tokens</system_warning>\n"

    def read_file(self, ctx: RunContext, filepath: str):
        """Read the full contents of a file from the filesystem.

        Use this to inspect source code, configuration, or any text file before making changes.

        Args:
            ctx: The run context containing usage info.
            filepath: Absolute or relative path to the file to read.

        Returns:
            The file contents as a string, "FILE_NOT_FOUND" if the path doesn't exist,
            or "ERROR: <message>" on failure.
        """
        usage_info = self._get_usage_info(ctx)
        try:
            with open(filepath, "r") as file:
                content = file.read()
            return usage_info + content
        except FileNotFoundError:
            return usage_info + "FILE_NOT_FOUND"
        except Exception as e:
            return usage_info + f"ERROR: {str(e)}"

    def write_file(self, ctx: RunContext, filepath: str, content: str):
        """Create or overwrite a file with the given content.

        WARNING: This overwrites the entire file. Always read_file first to avoid losing
        existing content. Prefer edit_file for targeted changes.

        Args:
            ctx: The run context containing usage info.
            filepath: Path to the file to create or overwrite.
            content: The full text content to write.

        Returns:
            "File written successfully" on success, or "ERROR: <message>" on failure.
        """
        usage_info = self._get_usage_info(ctx)
        try:
            with open(filepath, "w") as file:
                file.write(content)
            return usage_info + "File written successfully"
        except Exception as e:
            return usage_info + f"ERROR: {str(e)}"

    def list_files(
        self,
        ctx: RunContext,
        directory: str = ".",
        pattern: str = "*",
    ):
        """Recursively find files matching a glob pattern within a directory.

        Use this to discover project structure or locate files by name/extension.
        Automatically excludes .venv, __pycache__, and .git directories.

        Args:
            ctx: The run context containing usage info.
            directory: Root directory to search from. Defaults to current directory.
            pattern: Glob pattern to match filenames (e.g., "*.py", "test_*"). Defaults to "*".

        Returns:
            A list of matching file paths as strings with usage info appended.
        """
        usage_info = self._get_usage_info(ctx)
        exclude = {".venv", "__pycache__", ".git"}
        files = [
            str(f)
            for f in Path(directory).rglob(pattern)
            if not any(part in exclude for part in f.parts) and f.is_file()
        ]
        result = "\n".join(files) if files else "No files found"
        return usage_info + result

    def edit_file(self, ctx: RunContext, filepath: str, old_str: str, new_str: str):
        """Replace a specific string in a file with new content.

        Use this for targeted edits instead of rewriting the entire file with write_file.
        Replaces ALL occurrences of old_str. Always read_file first to find the exact
        string to match, including whitespace and indentation.

        Args:
            ctx: The run context containing usage info.
            filepath: Path to the file to edit.
            old_str: The exact text to find and replace. Must match file content exactly.
            new_str: The replacement text.

        Returns:
            "File edited successfully" on success,
            "Warning: No changes made to the file" if old_str was not found,
            or "ERROR: <message>" on failure.
        """
        usage_info = self._get_usage_info(ctx)
        try:
            with open(filepath, "r+") as f:
                content = f.read()
                f.seek(0)
                new_content = content.replace(old_str, new_str)
                if new_content == content:
                    return usage_info + "Warning: No changes made to the file"
                f.write(new_content)
                f.truncate()
            return usage_info + "File edited successfully"
        except Exception as e:
            return usage_info + f"ERROR: {str(e)}"

    def search_files(self, ctx: RunContext, pattern: str, path: str = "."):
        """Search file contents for a text pattern using grep.

        Use this to find where a function, variable, string, or pattern is used across
        the codebase. Automatically excludes .venv, .git, and __pycache__ directories.

        Args:
            ctx: The run context containing usage info.
            pattern: Text or regex pattern to search for (passed to grep -r).
            path: Directory to search within. Defaults to current directory.

        Returns:
            A list of matching lines in "filepath:line" format, or "ERROR: <message>" on failure.
        """
        usage_info = self._get_usage_info(ctx)
        exclude = [
            "--exclude-dir=.venv",
            "--exclude-dir=.git",
            "--exclude-dir=__pycache__",
        ]
        cmd = f"grep -r '{pattern}' '{path}' {' '.join(exclude)}"
        try:
            result = self._session.execute(cmd)
            result_lines = result.splitlines()
            result_str = "\n".join(result_lines) if result_lines else "No matches found"
            return usage_info + result_str
        except Exception as e:
            return usage_info + f"ERROR: {str(e)}"

    def execute(self, ctx: RunContext, command: str, timeout: float = 10.0) -> str:
        """Run a shell command and return its output.

        Use this for system operations like git, pip, running scripts, or other terminal
        commands. Do NOT use this for file operations — use the dedicated tools instead.

        Args:
            ctx: The run context containing usage info.
            command: The bash command to execute.
            timeout: Max seconds to wait before returning "TIMEOUT". Defaults to 10.

        Returns:
            Command stdout as a string, or "TIMEOUT" if the command exceeded the time limit.
        """
        usage_info = self._get_usage_info(ctx)
        result = self._session.execute(command, timeout)
        return usage_info + result
