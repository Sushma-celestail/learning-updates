// Q12. Config Builder with Destructuring

// Topics: Destructuring, Default Values, Spread, Object.freeze


// Problem Statement:

// Write a createConfig(options) function that accepts an options object and applies multi-level defaults using destructuring. Return a frozen config object.


// Input:

// const config1 = createConfig({

// server: { port: 9090 },

// logging: { level: "debug" }

// });

// console.log(config1);


// const config2 = createConfig({});

// console.log(config2);


// config2.server.port = 9999; // Should throw or silently fail

// console.log(config2.server.port); // Still 3000


// Output:

// { server: { port: 9090, host: "localhost" },

// database: { url: "postgres://localhost:5432/mydb", poolSize: 5 },

// logging: { level: "debug", file: "app.log" } }

// { server: { port: 3000, host: "localhost" },

// database: { url: "postgres://localhost:5432/mydb", poolSize: 5 },

// logging: { level: "info", file: "app.log" } }

// 3000


// Constraints:

// • Use nested destructuring with default values in the function signature

// • Defaults: server (port: 3000, host: "localhost"), database (url: "postgres://localhost:5432/mydb", poolSize: 5), logging (level: "info", file: "app.log")

// • Use Object.freeze() on the returned config (deep freeze — nested objects too)

// • Do NOT use any external library


// Deep freeze helper (recursive)
function deepFreeze(obj) {
    if (obj && typeof obj === "object" && !Object.isFrozen(obj)) {
        Object.freeze(obj);
        for (let key of Object.keys(obj)) {
            deepFreeze(obj[key]);
        }
    }
    return obj;
}

function createConfig({
    server: {
        port = 3000,
        host = "localhost"
    } = {},
    database: {
        url = "postgres://localhost:5432/mydb",
        poolSize = 5
    } = {},
    logging: {
        level = "info",
        file = "app.log"
    } = {}
} = {}) {

    const config = {
        server: { port, host },
        database: { url, poolSize },
        logging: { level, file }
    };

    return deepFreeze(config);
}


const config1 = createConfig({
    server: { port: 9090 },
    logging: { level: "debug" }
});

console.log(config1);

const config2 = createConfig({});
console.log(config2);

// odification (will fail silently or throw in strict mode)
config2.server.port = 9999;

console.log(config2.server.port); // still 3000