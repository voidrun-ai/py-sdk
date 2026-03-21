import os
from voidrun import VoidRun

def main() -> None:
    vr = VoidRun()
    sbx = vr.sandboxes.create(name="test-ts-exec").data

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
        print("Success:", res.data.success)
        print("Results:", res.data.results)
        print("Stdout:\n" + res.data.stdout)
        print("Stderr:\n" + res.data.stderr)

    finally:
        sbx.delete()
        print("Done")

if __name__ == "__main__":
    main()
