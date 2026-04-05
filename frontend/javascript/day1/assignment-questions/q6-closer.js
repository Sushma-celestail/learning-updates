// Q6. Closure — Wallet with Private State

// Topics: Closures, Data Privacy, Higher-Order Functions


// Problem Statement:

// Create a createWallet(ownerName, initialBalance) function that returns an object with methods: deposit(amount), withdraw(amount), getBalance(), getOwner(), and getHistory(). The balance and transaction history must be fully private.


// Input:

// const wallet = createWallet("Alice", 1000);

// wallet.deposit(500);

// wallet.withdraw(200);

// console.log(wallet.getBalance());

// console.log(wallet.getHistory());

// console.log(wallet.getOwner());

// wallet.withdraw(2000);


// Output:

// 1300

// [

// { type: "deposit", amount: 500, balance: 1500 },

// { type: "withdraw", amount: 200, balance: 1300 }

// ]

// "Alice"

// Error: Insufficient balance. Current balance: 1300


// Constraints:

// • Balance and history must NOT be accessible as properties (true privacy via closure)

// • deposit() and withdraw() must validate: amount > 0, withdrawal cannot exceed balance

// • Throw Error with descriptive messages for invalid operations

// • Each history entry: { type, amount, balance


function createWallet(ownerName, initialBalance) {
    // 🔒 Private variables (NOT accessible outside)
    let balance = initialBalance;
    let history = [];

    // ✅ Validate amount helper
    function validateAmount(amount) {
        if (typeof amount !== "number" || amount <= 0) {
            throw new Error("Amount must be a positive number");
        }
    }

    return {
        // 💰 Deposit
        deposit(amount) {
            validateAmount(amount);

            balance += amount;

            history.push({
                type: "deposit",
                amount: amount,
                balance: balance
            });
        },

        // 💸 Withdraw
        withdraw(amount) {
            validateAmount(amount);

            if (amount > balance) {
                throw new Error(
                    `Insufficient balance. Current balance: ${balance}`
                );
            }

            balance -= amount;

            history.push({
                type: "withdraw",
                amount: amount,
                balance: balance
            });
        },

        // 📊 Get Balance
        getBalance() {
            return balance;
        },

        // 👤 Get Owner
        getOwner() {
            return ownerName;
        },

        // 📜 Get History
        getHistory() {
            // return a copy to avoid external mutation
            return [...history];
        }
    };
}


// ------------------------------
// ✅ Usage
// ------------------------------

const wallet = createWallet("Alice", 1000);

wallet.deposit(500);
wallet.withdraw(200);

console.log(wallet.getBalance()); 
// 1300

console.log(wallet.getHistory());
// [
//   { type: "deposit", amount: 500, balance: 1500 },
//   { type: "withdraw", amount: 200, balance: 1300 }
// ]

console.log(wallet.getOwner());
// "Alice"

try {
    wallet.withdraw(2000);
} catch (e) {
    console.log(e.message);
}
// Error: Insufficient balance. Current balance: 1300
