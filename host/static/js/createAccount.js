// Wait for the DOM to fully load
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("createAccountForm");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirmPassword");
    const email = document.getElementById("email");

    // Function to validate email format
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Validate form on submission
    form.addEventListener("submit", (event) => {
        let isValid = true;
        const errors = [];

        // Check if email format is valid
        if (!isValidEmail(email.value)) {
            errors.push("Invalid email format.");
            isValid = false;
        }

        // Check if passwords match
        if (password.value !== confirmPassword.value) {
            errors.push("Passwords do not match.");
            isValid = false;
        }

        // Check password strength
        if (password.value.length < 8) {
            errors.push("Password must be at least 8 characters long.");
            isValid = false;
        }

        // Display errors if any
        if (!isValid) {
            event.preventDefault();
            alert(errors.join("\n"));
        }
    });
});
