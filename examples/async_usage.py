import asyncio
import os
from voidrun import AsyncVoidRun

async def main():
    # Initialize the async client
    client = AsyncVoidRun()

    print("--- Listing Sandboxes (Async) ---")
    sandboxes_resp = await client.sandboxes.list()
    for sb in sandboxes_resp.data:
        print(f"Found sandbox: {sb.name} ({sb.id})")

    print("\n--- Creating a Sandbox using Async Context Manager ---")
    create_resp = await client.sandboxes.create(name="python-sdk-async-demo")
    async with create_resp.data as sb:
        print(f"Created sandbox: {sb.name}")
        
        print("\n--- Executing Code (Async) ---")
        exec_resp = await sb.interpreter.run_async("import sys; print(f'Python version: {sys.version}')")
        print(f"Output: {exec_resp.data.stdout}")
        
        print("\n--- Listing Files (Async) ---")
        files = await sb.fs.list_files_async("/")
        print(f"Root files count: {len(files.data)}")

    print("\nAsync sandbox has been automatically deleted.")

if __name__ == "__main__":
    asyncio.run(main())
