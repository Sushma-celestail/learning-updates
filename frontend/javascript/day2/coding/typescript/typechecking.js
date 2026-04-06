"use strict";
function greet(name, age) {
    if (typeof age === "number") {
        return `Hello ${name}, you are ${age} years old.`;
    }
    return `Hello ${name}!`;
}
console.log(greet('sushma', 32));
console.log(greet("Charlie", "twenty"));
