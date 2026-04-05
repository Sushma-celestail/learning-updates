// Q9. Utility Functions with Array Methods

// Topics: reduce, Set, flat, Callbacks


// Problem Statement:

// Write the following utility functions using only array methods (no for/while loops):

// • groupBy(arr, key) — groups an array of objects by a given key property (use reduce)

// • unique(arr) — returns unique values preserving order (use filter with indexOf)

// • chunk(arr, size) — splits an array into chunks of the given size (use reduce)

// • zip(arr1, arr2) — combines two arrays into an array of pairs (use map)


// Input:

// const people = [

// { name: "Alice", dept: "Engineering" },

// { name: "Bob", dept: "Marketing" },

// { name: "Carol", dept: "Engineering" },

// { name: "Dave", dept: "Marketing" },

// { name: "Eve", dept: "HR" },

// ];

// console.log(groupBy(people, "dept"));

// console.log(unique([1, 2, 2, 3, 4, 4, 5]));

// console.log(chunk([1, 2, 3, 4, 5, 6, 7], 3));

// console.log(zip(["a", "b", "c"], [1, 2, 3]));


// Output:

// { Engineering: [{...}, {...}], Marketing: [{...}, {...}], HR: [{...}] }

// [1, 2, 3, 4, 5]

// [[1, 2, 3], [4, 5, 6], [7]]

// [["a", 1], ["b", 2], ["c", 3]]


// Constraints:

// • Each function must use array methods only (no for/while)

// • groupBy must use reduce

// • chunk must use reduce

// • unique must NOT use Set — use filter with indexOf


// ------------------------------
// 1️⃣ groupBy (using reduce)
// ------------------------------
function groupBy(arr, key) {
    return arr.reduce((acc, item) => {
        const groupKey = item[key];

        if (!acc[groupKey]) {
            acc[groupKey] = [];
        }

        acc[groupKey].push(item);

        return acc;
    }, {});
}


// ------------------------------
// 2️⃣ unique (using filter + indexOf)
// ------------------------------
function unique(arr) {
    return arr.filter((item, index) => arr.indexOf(item) === index);
}


// ------------------------------
// 3️⃣ chunk (using reduce)
// ------------------------------
function chunk(arr, size) {
    return arr.reduce((acc, item, index) => {
        const chunkIndex = Math.floor(index / size);

        if (!acc[chunkIndex]) {
            acc[chunkIndex] = [];
        }

        acc[chunkIndex].push(item);

        return acc;
    }, []);
}


// ------------------------------
// 4️⃣ zip (using map)
// ------------------------------
function zip(arr1, arr2) {
    return arr1.map((item, index) => [item, arr2[index]]);
}


// ------------------------------
// ✅ Test Input
// ------------------------------
const people = [
    { name: "Alice", dept: "Engineering" },
    { name: "Bob", dept: "Marketing" },
    { name: "Carol", dept: "Engineering" },
    { name: "Dave", dept: "Marketing" },
    { name: "Eve", dept: "HR" },
];

console.log(groupBy(people, "dept"));

console.log(unique([1, 2, 2, 3, 4, 4, 5]));

console.log(chunk([1, 2, 3, 4, 5, 6, 7], 3));

console.log(zip(["a", "b", "c"], [1, 2, 3]));
