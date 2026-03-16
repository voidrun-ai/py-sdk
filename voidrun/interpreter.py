import time
import json
from typing import Any, Optional, Dict, List, Union
from pydantic import BaseModel
from .api_client.api.execution_api import ExecutionApi
from .api_client.models.exec_request import ExecRequest
from .response import VoidRunResponse

class CodeExecutionResult(BaseModel):
    success: bool
    results: Any
    stdout: str
    stderr: str
    error: Optional[str] = None
    exit_code: Optional[int] = None
    logs: Dict[str, List[str]]

class Interpreter:
    def __init__(self, sandbox: Any):
        self._sandbox = sandbox
        self._client = sandbox._client
        self._api = ExecutionApi(self._client._api_client if hasattr(self._client, "_api_client") else self._client._sync_client._api_client)
        self._sandbox_id = sandbox.id

    def run(self, code: str, language: str = "python", timeout: int = 60, **kwargs) -> VoidRunResponse[CodeExecutionResult]:
        command = self._build_command(code, language)
        
        exec_req = ExecRequest(
            command=command,
            timeout=timeout,
            cwd=kwargs.get("cwd"),
            env=kwargs.get("env")
        )
        
        response = self._api.exec_command_with_http_info(
            id=self._sandbox_id,
            exec_request=exec_req
        )
        
        data = response.data.data if response.data else None
        stdout = (data.stdout if data and data.stdout is not None else "")
        stderr = (data.stderr if data and data.stderr is not None else "")
        exit_code = data.exit_code if data else 1
        
        results = self._parse_results(stdout, language)
        
        res = CodeExecutionResult(
            success=exit_code == 0,
            results=results,
            stdout=stdout,
            stderr=stderr,
            error=stderr or None,
            exit_code=exit_code,
            logs={"stdout": [stdout], "stderr": [stderr]}
        )
        
        return VoidRunResponse(res, response)

    async def run_async(self, code: str, language: str = "python", timeout: int = 60, **kwargs) -> VoidRunResponse[CodeExecutionResult]:
        from .client import AsyncVoidRun
        if isinstance(self._client, AsyncVoidRun):
             return await self._client._run_async(self.run, code=code, language=language, timeout=timeout, **kwargs)
        raise TypeError("run_async requires AsyncVoidRun")

    def _build_command(self, code: str, language: str) -> str:
        timestamp = int(time.time() * 1000)
        if language == "python":
            if len(code) < 1000 and "\n\n" not in code:
                escaped = code.replace("'", "'\\''")
                return f"python3 -c '{escaped}'"
            else:
                temp_file = f"/tmp/code_{timestamp}.py"
                return f"cat > {temp_file} << 'EOFPYTHON'\n{code}\nEOFPYTHON\npython3 {temp_file} && rm -f {temp_file}"
        elif language in ["javascript", "node"]:
            if len(code) < 1000 and "\n\n" not in code:
                escaped = code.replace("'", "'\\''")
                return f"node -e '{escaped}'"
            temp_file = f"/tmp/code_{timestamp}.js"
            return f"cat > {temp_file} << 'EOFJS'\n{code}\nEOFJS\nnode {temp_file} && rm -f {temp_file}"
        elif language == "typescript":
            temp_file = f"/tmp/code_{timestamp}.js"
            return f"cat > {temp_file} << 'EOFJS'\n{code}\nEOFJS\nnode {temp_file} && rm -f {temp_file}"
        elif language in ["bash", "sh"]:
            escaped = code.replace("'", "'\\''")
            return f"bash -c '{escaped}'"
        else:
            raise ValueError(f"Unsupported language: {language}")

    def _parse_results(self, output: str, language: str) -> Any:
        if not output or not output.strip():
            return None
        lines = output.strip().split("\n")
        last_line = lines[-1]
        try:
            return json.loads(last_line)
        except Exception:
            if last_line and last_line not in ["undefined", "None"]:
                return last_line
            return output.strip()
