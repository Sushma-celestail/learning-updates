"use strict";
// =======================
// (a) Type Guard
// =======================
function isString(value) {
    return typeof value === "string";
}
// 🔹 Usage Examples
const val1 = "hello";
if (isString(val1)) {
    console.log(val1.toUpperCase()); // OK
}
const val2 = 123;
if (isString(val2)) {
    console.log(val2.toUpperCase()); // Won’t run
}
const val3 = "TypeScript";
console.log(isString(val3)); // true
// =======================
// (b) Generic first/last
// =======================
function first(arr) {
    return arr.length > 0 ? arr[0] : undefined;
}
function last(arr) {
    return arr.length > 0 ? arr[arr.length - 1] : undefined;
}
// 🔹 Usage Examples
console.log(first([1, 2, 3])); // 1
console.log(first(["a", "b"])); // "a"
console.log(first([])); // undefined
console.log(last([1, 2, 3])); // 3
console.log(last(["x", "y"])); // "y"
console.log(last([])); // undefined
function on(eventName, handler) {
    console.log(`Event registered: ${eventName}`);
    // Simulate event trigger
}
// 🔹 Usage Examples
on("click", (data) => {
    console.log(data.x, data.y); // fully typed
});
on("keypress", (data) => {
    console.log(data.key);
});
on("resize", (data) => {
    console.log(data.width, data.height);
});
function createResponse(data, status) {
    return {
        data,
        status,
        success: status >= 200 && status < 300,
    };
}
// 🔹 Usage Examples
const res1 = createResponse({ name: "Alice" }, 200);
console.log(res1.data.name); // typed
const res2 = createResponse([1, 2, 3], 200);
console.log(res2.data[0]); // number
const res3 = createResponse("Error occurred", 500);
console.log(res3.success); // false
