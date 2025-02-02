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

