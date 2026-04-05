// Q3. Deep Equality Checker

// Topics: Type Checking, Recursion, Object Comparison


// Problem Statement:

// Write a function deepEqual(a, b) that checks whether two values are deeply equal. It must handle: primitives, arrays (order matters), nested objects, and null.


// Input:

// console.log(deepEqual({ a: 1, b: { c: 2 } }, { a: 1, b: { c: 2 } }));

// console.log(deepEqual([1, [2, 3]], [1, [2, 3]]));

// console.log(deepEqual({ a: 1 }, { a: "1" }));

// console.log(deepEqual(null, null));

// console.log(deepEqual(null, {}));


// Output:

// true

// true

// false

// true

// false


// Constraints:

// • Do NOT use JSON.stringify()

// • Must use recursion for nested structures

// • Must handle null explicitly (since typeof null === "object")

// • Use strict equality (===) for primitives


function deepEqual(a,b){
    //checks strict equality(handles primitives +same refeence)
    if(a===b){
        return true;
    }
    //handles null explicitly
    if(a === null || b === null){
        return false;
    }
    //handling the arrays
    if (typeof a==="object" && typeof b==="object"){
        if (Array.isArray(a)!==Array.isArray(b)){
            return false;
        }
        //get keys
        const keysA=Object.keys(a);
        const keysB=Object.keys(b);

        //compareing the number of keys
        if(keysA.length !== keysB.length){
             return false;
        }
        for(let key of keysA){
            if (!keysB.includes(key)||!deepEqual(a[key],b[key])){
                return false;
            }
    
        }
    }
    return true;
}
console.log(deepEqual({a:1,b:{c:2}},{a:1,b:{c:2}}));
console.log(deepEqual([1, [2, 3]], [1, [2, 3]]));                     // true
console.log(deepEqual({ a: 1 }, { a: "1" }));                         // false
console.log(deepEqual(null, null));                                   // true
console.log(deepEqual(null, {}));   