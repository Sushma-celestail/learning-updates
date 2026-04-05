// Q13. Object Transformer Utilities

// Topics: Object.keys, Object.entries, reduce, Computed Property Names


// Problem Statement:

// Write the following utility functions:

// • pick(obj, keys) — returns a new object with only the specified keys

// • omit(obj, keys) — returns a new object without the specified keys

// • mapKeys(obj, fn) — transforms all keys using a function

// • mapValues(obj, fn) — transforms all values using a function


// Input:

// const user = { firstName: "Alice", lastName: "Smith", age: 25, password: "secret" };


// console.log(pick(user, ["firstName", "lastName"]));

// console.log(omit(user, ["password"]));

// console.log(mapKeys(user, key => key.toUpperCase()));

// console.log(mapValues({ a: 1, b: 2, c: 3 }, val => val * 10));


// Output:

// { firstName: "Alice", lastName: "Smith" }

// { firstName: "Alice", lastName: "Smith", age: 25 }

// { FIRSTNAME: "Alice", LASTNAME: "Smith", AGE: 25, PASSWORD: "secret" }

// { a: 10, b: 20, c: 30 }


// Constraints:

// • Each function must use Object.entries() or Object.keys() with reduce()

// • Use computed property names { [key]: value }

// • Do NOT mutate the original object

// • Each function must be a pure function (no side effects)


// 1. pick → keep only specified keys
function pick(obj, keys) {
    return Object.entries(obj).reduce((acc, [key, value]) => {
        if (keys.includes(key)) {
            acc = { ...acc, [key]: value }; // computed property
        }
        return acc;
    }, {});
}


// 2. omit → remove specified keys
function omit(obj, keys) {
    return Object.entries(obj).reduce((acc, [key, value]) => {
        if (!keys.includes(key)) {
            acc = { ...acc, [key]: value };
        }
        return acc;
    }, {});
}


// 3. mapKeys → transform keys
function mapKeys(obj, fn) {
    return Object.entries(obj).reduce((acc, [key, value]) => {
        const newKey = fn(key);
        acc = { ...acc, [newKey]: value };
        return acc;
    }, {});
}


// 4. mapValues → transform values
function mapValues(obj, fn) {
    return Object.entries(obj).reduce((acc, [key, value]) => {
        const newValue = fn(value);
        acc = { ...acc, [key]: newValue };
        return acc;
    }, {});
}

const user = {
    firstName: "Alice",
    lastName: "Smith",
    age: 25,
    password: "secret"
};

console.log(pick(user, ["firstName", "lastName"]));
console.log(omit(user, ["password"]));
console.log(mapKeys(user, key => key.toUpperCase()));
console.log(mapValues({ a: 1, b: 2, c: 3 }, val => val * 10));
