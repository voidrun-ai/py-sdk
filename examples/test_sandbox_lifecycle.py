import time
from voidrun import VoidRun


def main() -> None:
    vr = VoidRun()

    sandbox = vr.sandboxes.create().data
    print("Sandbox created:", sandbox.id)

    info = vr.sandboxes.get(sandbox.id)
    print("Sandbox info:", info.data.id)

    sandboxes = vr.sandboxes.list()
    print("Total sandboxes:", len(sandboxes.data))

    time.sleep(2)
    sandbox.delete()
    print("Sandbox removed")

    sandbox2 = vr.sandboxes.create().data
    print("Sandbox 2:", sandbox2.id)
    time.sleep(2)
    sandbox2.delete()
    print("Sandbox 2 removed")


if __name__ == "__main__":
    main()
