import asyncio
from voidrun import VoidRun


async def main() -> None:
    vr = VoidRun()
    sandbox = vr.sandboxes.create(name="test-pty").data

    try:
        print("Ephemeral PTY")
        pty = await sandbox.pty.connect(
            on_data=lambda data: print(data, end="")
        )
        pty.send_input('echo "Hello from ephemeral"\n')
        await asyncio.sleep(1)
        await pty.close()

        print("\nPersistent session")
        session = sandbox.pty.create_session()
        session_id = session.data.data.session_id
        if not session_id:
            raise RuntimeError("Missing sessionId")

        pty2 = await sandbox.pty.connect(
            session_id=str(session_id),
            on_data=lambda data: print(data, end="")
        )
        pty2.send_input("ls -la\n")
        await asyncio.sleep(2)
        await pty2.close()

        sandbox.pty.delete_session(str(session_id))

    finally:
        sandbox.delete()
        print("Sandbox removed")


if __name__ == "__main__":
    asyncio.run(main())
