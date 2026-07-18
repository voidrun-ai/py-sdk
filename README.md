# VoidRun Python SDK

Python client for [VoidRun](https://voidrun.io) AI sandboxes: run commands, manage files, use pseudo-terminals, stream output, and execute multi-language code in isolated environments.

The high-level API is aligned with the official **TypeScript SDK** (`create_sandbox`, `list_sandboxes`, `remove_sandbox`, `Sandbox.run_code`, `CodeExecutionResult`, and shared defaults).

[![PyPI version](https://img.shields.io/pypi/v/voidrun)](https://pypi.org/project/voidrun/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick start](#quick-start)
- [Parity with the TypeScript SDK](#parity-with-the-typescript-sdk)
- [Core concepts](#core-concepts)
- [Code execution and interpreter](#code-execution-and-interpreter)
- [Background commands](#background-commands)
- [File system](#file-system)
- [File watching (async)](#file-watching-async)
- [Pseudo-terminal (PTY)](#pseudo-terminal-pty)
- [API reference (summary)](#api-reference-summary)
- [Runnable examples](#runnable-examples)
- [Development and tests](#development-and-tests)
- [Building and publishing](#building-and-publishing)
- [Error handling](#error-handling)
- [Troubleshooting](#troubleshooting)
- [Contributing, license, support](#contributing-license-support)

## Features

- **Sandbox lifecycle**: Create, list, fetch, start/sleep/wake (stop/pause→sleep, resume→wake), and remove sandboxes (sync and async).
- **Shell execution**: synchronous `exec` with optional `ExecRequest` (no `background` flag); SSE streaming via `exec_stream`; detached processes via `.commands.run`.
- **Code interpreter**: `run_code` / `interpreter.run` return a structured **`CodeExecutionResult`** (stdout, stderr, success, exit_code, results, logs).
- **Files**: Create, upload, download, list, move, copy, compress, extract, permissions, search, disk usage.
- **File watching**: WebSocket-backed directory watches (async).
- **PTY**: Ephemeral and persistent terminal sessions, resize, `run_command` with prompt detection.
- **Background commands**: Run, list, attach, wait, kill long-running processes.

## Requirements

- Python **3.9+**
- Dependencies: see [`pyproject.toml`](pyproject.toml) (Pydantic v2, httpx, urllib3, websockets, python-dotenv, etc.).

## Installation

```bash
pip install voidrun
```

With Poetry:

```bash
poetry add voidrun
```

**From this repository** (editable install for development):

```bash
cd py-sdk
pip install -e .
```

## Configuration

`VoidRun` and `AsyncVoidRun` require an **API key**. The **API base URL** defaults to the hosted endpoint (**`DEFAULT_API_BASE_URL`**, aligned with the TypeScript SDK and OpenAPI **`servers`**). Set **`VR_API_URL`** or **`API_URL`**, or pass **`base_url=`**, only for **self-hosted** deployments.

### Constructor

```python
from voidrun import VoidRun

vr = VoidRun(
    api_key="your-api-key",  # optional if VR_API_KEY / API_KEY is set
)
```

### Environment variables

| Variable | Purpose |
|----------|---------|
| `VR_API_KEY` or `API_KEY` | API key (required unless passed to the constructor). |
| `VR_API_URL` or `API_URL` | *(Self-hosted only.)* Overrides the default API base URL. |

### Defaults (aligned with TypeScript SDK)

Exported from `voidrun`:

| Constant | Value | Meaning |
|----------|-------|---------|
| `DEFAULT_API_BASE_URL` | `https://platform.void-run.com/api` | Default API host when `VR_API_URL` / `API_URL` are unset. |
| `DEFAULT_SANDBOX_IMAGE` | `"code"` | Default image id when creating a sandbox without `image=`. |
| `DEFAULT_SANDBOX_CPU` | `1` | Default CPU count. |
| `DEFAULT_SANDBOX_MEM` | `1024` | Default memory in MB. |

For **self-hosted** VoidRun, set **`VR_API_URL`** (or **`API_URL`**) to your instance’s API root (including `/api` if that is how your server is mounted).

## Quick start

### Synchronous (recommended shape)

```python
from voidrun import VoidRun

vr = VoidRun()  # uses VR_API_KEY; default base URL unless VR_API_URL / API_URL is set

sandbox = vr.create_sandbox(
    mem=1024,
    cpu=1,
    labels={"env": "prod", "team": "api"},
)

result = sandbox.exec('echo "Hello from VoidRun"')
# Exec returns VoidRunResponse whose .data is ExecResponseData
print(result.data.stdout)
print(sandbox.labels)

listed = vr.list_sandboxes(labels={"env": "prod"})
print(listed.meta.total)

sandbox.remove()
```

### Async

```python
import asyncio
from voidrun import AsyncVoidRun

async def main():
    async with AsyncVoidRun() as vr:
        sandbox = await vr.create_sandbox(mem=1024, cpu=1)
        result = sandbox.exec('echo "Hello"')
        print(result.data.stdout)
        await sandbox.remove_async()

asyncio.run(main())
```

### Context managers (auto cleanup)

Sync: exiting the block calls `remove()`. Async: `__aexit__` calls `remove_async()`.

```python
with vr.create_sandbox() as sandbox:
    print(sandbox.id)
```

```python
async with await vr.create_sandbox() as sandbox:
    print(sandbox.id)
```

## Parity with the TypeScript SDK

Use the same mental model as `@voidrun/sdk` (or the internal TS client):

| TypeScript (concept) | Python |
|----------------------|--------|
| `createSandbox` | `VoidRun.create_sandbox` / `await AsyncVoidRun.create_sandbox` |
| `getSandbox` | `get_sandbox` |
| `listSandboxes` | `list_sandboxes` → `ListSandboxesResult` |
| `removeSandbox` | `remove_sandbox` or `sandbox.remove()` |
| `sandbox.runCode` | `sandbox.run_code` |
| `CodeExecutionResult` | `CodeExecutionResult` (Pydantic model) |
| `CodeInterpreter` | `CodeInterpreter` (alias: `Interpreter` on `sandbox.interpreter`) |

**Listing sandboxes** returns a **`ListSandboxesResult`** with:

- `.sandboxes`: list of `Sandbox` instances  
- `.meta`: `ListSandboxesMeta` (`total`, `page`, `limit`, `total_pages`)

## Core concepts

### `VoidRun` / `AsyncVoidRun`

**Recommended methods**

- `create_sandbox(...)` → `Sandbox` (optional `labels=`)
- `get_sandbox(sandbox_id)` → `Sandbox`
- `list_sandboxes(page=..., limit=..., labels=...)` → `ListSandboxesResult`
- `remove_sandbox(sandbox_id)` → `None`

`AsyncVoidRun` exposes the same names with `await` and provides `aclose()` (and `async with` support) to shut down the thread pool used for API calls.

**Keyword aliases**

Create options accept both snake_case and camelCase where noted in code (e.g. `env_vars` / `envVars`, `org_id` / `orgId`).

### `Sandbox`

Notable attributes: `id`, `name`, `cpu`, `mem`, `org_id`, `status`, `env_vars`, `image`, `region`, `ref_id`, `auto_sleep`, `disk_mb`, `labels`, `created_at`, `created_by`.

Sub-clients:

- `.fs`: file operations  
- `.pty`: pseudo-terminal  
- `.interpreter`: `CodeInterpreter`  
- `.commands`: background processes  

Lifecycle:

- `start`, `sleep`, `wake` (and `*_async` variants)  
- `stop` / `pause` alias `sleep`; `resume` aliases `wake`  
- `remove()` / `remove_async()`: delete sandbox on the API  
- `delete()` / `delete_async()`: deprecated aliases for `remove`  

`info()` returns `self` (same idea as TS `sandbox.info()`).

## Code execution and interpreter

### `sandbox.exec`

Accepts a command string, or keyword `command=`, or a full **`ExecRequest`**:

```python
from voidrun.api_client.models.exec_request import ExecRequest

r = sandbox.exec("uname -a")
r = sandbox.exec(command="pwd", cwd="/tmp", timeout=60)
r = sandbox.exec(ExecRequest(command="ls", cwd="/"))
```

Return type: **`VoidRunResponse[ExecResponseData]`**: the API’s outer **`ExecResponse`** envelope is unwrapped so **`r.data`** is **`ExecResponseData`** (stdout / stderr / exit_code):

```python
print(r.data.stdout, r.data.stderr, r.data.exit_code)
```

**`sandbox.exec` is synchronous only** — it waits for the command. Do **not** use a `background` flag on `ExecRequest`; for a PID and long-running processes, use **`sandbox.commands.run`** ([Background commands](#background-commands)).

### Streaming (`exec_stream`)

Provide callbacks for SSE events (`on_stdout`, `on_stderr`, `on_exit`, `on_error`).

### Interpreter and `run_code`

`sandbox.interpreter` is a **`CodeInterpreter`**. Both `interpreter.run(...)` and **`sandbox.run_code(...)`** return **`CodeExecutionResult`** directly (no `.data` nesting):

```python
result = sandbox.run_code("print(2 + 2)", language="python")
print(result.stdout.strip())   # "4"
print(result.success)

result = sandbox.interpreter.run("console.log(1+1)", language="javascript")
```

**Supported languages** (typical): `python`, `javascript`, `typescript`, `node`, `bash`, `sh` (as supported by your VoidRun deployment).

## Background commands

```python
run_result = sandbox.commands.run(
    "sleep 5 && echo done",
    {"DEBUG": "true"},
    "/tmp",
    0,
)
print(run_result.data.pid)

sandbox.commands.list()
sandbox.commands.connect(pid, on_stdout=..., on_stderr=..., on_exit=...)
sandbox.commands.wait(pid)
sandbox.commands.kill(pid)
```

Response shapes follow the generated OpenAPI models; access fields via `.data` on `VoidRunResponse` where applicable.

## File system

```python
sandbox.fs.create_file("/tmp/hello.txt")
sandbox.fs.upload_file("/tmp/hello.txt", "Hello, World!")
sandbox.fs.upload_file_from_path("/tmp/remote.txt", "/local/file.txt")

data = sandbox.fs.download_file("/tmp/hello.txt")
sandbox.fs.delete_file("/tmp/hello.txt")

result = sandbox.fs.list_files("/tmp")
files = result.data

sandbox.fs.stat_file("/tmp/hello.txt")
sandbox.fs.create_directory("/tmp/mydir")
sandbox.fs.move_file("/tmp/a.txt", "/tmp/b.txt")
sandbox.fs.copy_file("/tmp/a.txt", "/tmp/copy.txt")
sandbox.fs.change_permissions("/tmp/a.txt", "755")

sandbox.fs.head_tail("/tmp/log.txt", head=True, lines=10)
sandbox.fs.search_files("/tmp", "*.txt")
sandbox.fs.disk_usage("/tmp")

archive = sandbox.fs.compress_file("/tmp", "tar.gz")
sandbox.fs.extract_archive("/tmp/archive.tar.gz", "/tmp/extracted")
```

## File watching (async)

```python
import asyncio
from voidrun import AsyncVoidRun

async def watch_tmp():
    async with AsyncVoidRun() as vr:
        sandbox = await vr.create_sandbox()

        watcher = await sandbox.fs.watch(
            "/app",
            recursive=True,
            on_event=lambda evt: print(evt.get("path"), evt.get("type")),
            on_error=lambda err: print("watch error:", err),
        )

        await asyncio.sleep(60)
        watcher.close()
        await sandbox.remove_async()

asyncio.run(watch_tmp())
```

## Pseudo-terminal (PTY)

### Ephemeral session

```python
import asyncio
from voidrun import AsyncVoidRun

async def ephemeral():
    async with AsyncVoidRun() as vr:
        sandbox = await vr.create_sandbox()
        pty = await sandbox.pty.connect(
            on_data=lambda data: print(data, end=""),
            on_error=lambda err: print("PTY error:", err),
        )
        pty.send_input('echo "Hello"\n')
        await asyncio.sleep(2)
        await pty.close()
        await sandbox.remove_async()

asyncio.run(ephemeral())
```

### Persistent session

```python
async def persistent():
    async with AsyncVoidRun() as vr:
        sandbox = await vr.create_sandbox()
        response = sandbox.pty.create_session()
        session_id = response.data.data.session_id

        pty = await sandbox.pty.connect(
            session_id=session_id,
            on_data=lambda data: print(data, end=""),
        )
        pty.send_input('echo "Hello"\n')
        await pty.close()

        reconnected = await sandbox.pty.connect(
            session_id=session_id,
            on_data=lambda data: print(data, end=""),
        )
        await reconnected.close()

        sandbox.pty.delete_session(session_id)
        await sandbox.remove_async()
```

### Helpers

```python
# After connect(...)
output = await pty.run_command("ls -la", timeout=5000, prompt="# ")
await pty.resize(80, 24)

sandbox.pty.list()
sandbox.pty.delete_session(session_id)
```

## API reference (summary)

### Exports (`from voidrun import ...`)

`VoidRun`, `AsyncVoidRun`, `Sandbox`, `CodeInterpreter`, `Interpreter` (alias), `CodeExecutionResult`, `ListSandboxesResult`, `ListSandboxesMeta`, `DEFAULT_SANDBOX_*`.

### `CodeExecutionResult`

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Derived from exit code. |
| `stdout` / `stderr` | `str` | Combined streams. |
| `exit_code` | `int \| None` | Process exit code. |
| `results` | `Any` | Parsed output when applicable. |
| `error` | `str \| None` | Error hint (often stderr). |
| `logs` | `dict` | e.g. `stdout` / `stderr` line lists. |

### OpenAPI client

The package includes a generated **`voidrun.api_client`** module. Regenerate it when the VoidRun OpenAPI specification changes (same spec as other official clients). After regen, confirm **sandbox `status`** values still match the server (e.g. `running`, `stopped`, `paused`, `error`, `killed`, `deleted`, …).

## Runnable examples

The [`examples/`](examples/) directory contains scripts for sync/async usage, exec, FS, lifecycle, PTY, background commands, and the code interpreter.

**Run all examples** (loads `py-sdk/.env` if present, sets `PYTHONPATH`):

```bash
chmod +x scripts/run_all_examples.sh   # once
./scripts/run_all_examples.sh
```

The script exits with status **1** if any example fails (useful for CI).

**Single example**

From the `py-sdk` directory (with `PYTHONPATH` including the repo root, same as the batch script):

```bash
export VR_API_KEY="your-api-key"
export PYTHONPATH="$(pwd)"

python3 examples/sync_usage.py
python3 examples/async_usage.py
```

Use an API key from the same VoidRun deployment as the API host (hosted default, or set **`VR_API_URL`** for self-hosted).

## Development and tests

```bash
cd py-sdk
pip install -e .
pip install pytest pytest-asyncio pytest-mock

pytest tests/
```

Hatch shortcut:

```bash
hatch run test
hatch run all-examples   # runs scripts/run_all_examples.sh
```

## Building and publishing

```bash
pip install build
python -m build
```

Or with Poetry: `poetry build` / `poetry publish`. See [`pyproject.toml`](pyproject.toml) for package metadata.

## Error handling

Failures raise exceptions from the OpenAPI client (for example **`ApiException`**) with HTTP status and body. Parse the error body for `error` and `details` fields returned by the VoidRun API.

```python
from voidrun import VoidRun
from voidrun.api_client.rest import ApiException

vr = VoidRun()

try:
    vr.get_sandbox("nonexistent-id")
except ApiException as e:
    print(e.status, e.body)
```

## Troubleshooting

### "API key is required …"

Set `VR_API_KEY` or pass `api_key=` to the constructor.

### "Base URL is required …"

You cleared the base URL (for example empty **`VR_API_URL`**). Omit the variable to use the packaged default, or set **`VR_API_URL`** / **`API_URL`** (self-hosted) with the correct prefix (often `/api`).

### Unauthorized / invalid API key

The key must match the VoidRun API you are calling (hosted default host or your self-hosted **`VR_API_URL`**). A local `.env` pointing at `localhost` with a cloud key (or vice versa) will return 401.

### Sandbox creation failures

Respect minimum **CPU** and **memory** enforced by your org/plan. Defaults are 1 CPU and 1024 MB; increase if the API rejects smaller values.

### PTY timeouts

Increase `timeout` in `run_command`, or allow more time before closing the session.

### File not found

List parent directories with `sandbox.fs.list_files` and confirm paths inside the sandbox.

## Contributing, license, support

Contributions are welcome; see the repository’s contributing guidelines if present.

- **License:** MIT: see the `LICENSE` file.  
- **PyPI:** [voidrun](https://pypi.org/project/voidrun/)  
- **Issues / discussions:** [GitHub](https://github.com/voidrun/py-sdk)  
- **Contact:** support@voidrun.io (see [`pyproject.toml`](pyproject.toml) authors)

---

Made with care by VoidRun.
