function greet(name, greeting = "Hello") {
  return `${greeting}, ${name}!`;
}

// Calling with both arguments
console.log(greet("Sushma", "Hi")); 
// 👉 Hi, Sushma!

// Calling with default greeting
console.log(greet("Sushma")); 
// 👉 Hello, Sushma!

console.log(greet())