// // ------------------------------
// // ✅ Hoisting Demo (Declaration)
// // ------------------------------

// // Calling BEFORE definition (works due to hoisting)
// const prices = [500, 300, 200];

// console.log(calculateTotal(prices, 0.18, 50, 30)); // 1085.6
// console.log(calculateTotal(prices));               // 1180
// console.log(calculateTotal(prices, 0.05));         // 1050


// // ------------------------------
// // 1️⃣ Function Declaration
// // ------------------------------
// function calculateTotal(prices, taxRate = 0.18, ...discounts) {
//     // Sum prices
//     let total = prices.reduce((sum, price) => sum + price, 0);

//     // Apply discounts
//     for (let discount of discounts) {
//         total -= discount;
//     }

//     // Clamp (cannot go below 0)
//     total = Math.max(0, total);

//     // Apply tax
//     return total * (1 + taxRate);
// }


// // ------------------------------
// // ❌ Calling Expression BEFORE definition (ERROR)
// // ------------------------------
// try {
//     console.log(calculateTotalExp(prices));
// } catch (e) {
//     console.log("Expression Error:", e.message);
// }


// // ------------------------------
// // 2️⃣ Function Expression
// // ------------------------------
// const calculateTotalExp = function (prices, taxRate = 0.18, ...discounts) {
//     let total = prices.reduce((sum, price) => sum + price, 0);

//     for (let discount of discounts) {
//         total -= discount;
//     }

//     total = Math.max(0, total);

//     return total * (1 + taxRate);
// };


// // ------------------------------
// // ❌ Calling Arrow BEFORE definition (ERROR)
// // ------------------------------
// try {
//     console.log(calculateTotalArrow(prices));
// } catch (e) {
//     console.log("Arrow Error:", e.message);
// }


// // ------------------------------
// // 3️⃣ Arrow Function
// // ------------------------------
// const calculateTotalArrow = (prices, taxRate = 0.18, ...discounts) => {
//     let total = prices.reduce((sum, price) => sum + price, 0);

//     for (let discount of discounts) {
//         total -= discount;
//     }

//     total = Math.max(0, total);

//     return total * (1 + taxRate);
// };


// ------------------------------
// ✅ Hoisting Demo (Declaration)
// ------------------------------

// Calling BEFORE definition (works due to hoisting)
const prices = [500, 300, 200];

console.log(calculateTotal(prices, 0.18, 50, 30)); // 1085.6
console.log(calculateTotal(prices));               // 1180
console.log(calculateTotal(prices, 0.05));         // 1050


// ------------------------------
// 1️⃣ Function Declaration
// ------------------------------
function calculateTotal(prices, taxRate = 0.18, ...discounts) {
    // Sum prices
    let total = prices.reduce((sum, price) => sum + price, 0);

    // Apply discounts
    for (let discount of discounts) {
        total -= discount;
    }

    // Clamp (cannot go below 0)
    total = Math.max(0, total);

    // Apply tax
    return total * (1 + taxRate);
}


// ------------------------------
// ❌ Calling Expression BEFORE definition (ERROR)
// ------------------------------
try {
    console.log(calculateTotalExp(prices));
} catch (e) {
    console.log("Expression Error:", e.message);
}


// ------------------------------
// 2️⃣ Function Expression
// ------------------------------
const calculateTotalExp = function (prices, taxRate = 0.18, ...discounts) {
    let total = prices.reduce((sum, price) => sum + price, 0);

    for (let discount of discounts) {
        total -= discount;
    }

    total = Math.max(0, total);

    return total * (1 + taxRate);
};


// ------------------------------
// ❌ Calling Arrow BEFORE definition (ERROR)
// ------------------------------
try {
    console.log(calculateTotalArrow(prices));
} catch (e) {
    console.log("Arrow Error:", e.message);
}


// ------------------------------
// 3️⃣ Arrow Function
// ------------------------------
const calculateTotalArrow = (prices, taxRate = 0.18, ...discounts) => {
    let total = prices.reduce((sum, price) => sum + price, 0);

    for (let discount of discounts) {
        total -= discount;
    }

    total = Math.max(0, total);

    return total * (1 + taxRate);
};