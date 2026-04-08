from voidrun import VoidRun


def main():
    client = VoidRun()

    print("--- Listing Sandboxes ---")
    listed = client.list_sandboxes()
    for sb in listed.sandboxes:
        print(f"Found sandbox: {sb.name} ({sb.id})")

    print("\n--- Creating a Sandbox using Context Manager ---")
    with client.create_sandbox(name="python-sdk-demo") as sb:
        print(f"Created sandbox: {sb.name}")

        print("\n--- Executing a Command ---")
        exec_resp = sb.interpreter.run("print('Hello from VoidRun Python SDK!')")
        print(f"Output: {exec_resp.stdout}")

        print("\n--- File System Operations ---")
        sb.fs.upload_file("/tmp/hello.txt", "Hello VoidRun!")
        files = sb.fs.list_files("/tmp")
        print(f"Files in /tmp: {[f.name for f in files.data]}")

        content = sb.fs.download_file("/tmp/hello.txt")
        print(f"Downloaded content: {content.decode()}")

    print("\nSandbox has been automatically deleted.")


if __name__ == "__main__":
    main()
