// ============================================
// IMPORT READLINE (Node.js input system)
// ============================================
const readline = require("readline");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});


// Helper function to ask questions (Promise-based)
function ask(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
}

// ============================================
// 1. QUIZ FUNCTION
// ============================================
async function runQuiz() {
  let score = 0;

  const q1 = await ask("1. What is 2 + 2? ");
  if (q1.trim() === "4") score++;

  const q2 = await ask("2. What is the capital of France? ");
  if (q2.trim().toLowerCase() === "paris") score++;

  const q3 = await ask("3. Is JS a programming language? (yes/no) ");
  if (q3.trim().toLowerCase() === "yes") score++;

  console.log("\n🎯 Quiz Score:", score + "/3\n");
}

// ============================================
// 2. SAFE DELETE (confirm alternative)
// ============================================
async function safeDelete(itemName) {
  const answer = await ask(`Are you sure you want to delete ${itemName}? (yes/no): `);

  if (answer.trim().toLowerCase() === "yes") {
    console.log(itemName + " deleted.");
    return true;
  } else {
    console.log("Deletion cancelled.");
    return false;
  }
}

// ============================================
// 3. GET USER AGE (validated input)
// ============================================
async function getUserAge() {
  while (true) {
    const input = await ask("Enter your age (1 - 120) or type 'cancel': ");

    if (input.toLowerCase() === "cancel") {
      console.log("Operation cancelled.");
      return null;
    }

    const age = Number(input);

    if (!isNaN(age) && age >= 1 && age <= 120) {
      return age;
    } else {
      console.log("❌ Invalid input! Enter a number between 1 and 120.\n");
    }
  }
}

// ============================================
// MAIN FLOW (runs everything in order)
// ============================================
async function main() {
  await runQuiz();

  await safeDelete("File.txt");

  const age = await getUserAge();
  console.log("User age:", age);

  rl.close(); // close readline at end
}

// Run program
main();