from voidrun import VoidRun


def main() -> None:
    vr = VoidRun()
    sbx = vr.create_sandbox(name="test-runcode")

    try:
        print("=== Test 1: Python (stdlib) ===")
        res = sbx.run_code("import math\nprint(sum([1,2,3,4]))\nprint(math.sqrt(81))")
        print(res.stdout)

        print("=== Test 2: JavaScript factorial ===")
        res = sbx.run_code(
            "function factorial(n) { if (n === 0) return 1; return n * factorial(n - 1); }\nconsole.log(factorial(6));",
            language="javascript"
        )
        print(res.stdout)

        print("=== Test 3: Simple Python ===")
        res = sbx.run_code("print('Hello from Python')\nprint(2 + 2)")
        print(res.stdout)

        print("=== Test 4: Bash ===")
        res = sbx.run_code("echo 'Current dir: $(pwd)' && ls -la", language="bash")
        print(res.stdout)

        print("=== Test 5: Python error ===")
        res = sbx.run_code("print(undefined_variable)")
        print("Success:", res.success)
        print("Error:", res.stderr)

    finally:
        sbx.remove()
        print("Done")


if __name__ == "__main__":
    main()
