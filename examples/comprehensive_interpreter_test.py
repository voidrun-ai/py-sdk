from voidrun import VoidRun


def main() -> None:
    vr = VoidRun()
    sandbox = None

    try:
        print("Creating sandbox...")
        sandbox = vr.sandboxes.create(name="code-interpreter-test", cpu=1, mem=1024).data
        print(f"Sandbox created: {sandbox.id}\n")

        def run(label: str, code: str, language: str) -> None:
            print(f"> {label}")
            result = sandbox.run_code(code, language=language)
            stdout = result.data.stdout.strip() if result.data else ""
            print(f"Output: {stdout}")
            print(f"Success: {result.data.exit_code == 0 if result.data else False}\n")

        print("=== Test 1: Python ===")
        run("2 + 2", "print(2 + 2)", "python")
        run("x = 10; y = 20; print(x + y)", "x = 10\ny = 20\nprint(x + y)", "python")
        run("List comprehension", "numbers = [1,2,3,4,5]\nprint([x**2 for x in numbers])", "python")
        run("String ops", "text = 'Hello, World!'\nprint(text.upper())\nprint(len(text))", "python")

        print("=== Test 2: JavaScript ===")
        run("console.log(2 + 2)", "console.log(2 + 2)", "javascript")
        run("Array.map", "const arr = [1,2,3,4,5];\nconsole.log(arr.map(x => x * 2));", "javascript")
        run("Object stringify", "const obj = {name: 'VoidRun', version: '1.0'};\nconsole.log(JSON.stringify(obj));", "javascript")

        print("=== Test 3: Bash ===")
        run("echo hello", "echo 'Hello from Bash'", "bash")
        run("math", "echo $((2 + 2))", "bash")

        print("=== Test 4: Multiple Snippets (Independent) ===")
        snippets = [
            "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)\nprint(factorial(5))",
            "numbers = list(range(1, 6))\nprint(sum(numbers))",
            "print([x * 2 for x in range(5)])",
        ]
        for idx, code in enumerate(snippets, start=1):
            res = sandbox.run_code(code, language="python")
            print(f"Snippet {idx} output: {res.data.stdout.strip()}")

        print("\n=== Test 5: Error Handling ===")
        err = sandbox.run_code("invalid python syntax !@#$", language="python")
        print("Success:", err.data.exit_code == 0)
        print("Error:", (err.data.stderr or "")[:100])

        print("\nAll tests completed")
    finally:
        if sandbox:
            sandbox.delete()
            print("Sandbox removed")


if __name__ == "__main__":
    main()
