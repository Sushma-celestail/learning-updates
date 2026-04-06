"use strict";
// =======================
// (a) Generic Stack<T>
// =======================
class Stack {
    items = [];
    push(item) {
        this.items.push(item);
    }
    pop() {
        if (this.isEmpty()) {
            throw new Error("Stack is empty");
        }
        return this.items.pop();
    }
    peek() {
        if (this.isEmpty()) {
            throw new Error("Stack is empty");
        }
        return this.items[this.items.length - 1];
    }
    isEmpty() {
        return this.items.length === 0;
    }
    size() {
        return this.items.length;
    }
    toArray() {
        return [...this.items];
    }
}
// 🔹 Stack Usage Examples
const stack = new Stack();
stack.push(1);
stack.push(2);
stack.push(3);
console.log(stack.pop()); // 3
console.log(stack.peek()); // 2
console.log(stack.size()); // 2
console.log(stack.toArray()); // [1,2]
const strStack = new Stack();
strStack.push("a");
strStack.push("b");
console.log(strStack.peek()); // "b"
// =======================
// (b) Generic Dictionary<K, V>
// =======================
class Dictionary {
    data = {};
    set(key, value) {
        this.data[key] = value;
    }
    get(key) {
        return this.data[key];
    }
    has(key) {
        return key in this.data;
    }
    delete(key) {
        delete this.data[key];
    }
    keys() {
        return Object.keys(this.data);
    }
    values() {
        return Object.values(this.data);
    }
    entries() {
        return Object.entries(this.data);
    }
    forEach(callback) {
        for (const key in this.data) {
            callback(this.data[key], key);
        }
    }
}
// 🔹 Dictionary Usage Examples
const dict = new Dictionary();
dict.set("age", 25);
dict.set("score", 100);
console.log(dict.get("age")); // 25
console.log(dict.has("score")); // true
dict.forEach((value, key) => {
    console.log(key, value);
});
console.log(dict.keys()); // ["age", "score"]
console.log(dict.values()); // [25, 100]
// Factory functions
function ok(value) {
    return { ok: true, value };
}
function err(error) {
    return { ok: false, error };
}
// Utility functions
function unwrap(result) {
    if (result.ok)
        return result.value;
    throw new Error(String(result.error));
}
function map(result, fn) {
    return result.ok ? ok(fn(result.value)) : result;
}
function flatMap(result, fn) {
    return result.ok ? fn(result.value) : result;
}
// 🔹 Result Usage Examples
const r1 = ok(42);
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
const r5 = flatMap(r1, x => x > 40 ? ok(x) : err("too small"));
console.log(r5);
