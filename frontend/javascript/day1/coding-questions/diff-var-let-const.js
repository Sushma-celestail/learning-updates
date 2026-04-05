// const name="sushma";
// console.log("hello, "+ name +"!");


// // null returns "object" — a famous JS bug from 1995
// // In memory, null was stored as 000... same tag as objects.
// // It was never fixed to preserve backward compatibility.

// // undefined vs null:
// let a;              // undefined — variable exists, no value assigned
// let b = null;       // null — value explicitly set to "nothing"

// a == b;             // true  — both are "empty"
// a === b;            // false — different types
// console.log(a)
// console.log(b)



// var hoistedVar;           // ← declaration silently moved to top
// // let hoistedLet;           ← also hoisted, but stays in TDZ

// console.log(hoistedVar);  // → undefined  (no error)
// console.log(hoistedLet);   //→ ❌ ReferenceError (TDZ)

// hoistedVar = "I'm var";
// let hoistedLet = "I'm let";  //TDZ ends here


// Instead of checking for null explicitly:
if (username !== null && username !== undefined && username !== "") 

// Just write this — falsy catches all empty/missing cases:
if (username) { // runs only if username has a real value
  console.log("Welcome, " + username);
}

// ⚠ Gotcha — empty array [] is truthy!
const items = [];
if (items) {
  console.log("this runs! [] is truthy"); //  runs
}
if (items.length) {
  console.log("this does NOT run"); //  skipped — length 0 is falsy
}
