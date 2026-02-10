from voidrun import VoidRun


def main() -> None:
    vr = VoidRun()
    sandbox = vr.sandboxes.create(name="test-commands").data

    try:
        print("[TEST] Run background process")
        handle = sandbox.commands.run("sh -c \"while true; do :; done\"")
        pid = handle.data.pid
        print("PID:", pid)

        print("[TEST] List running processes")
        procs = sandbox.commands.list()
        found = any(p.pid == pid for p in (procs.data or []))
        print("Found:", found)

        print("[TEST] Wait for completion")
        try:
            wait_res = sandbox.commands.wait(pid)
            print("Wait:", wait_res.data)
        except Exception as exc:
            print("Wait failed:", exc)

        print("[TEST] Attach to output")
        handle2 = sandbox.commands.run("sh -c \"echo line 1; echo line 2; echo line 3\"")
        try:
            sandbox.commands.connect(
                handle2.data.pid,
                on_stdout=lambda data: print("stdout:", data.strip()),
                on_exit=lambda result: print("exit:", result)
            )
        except Exception as exc:
            print("Attach failed:", exc)

        print("[TEST] Kill process")
        handle3 = sandbox.commands.run("sh -c \"while true; do :; done\"")
        try:
            sandbox.commands.kill(handle3.data.pid)
            print("Killed")
        except Exception as exc:
            print("Kill failed:", exc)

    finally:
        sandbox.delete()
        print("Sandbox removed")


if __name__ == "__main__":
    main()
