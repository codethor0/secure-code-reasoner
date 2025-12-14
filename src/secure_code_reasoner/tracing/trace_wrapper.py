"""Trace wrapper module for intercepting operations during execution."""

import os
import sys
from pathlib import Path


def trace_file_operation(operation: str, file_path: Path) -> None:
    """Trace a file operation."""
    if os.environ.get("SCR_TRACE_MODE") == "1":
        print(f"SCR_TRACE:{operation}|file={file_path}", file=sys.stderr, flush=True)


def trace_process_spawn(command: str, pid: int) -> None:
    """Trace a process spawn."""
    if os.environ.get("SCR_TRACE_MODE") == "1":
        print(f"SCR_TRACE:process_spawn|cmd={command},pid={pid}", file=sys.stderr, flush=True)


def trace_network_operation(operation: str, address: str, port: int) -> None:
    """Trace a network operation."""
    if os.environ.get("SCR_TRACE_MODE") == "1":
        if os.environ.get("SCR_NO_NETWORK") == "1":
            print(f"SCR_TRACE:{operation}|addr={address},port={port},blocked=1", file=sys.stderr, flush=True)
        else:
            print(f"SCR_TRACE:{operation}|addr={address},port={port}", file=sys.stderr, flush=True)


def trace_module_import(module_name: str) -> None:
    """Trace a module import."""
    if os.environ.get("SCR_TRACE_MODE") == "1":
        print(f"SCR_TRACE:module_import|module={module_name}", file=sys.stderr, flush=True)


def install_trace_hooks() -> None:
    """Install trace hooks for common operations."""
    if os.environ.get("SCR_TRACE_MODE") != "1":
        return

    original_open = open
    original_subprocess_run = None
    original_socket_create = None

    try:
        import subprocess
        original_subprocess_run = subprocess.run
    except ImportError:
        pass

    try:
        import socket
        original_socket_create = socket.socket
    except ImportError:
        pass

    def traced_open(file, mode="r", *args, **kwargs):
        file_path = Path(file) if isinstance(file, (str, Path)) else None
        if file_path:
            if "w" in mode or "a" in mode or "x" in mode:
                if os.environ.get("SCR_NO_FILE_WRITE") == "1":
                    raise PermissionError(f"File write blocked by sandbox: {file_path}")
                trace_file_operation("file_write", file_path)
            elif "r" in mode:
                trace_file_operation("file_read", file_path)
        return original_open(file, mode, *args, **kwargs)

    def traced_subprocess_run(*args, **kwargs):
        if original_subprocess_run:
            import os as os_module
            pid = os_module.getpid()
            cmd_str = str(args[0]) if args else "unknown"
            trace_process_spawn(cmd_str, pid)
            return original_subprocess_run(*args, **kwargs)
        return None

    def traced_socket_create(*args, **kwargs):
        if original_socket_create:
            if os.environ.get("SCR_NO_NETWORK") == "1":
                raise PermissionError("Network access blocked by sandbox")
            sock = original_socket_create(*args, **kwargs)
            original_connect = sock.connect
            
            def traced_connect(address):
                addr, port = address
                trace_network_operation("network_connect", str(addr), port)
                return original_connect(address)
            
            sock.connect = traced_connect
            return sock
        return None

    builtins = __import__("builtins")
    builtins.open = traced_open

    if original_subprocess_run:
        import subprocess
        subprocess.run = traced_subprocess_run

    if original_socket_create:
        import socket
        socket.socket = traced_socket_create


if __name__ == "__main__":
    install_trace_hooks()

