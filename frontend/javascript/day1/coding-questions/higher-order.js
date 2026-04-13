// function operate(a, b, operation) {
//   return operation(a, b);
// }

// // Different operations
// const add = (x, y) => x + y;
// const multiply = (x, y) => x * y;

// console.log(operate(5, 3, add));       // 8
// console.log(operate(5, 3, multiply));  // 15



function operate(a, b, operation) {
  return operation(a, b);
}

const add = (x, y) => x + y;

console.log(operate(5, 3, add));      // 8

console.log('start');

setTimeout(() => {
  console.log('callback!');
}, 2000);

console.log('end');