//Q2. Truthy/Falsy Filter & Null Replacer

// Topics: Truthy/Falsy, filter(), Nullish Values


// Problem Statement:

// Write two functions:

// (a) cleanData(arr) — returns a new array with all falsy values removed.

// (b) replaceNulls(arr, replacement) — replaces only null and undefined with the replacement value, keeping other falsy values (0, "", false) intact.


// Input:

// const data = [0, "hello", null, 42, "", undefined, false, "world", NaN];

// console.log(cleanData(data));

// console.log(replaceNulls(data, "N/A"));


// Output:

// ["hello", 42, "world"]

// [0, "hello", "N/A", 42, "", "N/A", false, "world", NaN]


// Constraints:

// • cleanData must use filter() in a single line

// • replaceNulls must use map() and check specifically for null and undefined (using == null)

// • Do NOT modify the original array



//it removes all the false values 
function cleanData(arr){
    return arr.filter(Boolean);
}

//replace only null and undefined
function replaceNulls(arr,replacement){
    return arr.map(value => value ==null ? replacement :value);
}
//test data
const data=[0,"hello",null,42,"",undefined,false,"world",NaN];

console.log(cleanData(data));
console.log(replaceNulls(data,"N/A"));