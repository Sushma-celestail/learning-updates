const form = document.getElementById("form");

// INPUTS
const nameInput = document.getElementById("name");
const nameError = document.getElementById("nameError");

const emailInput = document.getElementById("email");
const emailError = document.getElementById("emailError");

const password = document.getElementById("password");
const strengthText = document.getElementById("strength");

// NAME VALIDATION
nameInput.addEventListener("blur", function () {
    if (nameInput.value.trim() === "") {
        nameError.textContent = "Name is required";
    } else {
        nameError.textContent = "";
    }
});

// EMAIL VALIDATION (Regex + Constraint API)
function validateEmail(emailInput) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!pattern.test(emailInput.value)) {
        emailInput.setCustomValidity("Invalid email format");
        emailError.textContent = "Invalid email format";
    } else {
        emailInput.setCustomValidity("");
        emailError.textContent = "";
    }

    emailInput.reportValidity();
}

emailInput.addEventListener("blur", () => validateEmail(emailInput));

// PASSWORD STRENGTH
password.addEventListener("input", function () {
    const value = password.value;
    let strength = "Weak";

    if (
        value.length >= 8 &&
        /[A-Z]/.test(value) &&
        /[a-z]/.test(value) &&
        /[0-9]/.test(value) &&
        /[^A-Za-z0-9]/.test(value)
    ) {
        strength = "Strong";
    } else if (value.length >= 6) {
        strength = "Medium";
    }

    strengthText.textContent = "Strength: " + strength;
});

// STEP NAVIGATION
function nextStep() {
    if (nameInput.value.trim() === "") {
        nameError.textContent = "Name required";
        return;
    }

    document.getElementById("step1").style.display = "none";
    document.getElementById("step2").style.display = "block";
}

// FORM SUBMIT + FormData
form.addEventListener("submit", function (e) {
    e.preventDefault();

    validateEmail(emailInput);

    if (!form.checkValidity()) return;

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    console.log("Final Data:", data);
});