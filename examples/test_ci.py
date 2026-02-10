from voidrun import VoidRun


def main() -> None:
    vr = VoidRun()
    sandbox = None

    try:
        sandbox = vr.sandboxes.create(
            name="code-interpreter-ci-test",
            envVars={"CI": "true", "TEST_MODE": "enabled"}
        ).data

        result = sandbox.run_code("print(5 * 7)", language="python")
        output = (result.data.stdout or "").strip()
        if output != "35":
            print("Unexpected output for 5 * 7:", output)

        result = sandbox.run_code("i = 444\nprint('Looping', i)", language="python")
        print(result.data.stdout.strip())

        result = sandbox.run_code(
            "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n - 1)\n\nprint(factorial(6))",
            language="python"
        )
        output = result.data.stdout or ""
        numbers = [x for x in output.split() if x.isdigit()]
        if not numbers:
            print("No numeric output for factorial:", output)
        elif numbers[-1] != "720":
            print("Unexpected factorial output:", output)

        print("CI test completed successfully")
    finally:
        if sandbox:
            sandbox.delete()
            print("Sandbox removed")


if __name__ == "__main__":
    main()
