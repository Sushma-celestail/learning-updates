// Section D — Objects & Destructuring

// Q11. Object Deep Merge

// Topics: Objects, Recursion, Spread Operator, Type Checking


// Problem Statement:

// Write a function deepMerge(target, source) that deeply merges two objects. Nested objects should be merged recursively. Arrays should be concatenated. Primitive values from source should override target.


// Input:

// const defaults = {

// server: { port: 3000, host: "localhost" },

// database: { url: "localhost:5432", pool: { min: 2, max: 5 } },

// features: ["auth"],

// };

// const overrides = {

// server: { port: 8080 },

// database: { pool: { max: 20 } },

// features: ["logging"],

// debug: true,

// };

// console.log(deepMerge(defaults, overrides));


// Output:

// {

// server: { port: 8080, host: "localhost" },

// database: { url: "localhost:5432", pool: { min: 2, max: 20 } },

// features: ["auth", "logging"],

// debug: true

// }


// Constraints:

// • Use recursion for nested objects

// • Arrays must be concatenated, not overwritten

// • Must handle null (treat as a primitive, not an object)

// • Do NOT mutate the original target or source objects

// • Must work for any depth of nesting 


function deepMerge(target, source) {
    // Helper to check if value is a plain object
    const isObject = (val) => {
        return val !== null && typeof val === "object" && !Array.isArray(val);
    };

    // Create a new result object (avoid mutation)
    const result = { ...target };

    for (let key in source) {
        const targetValue = target[key];
        const sourceValue = source[key];

      
        if (Array.isArray(targetValue) && Array.isArray(sourceValue)) {
            result[key] = [...targetValue, ...sourceValue];
        }

        else if (isObject(targetValue) && isObject(sourceValue)) {
            result[key] = deepMerge(targetValue, sourceValue);
        }

        else {
            result[key] = sourceValue;
        }
    }

    return result;
}

const defaults = {
    server: { port: 3000, host: "localhost" },
    database: { url: "localhost:5432", pool: { min: 2, max: 5 } },
    features: ["auth"],
};

const overrides = {
    server: { port: 8080 },
    database: { pool: { max: 20 } },
    features: ["logging"],
    debug: true,
};

console.log(deepMerge(defaults, overrides));