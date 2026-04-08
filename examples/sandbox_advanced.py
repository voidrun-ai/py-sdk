import asyncio
import random
import time

from voidrun import AsyncVoidRun


async def main():
    print("--- Advanced Sandbox Construction ---")

    sandbox_name = f"advanced-sdbx-{random.randint(1, 1000)}"
    ref_id = f"ref-{int(time.time() * 1000)}"

    print(f"Creating sandbox {sandbox_name} in region 'us' with refId {ref_id}...")

    async with AsyncVoidRun() as vr:
        sandbox = await vr.create_sandbox(
            name=sandbox_name,
            auto_sleep=False,
            env_vars={
                "APP_ENV": "production",
                "DEBUG": "false",
            },
            ref_id=ref_id,
            region="us",
        )

        try:
            print("\nSandbox Metadata:")
            print(f"- ID: {sandbox.id}")
            print(f"- Name: {sandbox.name}")
            print(f"- Region: {sandbox.region}")
            print(f"- RefID: {sandbox.ref_id}")
            print(f"- AutoSleep: {sandbox.auto_sleep}")

            print("\n--- Pagination Test ---")
            print("Listing sandboxes (page 1, limit 2)...")
            listed = await vr.list_sandboxes(page=1, limit=2)

            print(f"Found {len(listed.sandboxes)} sandboxes on this page.")
            print(f"Total sandboxes: {listed.meta.total}")
            print(f"Total pages: {listed.meta.total_pages}")

            for i, s in enumerate(listed.sandboxes):
                print(f"  {i + 1}. {s.name} ({s.id})")

        finally:
            print("\nCleaning up...")
            await sandbox.remove_async()
            print("Cleanup complete.")


if __name__ == "__main__":
    asyncio.run(main())
