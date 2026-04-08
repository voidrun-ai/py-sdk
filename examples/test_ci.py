from voidrun import VoidRun


def main() -> None:
    vr = VoidRun()
    sandbox = None

    try:
        sandbox = vr.create_sandbox(
            name="code-interpreter-ci-test",
            env_vars={"CI": "true", "TEST_MODE": "enabled"},
        )

        result = sandbox.run_code("print(5 * 7)", language="python")
        output = (result.stdout or "").strip()
        if output != "35":
            print("Unexpected output for 5 * 7:", output)

        result = sandbox.run_code("i = 444\nprint('Looping', i)", language="python")
        print(result.stdout.strip())

        result = sandbox.run_code(
            "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n - 1)\n\nprint(factorial(6))",
            language="python"
        )
        output = result.stdout or ""
        numbers = [x for x in output.split() if x.isdigit()]
        if not numbers:
            print("No numeric output for factorial:", output)
        elif numbers[-1] != "720":
            print("Unexpected factorial output:", output)

        print("CI test completed successfully")
    finally:
        if sandbox:
            sandbox.remove()
            print("Sandbox removed")


if __name__ == "__main__":
    main()
