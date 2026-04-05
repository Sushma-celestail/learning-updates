// Imagine a user's score — 0 is a valid score!
const score = 0;

// ❌ || replaces 0 because 0 is falsy
const result1 = score || "No score yet";   // "No score yet" — WRONG!

// ✅ ?? only replaces if score is null or undefined
const result2 = score ?? "No score yet";   // 0 — CORRECT!

// ?? only triggers for null and undefined — nothing else
null      ?? "fallback"   // → "fallback"
undefined ?? "fallback"   // → "fallback"
0         ?? "fallback"   // → 0   (0 is kept)
""        ?? "fallback"   // → ""  ("" is kept)



console.log(0 && "hello");      // → 0        (0 is falsy, stops here)
console.log("hi" && "there");   // → "there"  (both truthy, returns last)
console.log(null && doThing()); // → null      (doThing() never called!)