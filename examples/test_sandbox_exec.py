import time
from voidrun import VoidRun


def main() -> None:
    vr = VoidRun()
    sandbox = vr.create_sandbox(
        name=f"exec-test-{int(time.time())}",
        cpu=1,
        mem=1024,
        env_vars={"DEBUG": "true", "LOG_LEVEL": "info"},
    )

    try:
        def step(title, fn):
            print(f"\n[TEST] {title}")
            result = fn()
            print(result)
            return result

        step("Simple echo", lambda: sandbox.exec("echo 'Hello from exec!'"))
        step("System info", lambda: sandbox.exec("uname -a"))
        step("List /tmp", lambda: sandbox.exec("ls -la /tmp"))

        print("\n[TEST] Streaming exec")
        sandbox.exec_stream(
            "seq 1 5 | while read i; do echo streaming $i; sleep 1; done",
            on_stdout=lambda data: print("out:", data.strip()),
            on_exit=lambda result: print("exit:", result)
        )

        step("Env vars", lambda: sandbox.exec("echo \"MY_VAR=$MY_VAR\"", env={"MY_VAR": "test"}))
        step("Working dir", lambda: sandbox.exec("pwd", cwd="/tmp"))
        step("Piped", lambda: sandbox.exec("echo -e 'line1\nline2\nline3' | grep line2"))
        step("Timeout", lambda: sandbox.exec("sleep 1 && echo done", timeout=5))
        step("Create file", lambda: sandbox.exec("echo 'test' > /tmp/exec-test.txt && cat /tmp/exec-test.txt"))

        print("\n[TEST] Empty command validation")
        try:
            sandbox.exec("")
            print("FAIL: expected error")
        except Exception as exc:
            print("PASS:", exc)

    finally:
        sandbox.remove()
        print("Sandbox removed")


if __name__ == "__main__":
    main()
