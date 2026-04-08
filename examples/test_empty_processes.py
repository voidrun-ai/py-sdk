import time
from voidrun import VoidRun


def main() -> None:
    vr = VoidRun()
    sandbox = vr.create_sandbox(name="test-empty-processes")

    try:
        time.sleep(3)
        resp = sandbox.commands.list()
        processes = resp.data or []
        if processes == []:
            print("PASS: processes is empty list")
        else:
            print("Unexpected processes:", processes)

        run_resp = sandbox.commands.run("echo test")
        print("PID:", run_resp.data.pid)
        time.sleep(2)

        resp_after = sandbox.commands.list()
        processes_after = resp_after.data or []
        if processes_after == []:
            print("PASS: processes empty after completion")
        else:
            print("Unexpected processes after:", processes_after)

    finally:
        sandbox.remove()
        print("Sandbox removed")


if __name__ == "__main__":
    main()
