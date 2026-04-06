// =======================
// (a) Generic Stack<T>
// =======================

class Stack<T> {
    private items: T[] = [];

    push(item: T): void {
        this.items.push(item);
    }

    pop(): T {
        if (this.isEmpty()) {
            throw new Error("Stack is empty");
        }
        return this.items.pop() as T;
    }

    peek(): T {
        if (this.isEmpty()) {
            throw new Error("Stack is empty");
        }
        return this.items[this.items.length - 1];
    }

    isEmpty(): boolean {
        return this.items.length === 0;
    }

    size(): number {
        return this.items.length;
    }

    toArray(): T[] {
        return [...this.items];
    }
}


// 🔹 Stack Usage Examples
const stack = new Stack<number>();
stack.push(1);
stack.push(2);
stack.push(3);

console.log(stack.pop());   // 3
console.log(stack.peek());  // 2
console.log(stack.size());  // 2
console.log(stack.toArray()); // [1,2]

const strStack = new Stack<string>();
strStack.push("a");
strStack.push("b");
console.log(strStack.peek()); // "b"



// =======================
// (b) Generic Dictionary<K, V>
// =======================

class Dictionary<K extends string | number, V> {
    private data: Record<K, V> = {} as Record<K, V>;

    set(key: K, value: V): void {
        this.data[key] = value;
    }

    get(key: K): V | undefined {
        return this.data[key];
    }

    has(key: K): boolean {
        return key in this.data;
    }

    delete(key: K): void {
        delete this.data[key];
    }

    keys(): K[] {
        return Object.keys(this.data) as K[];
    }

    values(): V[] {
        return Object.values(this.data);
    }

    entries(): [K, V][] {
        return Object.entries(this.data) as [K, V][];
    }

    forEach(callback: (value: V, key: K) => void): void {
        for (const key in this.data) {
            callback(this.data[key], key as K);
        }
    }
}


// 🔹 Dictionary Usage Examples
const dict = new Dictionary<string, number>();

dict.set("age", 25);
dict.set("score", 100);

console.log(dict.get("age")); // 25
console.log(dict.has("score")); // true

dict.forEach((value, key) => {
    console.log(key, value);
});

console.log(dict.keys());   // ["age", "score"]
console.log(dict.values()); // [25, 100]



// =======================
// (c) Result<T, E> (Discriminated Union)
// =======================

type Result<T, E> =
    | { ok: true; value: T }
    | { ok: false; error: E };


// Factory functions
function ok<T>(value: T): Result<T, never> {
    return { ok: true, value };
}

function err<E>(error: E): Result<never, E> {
    return { ok: false, error };
}


// Utility functions

function unwrap<T, E>(result: Result<T, E>): T {
    if (result.ok) return result.value;
    throw new Error(String(result.error));
}

function map<T, E, U>(
    result: Result<T, E>,
    fn: (value: T) => U
): Result<U, E> {
    return result.ok ? ok(fn(result.value)) : result;
}

function flatMap<T, E, U>(
    result: Result<T, E>,
    fn: (value: T) => Result<U, E>
): Result<U, E> {
    return result.ok ? fn(result.value) : result;
}


// 🔹 Result Usage Examples
const r1: Result<number, string> = ok(42);
console.log(unwrap(r1)); // 42

const r2 = err("not found");
// console.log(unwrap(r2)); // ❌ throws

// map example
const r3 = map(r1, x => x * 2);
console.log(unwrap(r3)); // 84

// flatMap example
const r4 = flatMap(r1, x => ok(x + 10));
console.log(unwrap(r4)); // 52

// chaining safely
const r5 = flatMap(r1, x =>
    x > 40 ? ok(x) : err("too small")
);
console.log(r5);