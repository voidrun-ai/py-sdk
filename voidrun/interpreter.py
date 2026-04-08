import json
import time
from functools import partial
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .api_client.api.execution_api import ExecutionApi
from .api_client.models.exec_request import ExecRequest


class CodeExecutionResult(BaseModel):
    """Aligned with ts-sdk `CodeExecutionResult`."""

    success: bool
    results: Any
    stdout: str
    stderr: str
    error: Optional[str] = None
    exit_code: Optional[int] = None
    logs: Dict[str, List[str]]


class CodeInterpreter:
    """Aligned with ts-sdk `CodeInterpreter` (run / runCode)."""

    def __init__(self, sandbox: Any):
        self._sandbox = sandbox
        self._client = sandbox._client
        self._api = ExecutionApi(
            self._client._api_client
            if hasattr(self._client, "_api_client")
            else self._client._sync_client._api_client,
        )
        self._sandbox_id = sandbox.id

    def run(
        self,
        code: str,
        language: str = "python",
        timeout: int = 60,
        **kwargs: Any,
    ) -> CodeExecutionResult:
        command = self._build_command(code, language)

        exec_req = ExecRequest(
            command=command,
            timeout=timeout,
            cwd=kwargs.get("cwd"),
            env=kwargs.get("env"),
        )

        response = self._api.exec_command_with_http_info(
            id=self._sandbox_id,
            exec_request=exec_req,
        )

        data = response.data.data if response.data else None
        stdout = data.stdout if data and data.stdout is not None else ""
        stderr = data.stderr if data and data.stderr is not None else ""
        exit_code = data.exit_code if data else 1

        results = self._parse_results(stdout, language)

        return CodeExecutionResult(
            success=exit_code == 0,
            results=results,
            stdout=stdout,
            stderr=stderr,
            error=stderr or None,
            exit_code=exit_code,
            logs={"stdout": [stdout], "stderr": [stderr]},
        )

    def run_code(
        self,
        code: str,
        *,
        language: str = "python",
        timeout: int = 60,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> CodeExecutionResult:
        """Same idea as ts-sdk `interpreter.runCode(code, options)`."""
        return self.run(code, language=language, timeout=timeout, cwd=cwd, env=env, **kwargs)

    async def run_async(
        self,
        code: str,
        language: str = "python",
        timeout: int = 60,
        **kwargs: Any,
    ) -> CodeExecutionResult:
        from .client import AsyncVoidRun

        if isinstance(self._client, AsyncVoidRun):
            return await self._client._run_async(
                partial(
                    self.run,
                    code,
                    language=language,
                    timeout=timeout,
                    **kwargs,
                ),
            )
        raise TypeError("run_async requires AsyncVoidRun client on Sandbox")

    async def run_code_async(
        self,
        code: str,
        *,
        language: str = "python",
        timeout: int = 60,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> CodeExecutionResult:
        return await self.run_async(
            code,
            language=language,
            timeout=timeout,
            cwd=cwd,
            env=env,
            **kwargs,
        )

    def _build_command(self, code: str, language: str) -> str:
        timestamp = int(time.time() * 1000)
        if language == "python":
            if len(code) < 1000 and "\n\n" not in code:
                escaped = code.replace("'", "'\\''")
                return f"python3 -c '{escaped}'"
            temp_file = f"/tmp/code_{timestamp}.py"
            return (
                f"cat > {temp_file} << 'EOFPYTHON'\n{code}\nEOFPYTHON\n"
                f"python3 {temp_file} && rm -f {temp_file}"
            )
        if language in ("javascript", "node"):
            if len(code) < 1000 and "\n\n" not in code:
                escaped = code.replace("'", "'\\''")
                return f"node -e '{escaped}'"
            temp_file = f"/tmp/code_{timestamp}.js"
            return (
                f"cat > {temp_file} << 'EOFJS'\n{code}\nEOFJS\n"
                f"node {temp_file} && rm -f {temp_file}"
            )
        if language == "typescript":
            if len(code) < 1000 and "\n\n" not in code:
                escaped = code.replace("'", "'\\''")
                return f"tsx -e '{escaped}'"
            temp_file = f"/tmp/code_{timestamp}.ts"
            return (
                f"cat > {temp_file} << 'EOFTS'\n{code}\nEOFTS\n"
                f"tsx {temp_file} && rm -f {temp_file}"
            )
        if language in ("bash", "sh"):
            escaped = code.replace("'", "'\\''")
            return f"bash -c '{escaped}'"
        raise ValueError(f"Unsupported language: {language}")

    def _parse_results(self, output: str, language: str) -> Any:
        if not output or not output.strip():
            return None
        lines = output.strip().split("\n")
        last_line = lines[-1]
        try:
            return json.loads(last_line)
        except Exception:
            if last_line and last_line not in ("undefined", "None"):
                return last_line
            return output.strip()


# Backward compatibility
Interpreter = CodeInterpreter
