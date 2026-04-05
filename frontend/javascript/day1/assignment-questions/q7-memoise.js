// Q7. Closure — Memoize Function

// Topics: Closures, Caching, Higher-Order Functions


// Problem Statement:

// Write a memoize(fn) function that returns a memoized version of any single-argument function. The memoized function should cache results and return the cached value if the same argument is passed again. Log "Cache hit" or "Computing" on each call.


// Input:

// const slowSquare = (n) => {

// for (let i = 0; i < 1e8; i++) {} // simulate slow

// return n * n;

// };

// const fastSquare = memoize(slowSquare);

// console.log(fastSquare(5));

// console.log(fastSquare(5));

// console.log(fastSquare(10));


// Output:

// Computing: 5

// 25

// Cache hit: 5

// 25

// Computing: 10

// 100


// Constraints:

// • Use a closure to store the cache object

// • Cache key is the stringified argument

// • Log "Computing: <arg>" on miss and "Cache hit: <arg>" on hit

// • Must work for any single-argument function



