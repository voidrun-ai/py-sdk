# VoidRun Python SDK

A powerful Python SDK for interacting with VoidRun AI Sandboxes. Execute code, manage files, watch file changes, and interact with pseudo-terminals in isolated environments.

[![PyPI version](https://img.shields.io/pypi/v/voidrun)](https://pypi.org/project/voidrun/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Features

- 🏗️ **Sandbox Management** - Create, list, start, stop, pause, resume, and remove sandboxes
- 🚀 **Code Execution** - Execute commands with real-time streaming output capture
- 📁 **File Operations** - Create, read, delete, compress, and extract files
- 👀 **File Watching** - Monitor file changes in real-time via WebSocket
- 💻 **Pseudo-Terminal (PTY)** - Interactive terminal sessions (ephemeral & persistent)
- 🧠 **Code Interpreter** - Easy multi-language code execution (Python, JavaScript, Bash)
- ⚡ **Background Commands** - Run, list, kill, and attach to background processes
- 🎯 **Sync & Async** - Both synchronous and asynchronous APIs

## Installation

With pip:

```bash
pip install voidrun
```

With Poetry:

```bash
poetry add voidrun
```

## Quick Start

### Basic Usage (Sync)

```python
from voidrun import VoidRun

# Initialize the SDK with your credentials
vr = VoidRun(api_key="your-api-key-here")

# Create a sandbox
sandbox = vr.sandboxes.create(mem=1024, cpu=1).data

# Execute a command
result = sandbox.exec('echo "Hello from VoidRun"')
print(result.data.data.stdout)

# Clean up
sandbox.delete()
```

### Basic Usage (Async)

```python
import asyncio
from voidrun import AsyncVoidRun

async def main():
    vr = AsyncVoidRun(api_key="your-api-key-here")
    
    sandbox = await vr.sandboxes.create(mem=1024, cpu=1)
    
    result = sandbox.exec('echo "Hello from VoidRun"')
    print(result.data.data.stdout)
    
    await sandbox.delete_async()
    await vr.aclose()

asyncio.run(main())
```

## Core Concepts

### Sandboxes

An isolated environment where you can execute code, manage files, and run terminals.

```python
# Create a sandbox with options (sync)
sandbox = vr.sandboxes.create(
    name="my-sandbox",       # Optional: Sandbox name
    mem=1024,               # Memory in MB (optional, has defaults)
    cpu=1,                  # CPU cores (optional, has defaults)
    image="template-id",  # Optional: Image ID
    env_vars={              # Optional: Environment variables
        "DEBUG": "true",
        "LOG_LEVEL": "info"
    }
).data

# Using context manager (auto-cleanup)
with vr.sandboxes.create(name="my-sandbox").data as sandbox:
    # Work with sandbox
    pass
# Sandbox automatically deleted

# List all sandboxes
resp = vr.sandboxes.list()
sandboxes = resp.data
print(f"Total sandboxes: {len(sandboxes)}")

# Get a specific sandbox
existing = vr.sandboxes.get(sandbox_id).data

# Sandbox lifecycle management
sandbox.start()    # Start a stopped sandbox
sandbox.stop()     # Stop a running sandbox
sandbox.pause()    # Pause a running sandbox
sandbox.resume()   # Resume a paused sandbox

# Remove a sandbox
sandbox.delete()
```

### Code Execution

Execute commands and capture output, errors, and exit codes.

#### Synchronous Execution

```python
result = sandbox.exec("ls -la /home")

print(result.data.data.stdout)   # standard output
print(result.data.data.stderr)   # standard error
print(result.data.data.exit_code)  # exit code
```

#### Streaming Execution (SSE)

For real-time output, provide streaming handlers:

```python
def on_stdout(data):
    print("stdout:", data)

def on_stderr(data):
    print("stderr:", data)

def on_exit(result):
    print("exit:", result)

def on_error(error):
    print("error:", error)

sandbox.exec_stream(
    "seq 1 10 | while read i; do echo \"Line $i\"; sleep 1; done",
    on_stdout=on_stdout,
    on_stderr=on_stderr,
    on_exit=on_exit,
    on_error=on_error
)
```

#### Execution with Options

```python
result = sandbox.exec(
    "echo $MY_VAR && pwd",
    cwd="/tmp",                    # Working directory
    env={"MY_VAR": "test_value"},  # Environment variables
    timeout=30                     # Timeout in seconds
)
```

### Code Interpreter

Execute code in multiple programming languages with a simple, intuitive API.

```python
# Execute Python code
result = sandbox.interpreter.run('print(2 + 2)', language="python")
print(result.data.stdout.strip())  # "4"
print(result.data.success)         # True

# Execute JavaScript code
js_result = sandbox.interpreter.run('console.log("Hello")', language="javascript")

# Check execution result
print(result.data.exit_code)   # 0 for success
print(result.data.results)     # Parsed results
print(result.data.logs)        # {"stdout": [...], "stderr": [...]}
```

**Supported Languages:** `python`, `javascript`, `typescript`, `node`, `bash`, `sh`

### Background Commands

Run long-running processes in the background and manage them.

```python
# Start a background process
run_result = sandbox.commands.run(
    "sleep 100 && echo 'Done'",  # command
    {"DEBUG": "true"},            # env (optional)
    "/tmp",                      # cwd (optional)
    0                            # timeout (0 = no timeout)
)
print(run_result.data.pid)  # Process ID

# List all running processes
list_result = sandbox.commands.list()
print(list_result.data)  # Array of ProcessInfo

# Attach to a process and stream output
def on_stdout(data):
    print(data)

def on_stderr(data):
    print(data)

def on_exit(result):
    print("Process exited:", result)

sandbox.commands.connect(
    run_result.data.pid,
    on_stdout=on_stdout,
    on_stderr=on_stderr,
    on_exit=on_exit
)

# Wait for a process to complete
wait_result = sandbox.commands.wait(run_result.data.pid)
print(wait_result.data.exit_code)

# Kill a running process
kill_result = sandbox.commands.kill(run_result.data.pid)
print(kill_result.data.success)
```

### File Operations

Create, read, update, and manage files in the sandbox.

```python
# Create a file
sandbox.fs.create_file("/tmp/hello.txt")

# Upload content to file
sandbox.fs.upload_file("/tmp/hello.txt", "Hello, World!")

# Upload from local file path
sandbox.fs.upload_file_from_path("/tmp/remote.txt", "/local/file.txt")

# Read a file
data = sandbox.fs.download_file("/tmp/hello.txt")
content = data.decode("utf-8")

# Delete a file
sandbox.fs.delete_file("/tmp/hello.txt")

# List directory
result = sandbox.fs.list_files("/tmp")
files = result.data
print([f.name for f in files])

# Get file stats
stats = sandbox.fs.stat_file("/tmp/hello.txt")

# Create directory
sandbox.fs.create_directory("/tmp/mydir")

# Move file
sandbox.fs.move_file("/tmp/file.txt", "/tmp/newfile.txt")

# Copy file
sandbox.fs.copy_file("/tmp/file.txt", "/tmp/copy.txt")

# Change permissions
sandbox.fs.change_permissions("/tmp/file.txt", "755")

# Head/Tail - read first or last lines
head = sandbox.fs.head_tail("/tmp/file.txt", head=True, lines=10)
tail = sandbox.fs.head_tail("/tmp/file.txt", head=False, lines=10)

# Search files by pattern
search = sandbox.fs.search_files("/tmp", "*.txt")

# Get folder size
size = sandbox.fs.disk_usage("/tmp")

# Compress files
archive = sandbox.fs.compress_file("/tmp", "tar.gz")
print(archive.data)

# Extract archive
sandbox.fs.extract_archive("/tmp/archive.tar.gz", "/tmp/extracted")
```

### File Watching (Async)

Monitor file changes in real-time.

```python
import asyncio
from voidrun import AsyncVoidRun

async def watch_tmp():
    vr = AsyncVoidRun()
    sandbox = await vr.sandboxes.create()
    
    watcher = await sandbox.fs.watch(
        "/app",
        recursive=True,
        on_event=lambda evt: print(f"File changed: {evt.get('path')} - {evt.get('type')}"),
        on_error=lambda err: print("Watch error:", err),
    )

    # Keep watching for a while
    await asyncio.sleep(60)
    
    # Stop watching
    watcher.close()
    
    await sandbox.delete_async()
    await vr.aclose()

asyncio.run(watch_tmp())
```

### Pseudo-Terminal (PTY)

Interactive terminal sessions with two modes:

#### Ephemeral Sessions (Temporary)

```python
import asyncio
from voidrun import AsyncVoidRun

async def ephemeral_pty():
    vr = AsyncVoidRun()
    sandbox = await vr.sandboxes.create()
    
    # Connect to ephemeral PTY (no session management - temporary shell)
    pty = await sandbox.pty.connect(
        on_data=lambda data: print(data, end=""),
        on_error=lambda err: print("PTY error:", err),
    )

    # Send commands
    pty.send_input('echo "Hello"\n')
    pty.send_input("pwd\n")

    await asyncio.sleep(2)
    
    # Close connection
    await pty.close()
    
    await sandbox.delete_async()
    await vr.aclose()

asyncio.run(ephemeral_pty())
```

#### Persistent Sessions

```python
import asyncio
from voidrun import AsyncVoidRun

async def persistent_pty():
    vr = AsyncVoidRun()
    sandbox = await vr.sandboxes.create()
    
    # Create a persistent session
    response = sandbox.pty.create_session()
    session_id = response.data.data.session_id

    # Connect to the session
    pty = await sandbox.pty.connect(
        session_id=session_id,
        on_data=lambda data: print(data, end=""),
    )

    # Send commands
    pty.send_input('echo "Hello"\n')

    # Close connection (session persists)
    await pty.close()

    # Reconnect later - session and output persist
    reconnected = await sandbox.pty.connect(
        session_id=session_id,
        on_data=lambda data: print(data, end=""),  # Includes buffered output
    )
    
    await reconnected.close()
    
    # Delete the session when done
    sandbox.pty.delete_session(session_id)
    
    await sandbox.delete_async()
    await vr.aclose()

asyncio.run(persistent_pty())
```

#### Interactive Commands

Run commands with automatic prompt detection:

```python
pty = await sandbox.pty.connect(session_id=session_id)

output = await pty.run_command(
    "ls -la",
    timeout=5000,
    prompt="# "  # Prompt to detect (default: "# ")
)

print("Output:", output)
```

#### Resize Terminal

```python
await pty.resize(80, 24)  # columns, rows
```

#### Session Management

```python
# List all sessions
sessions = sandbox.pty.list()

# Delete a session
sandbox.pty.delete_session(session_id)
```

## API Reference

### VoidRun Class

Main synchronous client for interacting with the API.

```python
vr = VoidRun(api_key="...")
```

**Options:**

- `api_key: str` - API key (defaults to `os.environ.get("VR_API_KEY")`)

**Properties:**

- `sandboxes: SandboxesFacade` - Sandbox management interface

**Methods:**

- `sandboxes.create(...)` - Create a new sandbox
  - `name?: str` - Sandbox name
  - `cpu?: int` - CPU cores
  - `mem?: int` - Memory in MB
  - `image?: str` - Image ID
  - `env_vars?: dict` - Environment variables
- `sandboxes.list(page=1, limit=50)` - List all sandboxes
- `sandboxes.get(id: str)` - Get a specific sandbox
- `sandboxes.delete(id: str)` - Delete a sandbox

### AsyncVoidRun Class

Main asynchronous client for interacting with the API.

```python
vr = AsyncVoidRun(api_key="...")
```

**Options:** Same as `VoidRun`

**Methods:**

- `sandboxes.create(...)` - Create a new sandbox (async)
- `sandboxes.list(...)` - List all sandboxes (async)
- `sandboxes.get(id)` - Get a specific sandbox (async)
- `sandboxes.delete(id)` - Delete a sandbox (async)
- `aclose()` - Close the async client

### Sandbox Class

Represents an isolated sandbox environment.

**Properties:**

- `id: str` - Sandbox ID
- `name: str` - Sandbox name
- `cpu: int` - CPU cores
- `mem: int` - Memory in MB
- `org_id: str` - Organization ID
- `status: str` - Sandbox status
- `env_vars: dict` - Environment variables
- `fs: FS` - File system interface
- `pty: PTY` - PTY interface
- `interpreter: Interpreter` - Code interpreter
- `commands: Commands` - Background commands interface

**Methods:**

- `exec(command: str, timeout=30, env=None, cwd=None)` - Execute a command
- `exec_stream(command: str, timeout=30, env=None, cwd=None, on_stdout=None, on_stderr=None, on_exit=None, on_error=None)` - Streaming execution
- `interpreter.run(code: str, language="python", timeout=60)` - Execute code
- `start()` - Start the sandbox
- `stop()` - Stop the sandbox
- `pause()` - Pause the sandbox
- `resume()` - Resume the sandbox
- `delete()` - Delete the sandbox
- `delete_async()` - Delete the sandbox (async)

**Exec Response:**

```python
{
    data: {
        stdout: str,     # standard output
        stderr: str,    # standard error
        exit_code: int  # exit code
    }
}
```

**Code Execution Result:**

```python
{
    success: bool,
    results: Any,          # Parsed results
    stdout: str,           # Combined stdout
    stderr: str,           # Combined stderr
    error: Optional[str],  # Error message if any
    exit_code: Optional[int],  # Process exit code
    logs: {
        stdout: List[str],  # Individual stdout lines
        stderr: List[str]  # Individual stderr lines
    }
}
```

### Commands Class

Background process management.

**Methods:**

- `run(command: str, env=None, cwd=None, timeout=0)` - Start a background process
- `list()` - List all running processes
- `kill(pid: int)` - Kill a process
- `connect(pid: int, on_stdout=None, on_stderr=None, on_exit=None, on_error=None)` - Attach to process output stream
- `wait(pid: int)` - Wait for process to complete

### FS Class

Manage files and directories.

**Methods:**

- `create_file(path: str)` - Create a file
- `upload_file(path: str, content: str)` - Upload file content
- `upload_file_from_path(path: str, file_path: str)` - Upload from local path
- `download_file(path: str)` - Download file as bytes
- `delete_file(path: str)` - Delete a file/directory
- `list_files(path: str)` - List directory contents
- `stat_file(path: str)` - Get file metadata
- `create_directory(path: str)` - Create a directory
- `compress_file(path: str, format="tar.gz")` - Create archive
- `extract_archive(archive: str, dest=None)` - Extract archive
- `move_file(source: str, destination: str)` - Move/rename file
- `copy_file(source: str, destination: str)` - Copy file
- `change_permissions(path: str, mode: str)` - Change file permissions
- `head_tail(path: str, lines=10, head=True)` - Read file head/tail
- `search_files(path: str, pattern: str)` - Search files by pattern
- `disk_usage(path: str)` - Get folder size
- `watch(path: str, recursive=True, ignore_hidden=True, on_event=None, on_error=None)` - Watch for file changes (async)

### PTY Class

Pseudo-terminal operations.

**Methods:**

- `list()` - List active sessions
- `create_session(cols=80, rows=24)` - Create a persistent session
- `connect(session_id=None, on_data=None, on_close=None, on_error=None)` - Connect to PTY
- `delete_session(session_id: str)` - Delete a session

### PtySession Methods

- `send_input(data: str)` - Send data to terminal
- `run_command(cmd: str, timeout=30000, prompt="# ")` - Execute with prompt detection
- `resize(cols: int, rows: int)` - Resize terminal
- `close()` - Close connection

## Examples

### Execute Python Script

```python
from voidrun import VoidRun

vr = VoidRun()
sandbox = vr.sandboxes.create(mem=1024, cpu=1).data

# Create Python script
sandbox.fs.create_file("/tmp/script.py")
sandbox.fs.upload_file(
    "/tmp/script.py",
    """
import sys
print("Python version:", sys.version)
print("Hello from Python!")
"""
)

result = sandbox.exec("python3 /tmp/script.py")
print(result.data.data.stdout)

sandbox.delete()
```

### Code Interpreter Workflow

```python
sandbox = vr.sandboxes.create(name="interpreter-demo").data

# Python data analysis
result = sandbox.interpreter.run("""
import json
data = [1, 2, 3, 4, 5]
result = {
    "sum": sum(data),
    "avg": sum(data) / len(data),
    "max": max(data)
}
print(json.dumps(result))
""", language="python")

print(result.data.results)  # Parsed JSON output

# JavaScript
js_result = sandbox.interpreter.run("""
const fib = (n) => n <= 1 ? n : fib(n-1) + fib(n-2);
console.log(fib(10));
""", language="javascript")

sandbox.delete()
```

### Background Process Management

```python
sandbox = vr.sandboxes.create().data

# Start a long-running process
run_result = sandbox.commands.run("tail -f /var/log/syslog")
pid = run_result.data.pid

# Attach to stream output
sandbox.commands.connect(
    pid,
    on_stdout=lambda data: print(data),
    on_exit=lambda result: print("Exited:", result)
)

# Later, kill the process
sandbox.commands.kill(pid)

sandbox.delete()
```

### Monitor Code Changes

```python
import asyncio
from voidrun import AsyncVoidRun

async def watch_changes():
    vr = AsyncVoidRun()
    sandbox = await vr.sandboxes.create(mem=1024, cpu=1)
    
    # Watch for file changes
    watcher = await sandbox.fs.watch(
        "/app/src",
        recursive=True,
        on_event=lambda event: print(f"File {event.get('type')}: {event.get('path')}"),
    )
    
    # Keep watching for a while
    await asyncio.sleep(60)
    
    watcher.close()
    await sandbox.delete_async()
    await vr.aclose()

asyncio.run(watch_changes())
```

### Build & Test Workflow

```python
sandbox = vr.sandboxes.create(mem=2048, cpu=2).data

# Upload source code
sandbox.fs.create_file("/app/main.js")
sandbox.fs.upload_file("/app/main.js", "console.log('Hello World');")

# Install dependencies
result = sandbox.exec("npm install")
if result.data.data.exit_code != 0:
    raise Error("Install failed")

# Run tests
result = sandbox.exec("npm test")
print("Test output:", result.data.data.stdout)

# Build
result = sandbox.exec("npm run build")
print("Build output:", result.data.data.stdout)

sandbox.delete()
```

## Configuration

The SDK can be configured by passing options to the constructor or using environment variables:

```python
vr = VoidRun(
    api_key="your-api-key",              # Required: Your API key
)
```

Environment variables:

```bash
export VR_API_KEY="your-api-key"
```

## Error Handling

```python
from voidrun import VoidRun

try:
    sandbox = vr.sandboxes.create(mem=256, cpu=0.5)
except Exception as e:
    print("Error:", str(e))
```

Common errors:

- **Validation Error** - Invalid sandbox parameters
- **Authentication Error** - Invalid or missing API key
- **Not Found** - Sandbox or session doesn't exist
- **Timeout** - Operation took too long

## Testing

Run the examples:

```bash
# Run every script under examples/ (loads py-sdk/.env if present, sets PYTHONPATH)
chmod +x scripts/run_all_examples.sh   # once
./scripts/run_all_examples.sh
```

Or run a single example:

```bash
# Set your API key
export VR_API_KEY="your-api-key"

# Run sync example
python -m examples.sync_usage

# Run async example
python -m examples.async_usage

# Run other examples
python -m examples.test_sandbox_exec
python -m examples.test_sandbox_fs
python -m examples.test_sandbox_lifecycle
python -m examples.test_pty
python -m examples.test_background_exec
python -m examples.code_interpreter_example
```

## Building from Source

```bash
# Install dependencies
pip install -e .

# Or with poetry
poetry install
```

## Publishing

```bash
# Build and publish to PyPI
poetry build
poetry publish
```

## Troubleshooting

### "API key is required (pass it or set VR_API_KEY/API_KEY)"

Pass your API key in the constructor:

```python
vr = VoidRun(api_key="your-api-key")
```

Or set environment variable:

```bash
export VR_API_KEY="your-api-key"
```

### "Sandbox creation failed"

Ensure your sandbox parameters are valid:

- `mem`: minimum 1024 MB
- `cpu`: minimum 1 core

```python
sandbox = vr.sandboxes.create(
    mem=1024,  # At least 1GB
    cpu=1,     # At least 1 core
)
```

### "PTY Connection Timeout"

Increase timeout for slow systems:

```python
pty = await sandbox.pty.connect(
    session_id=session_id,
    on_data=lambda data: print(data),
)

# For run_command
output = await pty.run_command("slow-command", timeout=30000)  # 30 seconds
```

### "File Not Found"

Check the file path:

```python
# List files to verify path
files = sandbox.fs.list_files("/app")
print([f.name for f in files.data])

# Then access specific file
content = sandbox.fs.download_file("/app/file.txt")
```

## API Documentation

Full API documentation is available at the VoidRun docs site.

## Contributing

Contributions are welcome! Please check the main repository for guidelines.

## License

MIT License - See LICENSE file for details

## Support

- 📧 Email: support@void-run.com
- 🐛 Issues: [GitHub Issues](https://github.com/voidrun/py-sdk/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/voidrun/py-sdk/discussions)

---

**Made with ❤️ by VoidRun**
