import asyncio

from voidrun import AsyncVoidRun


async def main():
    client = AsyncVoidRun()

    print("--- Listing Sandboxes (Async) ---")
    listed = await client.list_sandboxes()
    for sb in listed.sandboxes:
        print(f"Found sandbox: {sb.name} ({sb.id})")

    print("\n--- Creating a Sandbox using Async Context Manager ---")
    sb = await client.create_sandbox(name="python-sdk-async-demo")
    async with sb:
        print(f"Created sandbox: {sb.name}")

        print("\n--- Executing Code (Async) ---")
        exec_resp = await sb.interpreter.run_async(
            "import sys; print(f'Python version: {sys.version}')",
        )
        print(f"Output: {exec_resp.stdout}")

        print("\n--- Listing Files (Async) ---")
        files = await sb.fs.list_files_async("/")
        print(f"Root files count: {len(files.data)}")

    print("\nAsync sandbox has been automatically deleted.")


if __name__ == "__main__":
    asyncio.run(main())
