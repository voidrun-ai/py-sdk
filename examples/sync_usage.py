import os
from voidrun import VoidRun

def main():
    # Initialize the client (ensure VR_API_KEY is set in your environment)
    client = VoidRun()

    print("--- Listing Sandboxes ---")
    sandboxes_resp = client.sandboxes.list()
    for sb in sandboxes_resp.data:
        print(f"Found sandbox: {sb.name} ({sb.id})")

    print("\n--- Creating a Sandbox using Context Manager ---")
    # This automatically cleans up the sandbox after the 'with' block
    with client.sandboxes.create(name="python-sdk-demo").data as sb:
        print(f"Created sandbox: {sb.name}")
        
        print("\n--- Executing a Command ---")
        exec_resp = sb.interpreter.run("print('Hello from VoidRun Python SDK!')")
        print(f"Output: {exec_resp.data.stdout}")
        
        print("\n--- File System Operations ---")
        sb.fs.upload_file("/tmp/hello.txt", "Hello VoidRun!")
        files = sb.fs.list_files("/tmp")
        print(f"Files in /tmp: {[f.name for f in files.data]}")
        
        content = sb.fs.download_file("/tmp/hello.txt")
        print(f"Downloaded content: {content.decode()}")

    print("\nSandbox has been automatically deleted.")

if __name__ == "__main__":
    main()
