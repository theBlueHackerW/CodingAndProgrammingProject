document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');

    loginForm.addEventListener('submit', function(event) {
        const username = document.getElementById('username').value;
        const accountCode = document.getElementById('account_code').value;
        const password = document.getElementById('password').value;
        let hasError = false;
        
        // Example client-side validation
        if (username.trim() === '') {
            alert('Username is required.');
            hasError = true;
        }
        // Validate that the account code is exactly 4 digits
        if (accountCode.trim().length !== 4) {
            alert('Account code must be 4 digits.');
            hasError = true;
        }
        if (password.trim() === '') {
            alert('Password is required.');
            hasError = true;
        }

        if (hasError) {
            event.preventDefault(); // Stop form submission
        }
    });
});
