// Q10. Custom Array Method Implementations

// Topics: Prototypes, Callbacks, this


// Problem Statement:

// Implement your own versions of myMap(), myFilter(), and myReduce() on Array.prototype. Each must accept a callback function and behave identically to the native methods.


// Input:

// const nums = [1, 2, 3, 4, 5];

// console.log(nums.myMap(n => n * 2));

// console.log(nums.myFilter(n => n % 2 === 0));

// console.log(nums.myReduce((acc, n) => acc + n, 0));


// Output:

// [2, 4, 6, 8, 10]

// [2, 4]

// 15


// Constraints:

// • Implement on Array.prototype (e.g., Array.prototype.myMap = function(...))

// • Use this inside the implementation to access the array

// • myMap(callback) — callback receives (element, index, array)

// • myFilter(callback) — callback receives (element, index, array)

// • myReduce(callback, initialValue) — callback receives (accumulator, element, index, array)

// • Do NOT call the native map, filter, or reduce inside your implementations

// ------------------------------
// 1️⃣ myMap
// ------------------------------
Array.prototype.myMap = function (callback) {
    const result = [];

    for (let i = 0; i < this.length; i++) {
        // Skip empty slots (like native map)
        if (i in this) {
            result.push(callback(this[i], i, this));
        }
    }

    return result;
};


// ------------------------------
// 2️⃣ myFilter
// ------------------------------
Array.prototype.myFilter = function (callback) {
    const result = [];

    for (let i = 0; i < this.length; i++) {
        if (i in this) {
            if (callback(this[i], i, this)) {
                result.push(this[i]);
            }
        }
    }

    return result;
};


// ------------------------------
// 3️⃣ myReduce
// ------------------------------
Array.prototype.myReduce = function (callback, initialValue) {
    let accumulator = initialValue;
    let startIndex = 0;

    // If no initial value, use first element
    if (accumulator === undefined) {
        accumulator = this[0];
        startIndex = 1;
    }

    for (let i = startIndex; i < this.length; i++) {
        if (i in this) {
            accumulator = callback(accumulator, this[i], i, this);
        }
    }

    return accumulator;
};


// ------------------------------
// ✅ Test
// ------------------------------
const nums = [1, 2, 3, 4, 5];

console.log(nums.myMap(n => n * 2));
// [2, 4, 6, 8, 10]

console.log(nums.myFilter(n => n % 2 === 0));
// [2, 4]

console.log(nums.myReduce((acc, n) => acc + n, 0));
// 15
