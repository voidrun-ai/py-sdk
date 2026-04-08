from pathlib import Path
from voidrun import VoidRun


def main() -> None:
    vr = VoidRun()
    sandbox = vr.create_sandbox()
    fs = sandbox.fs

    base_dir = "/tmp/fs-e2e"
    file_path = f"{base_dir}/hello.txt"
    copy_path = f"{base_dir}/hello-copy.txt"
    moved_path = f"{base_dir}/sub/hello.txt"
    extract_dir = f"{base_dir}/extract"

    try:
        fs.create_directory(base_dir)
        fs.create_directory(f"{base_dir}/sub")
        fs.create_file(file_path)
        fs.upload_file(file_path, "hello world\nline two\n")

        fs.list_files(base_dir)
        fs.stat_file(file_path)
        fs.head_tail(file_path)
        fs.change_permissions(file_path, "644")
        fs.copy_file(file_path, copy_path)
        fs.move_file(copy_path, moved_path)

        archive_resp = fs.compress_file(base_dir, "tar.gz")
        archive_path = getattr(archive_resp.data, "archive_path", f"{base_dir}.tar.gz")
        fs.extract_archive(archive_path, extract_dir)

        fs.disk_usage(base_dir)
        fs.search_files(base_dir, "*.txt")

        downloaded = fs.download_file(file_path)
        local_dir = Path("/tmp/voidrun-fs-e2e")
        local_dir.mkdir(parents=True, exist_ok=True)
        download_path = local_dir / "downloaded.txt"
        download_path.write_bytes(downloaded if isinstance(downloaded, (bytes, bytearray)) else bytes(downloaded))

        fs.delete_file(moved_path)
        if download_path.exists():
            download_path.unlink()
        fs.delete_file(archive_path)
        fs.delete_file(extract_dir)
        fs.delete_file(base_dir)

        print("FS test completed")
    finally:
        sandbox.remove()


if __name__ == "__main__":
    main()
