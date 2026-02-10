# VoidRun Python SDK

Python SDK for interacting with VoidRun AI Sandboxes. Create sandboxes, execute commands, manage files, watch changes, and use interactive PTY sessions.

[![PyPI version](https://img.shields.io/pypi/v/voidrun)](https://pypi.org/project/voidrun/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Features

- Sandbox lifecycle management
- Command execution with stdout/stderr capture
- File system operations (upload, download, list, copy, move)
- File watching via WebSocket
- PTY sessions (ephemeral and persistent)
- Code interpreter helper for common languages
- Sync and async clients

## Installation

With pip:

```bash
pip install voidrun
```

With Poetry:

```bash
poetry add voidrun
```

## Quick Start (Sync)

Set your API key:

```bash
export VR_API_KEY="your-api-key"
```

Basic usage:

```python
from voidrun import VoidRun

vr = VoidRun()

resp = vr.sandboxes.create(mem=1024, cpu=1)
sandbox = resp.data

exec_resp = sandbox.exec('echo "Hello from VoidRun"')
print(exec_resp.data.data.stdout)

sandbox.delete()
```

## Quick Start (Async)

```python
import asyncio
from voidrun import AsyncVoidRun


async def main():
    vr = AsyncVoidRun()
    resp = await vr.sandboxes.create(mem=1024, cpu=1)
    sandbox = resp.data

    exec_resp = sandbox.exec('echo "Hello from VoidRun"')
    print(exec_resp.data.data.stdout)

    await sandbox.delete_async()
    await vr.aclose()


asyncio.run(main())
```

## Core Operations

### Sandboxes

```python
resp = vr.sandboxes.list()
sandboxes = resp.data

resp = vr.sandboxes.get("sandbox-id")
existing = resp.data

vr.sandboxes.delete("sandbox-id")
```

### Command Execution

```python
result = sandbox.exec("ls -la /home")
print(result.data.data.stdout)
print(result.data.data.stderr)
print(result.data.data.exit_code)
```

### Streaming Execution

```python
def on_stdout(data):
    print("STDOUT:", data)


def on_stderr(data):
    print("STDERR:", data)


sandbox.exec_stream(
    "python3 -c 'print(2 + 2)'",
    on_stdout=on_stdout,
    on_stderr=on_stderr,
)
```

### Code Interpreter

```python
resp = sandbox.run_code("print(2 + 2)", language="python")
print(resp.data.stdout)
```

### File Operations

```python
sandbox.fs.create_file("/tmp/hello.txt")
sandbox.fs.upload_file("/tmp/hello.txt", "Hello, World!")

data = sandbox.fs.download_file("/tmp/hello.txt")
print(data.decode("utf-8"))

files = sandbox.fs.list_files("/tmp")
print(files.data)
```

### File Watching (Async)

```python
async def watch_tmp():
    watcher = await sandbox.fs.watch(
        "/tmp",
        recursive=True,
        on_event=lambda evt: print("event:", evt),
        on_error=lambda err: print("watch error:", err),
    )

    # Stop watching when done
    watcher.close()
```

### PTY Sessions (Async)

```python
session_resp = sandbox.pty.create_session()
session_id = session_resp.data.data.session_id

pty = await sandbox.pty.connect(
    session_id=session_id,
    on_data=lambda data: print(data, end=""),
)

pty.send_input("echo 'hello'\n")
await pty.close()
```

## Configuration

Environment variables:

```bash
export VR_API_KEY="your-api-key"
export VOIDRUN_BASE_URL="https://api.voidrun.io"
```

You can also pass `api_key` and `base_url` directly:

```python
vr = VoidRun(api_key="...", base_url="https://api.voidrun.io")
```

## Examples

See the examples in [py-sdk/examples](py-sdk/examples).

## License

MIT License
