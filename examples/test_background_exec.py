import time
from voidrun import VoidRun


def main() -> None:
    vr = VoidRun()
    sandbox = vr.sandboxes.create(name=f"test-bg-exec-{int(time.time())}").data

    try:
        print("[TEST 1] Start background process")
        bg = sandbox.commands.run("sh -c \"while true; do :; done\"")
        pid = bg.data.pid
        print("PID:", pid)

        time.sleep(0.2)

        print("[TEST 2] List processes")
        procs = sandbox.commands.list()
        found = any(p.pid == pid for p in (procs.data or []))
        print("Found process:", found)

        print("[TEST 3] Kill process")
        if found:
            sandbox.commands.kill(pid)
            print("Killed")
        else:
            print("Process not found; skipping kill")

        print("[TEST 4] Stream output")
        stream_proc = sandbox.commands.run("sh -c \"echo line 1; echo line 2; echo line 3\"")
        stream_pid = stream_proc.data.pid

        def on_stdout(data: str):
            print("stdout:", data.strip())

        def on_exit(result):
            print("exit:", result)

        try:
            sandbox.commands.connect(stream_pid, on_stdout=on_stdout, on_exit=on_exit)
        except Exception as exc:
            print("connect failed:", exc)

        print("[TEST 5] Wait")
        wait_proc = sandbox.commands.run("sh -c \"exit 0\"")
        try:
            wait_res = sandbox.commands.wait(wait_proc.data.pid)
            print("wait result:", wait_res.data)
        except Exception as exc:
            print("wait failed:", exc)

    finally:
        sandbox.delete()
        print("Sandbox removed")


if __name__ == "__main__":
    main()
