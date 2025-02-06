// Existing transaction modal functions and sets the front end for each table
function openAddTransactionModal() {
    document.getElementById('modalTitle').innerText = "Add Transaction";
    document.getElementById('transactionForm').action = "/add_transaction";
    document.getElementById('tx_id').value = "";
    document.getElementById('amount').value = "";
    document.getElementById('category').value = "";
    document.getElementById('transaction_type').value = "income";
    document.getElementById('recurrence').value = 0;
    document.getElementById('description').value = "";
    document.getElementById('transactionModal').style.display = "block";
}

//Same as adding but edits and existing transaction
function openEditTransactionModal(id, category, amount, type, description, recurrence) {
    document.getElementById('modalTitle').innerText = "Edit Transaction";
    document.getElementById('transactionForm').action = "/edit_transaction/" + id;
    document.getElementById('tx_id').value = id;
    document.getElementById('amount').value = Math.abs(amount);  // Display positive value for editing
    document.getElementById('category').value = category;
    document.getElementById('transaction_type').value = type;
    document.getElementById('recurrence').value = recurrence;
    document.getElementById('description').value = description;
    document.getElementById('transactionModal').style.display = "block";
}

function closeTransactionModal() {
    document.getElementById('transactionModal').style.display = "none";
}

// Chatbot window opens

function toggleChatbotWindow() {
    var chatbotWindow = document.getElementById("chatbotWindow");
    if (chatbotWindow.style.display === "none" || chatbotWindow.style.display === "") {
        chatbotWindow.style.display = "flex";
    } else {
        chatbotWindow.style.display = "none";
    }
  }
//Sends the inputted values to the backend, which is then taken to the AI bot's generate_response()
function sendChatbotQuery() {
    const inputField = document.getElementById("chatbotInput");
    const question = inputField.value;
    const chatbotResponse = document.getElementById("chatbotResponse");
    if (question.trim() === "") {
        chatbotResponse.innerHTML = "<p>Please enter a question.</p>";
        return;
    }
    //Uses post method to send the question and retreive answer
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: question })
    })
    //collects the response an puts it onto the HTML page
    .then(response => response.json())
    .then(data => {
        chatbotResponse.innerHTML = "<p>" + data.answer + "</p>";
    })
    //Syntatic error handling
    .catch(error => {
        chatbotResponse.innerHTML = "<p>Error: " + error + "</p>";
    });
}
