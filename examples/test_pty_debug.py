import asyncio
from voidrun import VoidRun


async def main() -> None:
    vr = VoidRun()
    sandbox = vr.create_sandbox(name="test-pty-debug", envVars={"DEBUG": "pty"})

    try:
        print("Connecting to PTY...")
        pty = await sandbox.pty.connect(
            on_data=lambda data: print("[DATA]", data.rstrip())
        )

        await asyncio.sleep(2)
        pty.send_input('echo "Hello from PTY"\n')
        await asyncio.sleep(2)
        await pty.close()

    finally:
        sandbox.remove()
        print("Sandbox removed")


if __name__ == "__main__":
    asyncio.run(main())
