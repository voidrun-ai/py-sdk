import os
from voidrun import VoidRun

def main() -> None:
    vr = VoidRun()
    sbx = vr.create_sandbox(name="test-ts-exec")

    try:
        print("=== Test: TypeScript Execution ===")
        ts_code = """
interface User {
    name: string;
    age: number;
}
const user: User = { name: "Alice", age: 30 };
console.log(`User ${user.name} is ${user.age} years old.`);
function factorial(n: number): number {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
console.log(`Factorial of 5 is ${factorial(5)}`);
"""
        res = sbx.run_code(ts_code, language="typescript")
        print("Success:", res.success)
        print("Results:", res.results)
        print("Stdout:\n" + res.stdout)
        print("Stderr:\n" + res.stderr)

    finally:
        sbx.remove()
        print("Done")

if __name__ == "__main__":
    main()
