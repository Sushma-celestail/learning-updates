// ==============================
// FIX 1: Using bind(this)
// ==============================

const timer1 = {

    seconds: 0,              // counter to track seconds
    intervalId: null,        // will store interval ID for stopping later

    start: function () {

        // setInterval runs every 1000ms (1 second)
        // .bind(this) ensures 'this' inside callback refers to timer1
        this.intervalId = setInterval(function () {

            this.seconds++;  // increment seconds on timer1 object
            console.log(`Elapsed: ${this.seconds}s`);

        }.bind(this), 1000); // bind(this) fixes lost context

    },

    stop: function () {
        // clearInterval stops the running interval using stored ID
        clearInterval(this.intervalId);
    }
};



// ==============================
// FIX 2: Using Arrow Function
// ==============================

const timer2 = {

    seconds: 0,
    intervalId: null,

    start: function () {

        // Arrow function does NOT have its own 'this'
        // It takes 'this' from surrounding scope (timer2)
        this.intervalId = setInterval(() => {

            this.seconds++;  // correctly refers to timer2.seconds
            console.log(`Elapsed: ${this.seconds}s`);

        }, 1000);

    },

    stop: function () {
        clearInterval(this.intervalId);
    }
};



// ==============================
// FIX 3: Using const self = this
// ==============================

const timer3 = {

    seconds: 0,
    intervalId: null,

    start: function () {

        const self = this; // store reference to timer3 object

        // normal function has its own 'this' (wrong context)
        // so we use 'self' instead of 'this'
        this.intervalId = setInterval(function () {

            self.seconds++;  // use self to access correct object
            console.log(`Elapsed: ${self.seconds}s`);

        }, 1000);

    },

    stop: function () {
        clearInterval(this.intervalId);
    }
};



// ==============================
// USAGE EXAMPLE
// ==============================

// Start any one timer
timer1.start();

// Stop after 5 seconds (example)
setTimeout(() => {
    timer1.stop();
    console.log("Timer stopped");
}, 5000);