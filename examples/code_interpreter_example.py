import os
from voidrun import VoidRun


def main() -> None:
    vr = VoidRun()
    sandbox = vr.create_sandbox(name="code-interpreter-demo")

    try:
        print("=== Python ===")
        result = sandbox.run_code("print(2 + 2)", language="python")
        print("Output:", result.stdout.strip())

        result = sandbox.run_code("x = 10\ny = 20\nprint(x + y)", language="python")
        print("Output:", result.stdout.strip())

        result = sandbox.run_code("numbers = [1, 2, 3, 4, 5]\nprint(sum(numbers))", language="python")
        print("Output:", result.stdout.strip())

        print("\n=== JavaScript ===")
        result = sandbox.run_code("console.log('Hello from JS')", language="javascript")
        print("Output:", result.stdout.strip())

        result = sandbox.run_code(
            "const arr = [1, 2, 3];\nconsole.log(arr.reduce((a, b) => a + b, 0))",
            language="javascript"
        )
        print("Output:", result.stdout.strip())

        print("\n=== Multiple Snippets (Independent) ===")
        snippets = [
            ("print(2 ** 10)", "python"),
            ("import math\nprint(math.factorial(5))", "python"),
            ("print([x * 2 for x in range(5)])", "python"),
        ]

        for idx, (code, lang) in enumerate(snippets, start=1):
            res = sandbox.run_code(code, language=lang)
            print(f"Snippet {idx} output:", res.stdout.strip())

    finally:
        sandbox.remove()
        print("\nSandbox removed")


if __name__ == "__main__":
    main()
