// Navigation functions
function goToLogin() {
  window.location.href = "/login";
}

function goToCreateAccount() {
  window.location.href = "/create_account";
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
//Sends the user's input to the backend, then to chatbot
function sendChatbotQuery() {
  const inputField = document.getElementById("chatbotInput");
  const question = inputField.value;
  const chatbotResponse = document.getElementById("chatbotResponse");

  if (question.trim() === "") {
      chatbotResponse.innerHTML += "<p>Please enter a question.</p>";
      return;
  }

  //Displays the response from the AI
  fetch("/chat", {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify({ question: question })
  })
  .then(response => response.json())
  .then(data => {
      chatbotResponse.innerHTML += `<p><b>You:</b> ${question}</p>`;
      chatbotResponse.innerHTML += `<p><b>Bot:</b> ${data.answer}</p>`;
  })
  //Syntatic error handling
  .catch(error => {
      chatbotResponse.innerHTML += `<p>Error: ${error}</p>`;
  });

  inputField.value = "";  // Clear input field after sending
}

