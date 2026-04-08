import asyncio
from voidrun import VoidRun


async def main() -> None:
    vr = VoidRun()
    sandbox = vr.create_sandbox(name="watch-test")

    events = []

    def on_event(evt):
        print("Event:", evt)
        events.append(evt)

    try:
        watcher = await sandbox.fs.watch("/tmp", on_event=on_event)
        await asyncio.sleep(1)

        sandbox.fs.create_file("/tmp/hello.txt")
        sandbox.fs.upload_file("/tmp/hello11.txt", "Hello World")
        sandbox.fs.delete_file("/tmp/hello.txt")
        sandbox.fs.create_directory("/tmp/newdir")
        sandbox.fs.delete_file("/tmp/newdir")

        await asyncio.sleep(2)
        if events:
            print("SUCCESS: received events", len(events))
        else:
            print("FAIL: no events")

        watcher.close()
    finally:
        sandbox.remove()
        print("Sandbox removed")


if __name__ == "__main__":
    asyncio.run(main())
