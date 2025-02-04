// Navigation functions
function goToLogin() {
  window.location.href = "/login";
}

function goToCreateAccount() {
  window.location.href = "/create_account";
}

// Chatbot window functionality
function toggleChatbotWindow() {
  const chatbotWindow = document.getElementById("chatbotWindow");
  if (chatbotWindow.style.display === "none" || chatbotWindow.style.display === "") {
      chatbotWindow.style.display = "block";
  } else {
      chatbotWindow.style.display = "none";
  }
}

function sendChatbotQuery() {
  const inputField = document.getElementById("chatbotInput");
  const question = inputField.value;
  const chatbotResponse = document.getElementById("chatbotResponse");
  if (question.trim() === "") {
      chatbotResponse.innerHTML = "<p>Please enter a question.</p>";
      return;
  }
    fetch("/chat", {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify({ question: question })
  })
  .then(response => response.json())
  .then(data => {
      chatbotResponse.innerHTML = "<p>" + data.answer + "</p>";
  })
  .catch(error => {
      chatbotResponse.innerHTML = "<p>Error: " + error + "</p>";
  });
}
