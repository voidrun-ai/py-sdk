import time

from voidrun import VoidRun


def main() -> None:
    vr = VoidRun()

    sandbox = vr.create_sandbox()
    print("Sandbox created:", sandbox.id)

    info = vr.get_sandbox(sandbox.id)
    print("Sandbox info:", info.id)

    listed = vr.list_sandboxes()
    print("Total sandboxes:", len(listed.sandboxes))

    time.sleep(2)
    sandbox.remove()
    print("Sandbox removed")

    sandbox2 = vr.create_sandbox()
    print("Sandbox 2:", sandbox2.id)
    time.sleep(2)
    sandbox2.remove()
    print("Sandbox 2 removed")


if __name__ == "__main__":
    main()
