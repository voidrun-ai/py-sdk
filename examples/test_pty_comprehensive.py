import asyncio
from voidrun import VoidRun


async def main() -> None:
    vr = VoidRun()
    sandbox = vr.create_sandbox(name="pty-comprehensive", envVars={"PTY_TEST": "comprehensive"})

    try:
        print("List sessions (should be empty)")
        print(sandbox.pty.list().data)

        print("Ephemeral PTY")
        pty = await sandbox.pty.connect(on_data=lambda data: print(data, end=""))
        pty.send_input('echo "Ephemeral PTY"\n')
        await asyncio.sleep(1.5)
        await pty.close()

        print("Create two sessions")
        s1 = sandbox.pty.create_session()
        s2 = sandbox.pty.create_session()
        sid1 = str(s1.data.data.session_id)
        sid2 = str(s2.data.data.session_id)

        print("List sessions after creation")
        print(sandbox.pty.list().data)

        print("Connect to first session")
        pty1 = await sandbox.pty.connect(session_id=sid1, on_data=lambda data: print(data, end=""))
        pty1.send_input('echo "Session 1"\n')
        await asyncio.sleep(1.5)
        await pty1.close()

        print("Reconnect to first session")
        pty1b = await sandbox.pty.connect(session_id=sid1, on_data=lambda data: print(data, end=""))
        pty1b.send_input('echo "Reconnected"\n')
        await asyncio.sleep(1.5)
        await pty1b.close()

        print("Delete sessions")
        sandbox.pty.delete_session(sid1)
        sandbox.pty.delete_session(sid2)

        print("Verify deletion")
        print(sandbox.pty.list().data)

    finally:
        sandbox.remove()
        print("Sandbox removed")


if __name__ == "__main__":
    asyncio.run(main())
