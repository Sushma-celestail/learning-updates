// Section A — Variables, Types & Operators

// Q1. Type Checker Utility

// Topics: Data Types, typeof, Strict Equality


// Problem Statement:

// Write a function describeType(value) that takes any value and returns a string describing its type with additional detail: "null", "array", "object", "function", "NaN", "undefined", "string", "number", "boolean", "bigint", "symbol".


// Input:

// console.log(describeType(42));

// console.log(describeType("hello"));

// console.log(describeType(null));

// console.log(describeType([1, 2]));

// console.log(describeType(NaN));

// console.log(describeType({ a: 1 }));

// console.log(describeType(undefined));

// console.log(describeType(() => {}));


// Output:

// "number"

// "string"

// "null"

// "array"

// "NaN"

// "object"

// "undefined"

// "function"


// Constraints:

// • Use ===, typeof, Array.isArray(), and Number.isNaN()

// • Must correctly identify null (not "object"), NaN (not "number"), and arrays (not "object")

// • Do NOT use any external library
function describeType(value){
    if(value===null){
        return "null";
    }
    if (Number.isNaN(value)){
        return "NaN";
    }
    if(Array.isArray(value)){
        return "array";
    }
    const type=typeof value;

    return type;
}

console.log(describeType(42));           // "number"
console.log(describeType("hello"));      // "string"
console.log(describeType(null));         // "null"
console.log(describeType([1, 2]));       // "array"
console.log(describeType(NaN));          // "NaN"
console.log(describeType({ a: 1 }));     // "object"
console.log(describeType(undefined));    // "undefined"
console.log(describeType(() => {}));     // "function"
