import asyncio
import time
import random
from voidrun import AsyncVoidRun

async def main():
    print("--- Advanced Sandbox Construction ---")
    
    sandbox_name = f"advanced-sdbx-{random.randint(1, 1000)}"
    ref_id = f"ref-{int(time.time() * 1000)}"
    
    print(f"Creating sandbox {sandbox_name} in region 'us' with refId {ref_id}...")
    
    async with AsyncVoidRun() as vr:
        response = await vr.sandboxes.create(
            name=sandbox_name,
            region="us",
            ref_id=ref_id,
            disable_pause=True,
            env_vars={
                "APP_ENV": "production",
                "DEBUG": "false"
            }
        )
        sandbox = response.data
        
        try:
            print("\nSandbox Metadata:")
            print(f"- ID: {sandbox.id}")
            print(f"- Name: {sandbox.name}")
            
            # The properties might not be strongly typed on the Sandbox object yet, so we get them from the underlying model
            region = getattr(sandbox._model, "region", None)
            model_ref_id = getattr(sandbox._model, "ref_id", None)
            disable_pause = getattr(sandbox._model, "disable_pause", None)

            print(f"- Region: {region}")
            print(f"- RefID: {model_ref_id}")
            print(f"- DisablePause: {disable_pause}")

            print("\n--- Pagination Test ---")
            print("Listing sandboxes (page 1, limit 2)...")
            list_response = await vr.sandboxes.list(page=1, limit=2)
            
            sandboxes = list_response.data
            meta = list_response.raw_response.data.meta
            
            print(f"Found {len(sandboxes)} sandboxes on this page.")
            print(f"Total sandboxes: {meta.total}")
            print(f"Total pages: {meta.total_pages}")

            for i, s in enumerate(sandboxes):
                print(f"  {i+1}. {s.name} ({s.id})")

        finally:
            print("\nCleaning up...")
            await sandbox.delete_async()
            print("Cleanup complete.")

if __name__ == "__main__":
    asyncio.run(main())
