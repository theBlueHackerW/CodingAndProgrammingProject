document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("createAccountForm");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirmPassword");
    const email = document.getElementById("email");
    const username = document.getElementById("username");
    const securityCode = document.getElementById("securityCode");  // Reference to the security code input
    const errorContainer = document.getElementById("errorContainer");

    // Function to validate email format using a regular expression
    function isValidEmail(emailValue) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(emailValue);
    }

    // Function to display error messages in the error container
    function displayErrors(errors) {
        errorContainer.innerHTML = errors.map(error => `<p class="error">${error}</p>`).join("");
    }

    // Function to check for duplicate usernames or emails using AJAX
    function checkDuplicates() {
        const usernameVal = username.value.trim();
        const emailVal = email.value.trim();

        if (usernameVal || emailVal) {
            fetch('/check_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username: usernameVal, email: emailVal })
            })
            .then(response => response.json())
            .then(data => {
                if (data.errors && Object.keys(data.errors).length > 0) {
                    const duplicateErrors = Object.values(data.errors);
                    displayErrors(duplicateErrors);
                } else {
                    errorContainer.innerHTML = "";
                }
            })
            .catch(err => console.error("Error checking duplicates:", err));
        }
    }

    // Validate form on submission
    form.addEventListener("submit", (event) => {
        let isValid = true;
        const errors = [];

        // Clear previous errors
        errorContainer.innerHTML = "";

        // Validate email format
        if (!isValidEmail(email.value)) {
            errors.push("Invalid email format.");
            isValid = false;
        }

        // Validate that passwords match
        if (password.value !== confirmPassword.value) {
            errors.push("Passwords do not match.");
            isValid = false;
        }

        // Validate password strength (minimum 8 characters)
        if (password.value.length < 8) {
            errors.push("Password must be at least 8 characters long.");
            isValid = false;
        }

        // Validate the security code (exactly 4 digits)
        if (!/^\d{4}$/.test(securityCode.value)) {
            errors.push("Security code must be exactly 4 digits.");
            isValid = false;
        }

        // If there are any errors, prevent form submission and display errors
        if (!isValid) {
            event.preventDefault();
            displayErrors(errors);
        }
    });
});
