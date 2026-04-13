

function myDisplayer(some) {
  return "hello " + some;
}

function step1() {
  return Promise.resolve("A");
}

async function run() {
  let value = await step1();          // wait for Promise
  let result = myDisplayer(value);    // use returned value
  console.log(result);                // display output
}

run();