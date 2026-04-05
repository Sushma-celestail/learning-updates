// Q5. Scope & Hoisting Bug Fix

// Topics: var vs let, Block Scope, Closures in Loops, setTimeout


// Problem Statement:

// The following code is supposed to print 0, 1, 2, 3, 4 with a 1-second gap — but it prints 5 five times instead. Explain the bug and fix it two ways.


// Input:

// // BUGGY CODE:

// for (var i = 0; i < 5; i++) {

// setTimeout(function () {

// console.log(i);

// }, i * 1000);

// }


// Output:

// 0 (at ~0s)

// 1 (at ~1s)

// 2 (at ~2s)

// 3 (at ~3s)

// 4 (at ~4s)


// Constraints:

// • Fix 1: Replace var with let — explain why this works

// • Fix 2: Keep var but wrap the setTimeout inside an IIFE that captures i

// • Add a comment above each fix explaining the scoping mechanism that makes it wor


// ------------------------------
// ❌ BUGGY CODE
// ------------------------------
// Problem: `var` is function-scoped, so all timeouts share the same `i`
// By the time setTimeout runs, loop is finished and i = 5
// Output: 5 5 5 5 5 ❌

for (var i = 0; i < 5; i++) {
    setTimeout(function () {
        console.log("BUG:", i);
    }, i * 1000);
}


// ------------------------------
// ✅ FIX 1: Using `let`
// ------------------------------
// `let` is block-scoped, so each iteration gets its own copy of `i`
// Each timeout closure captures a different value
// Output: 0 1 2 3 4 ✅

for (let i = 0; i < 5; i++) {
    setTimeout(function () {
        console.log("FIX 1 (let):", i);
    }, i * 1000);
}


// ------------------------------
// ✅ FIX 2: Using IIFE with `var`
// ------------------------------
// IIFE creates a new function scope for each iteration
// Current value of `i` is passed as argument `j`
// Each timeout uses its own `j`
// Output: 0 1 2 3 4 ✅

for (var i = 0; i < 5; i++) {
    (function (j) {
        setTimeout(function () {
            console.log("FIX 2 (IIFE):", j);
        }, j * 1000);
    })(i);
}
