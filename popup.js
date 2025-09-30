document.addEventListener("DOMContentLoaded", async () => {
    // Get references to all the HTML elements
    const chatArea = document.getElementById("chat");
    const questionInput = document.getElementById("question");
    const askBtn = document.getElementById("askBtn");

    let videoId = null;

    try {
        // Get the active tab to find the YouTube video ID
        let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        // Check if it's a valid YouTube video URL and extract the video ID
        if (tab && tab.url && tab.url.includes("youtube.com/watch")) {
            const urlParams = new URLSearchParams(new URL(tab.url).search);
            videoId = urlParams.get("v");
        }
    } catch (e) {
        console.error("Could not query tabs. Are you running this as an extension?", e);
    }
    
    // If we're not on a YouTube video page, show a message and disable the input
    if (!videoId) {
        // Clear any example messages and show the notice
        chatArea.innerHTML = "<div class='bubble bot-message'>This feature only works on a YouTube video page.</div>";
        askBtn.disabled = true;
        questionInput.disabled = true;
        questionInput.placeholder = "Unavailable";
        return;
    }

    // --- Main function to handle the entire question-answer flow ---
    async function handleUserQuestion() {
        const userText = questionInput.value.trim();
        if (!userText) return; // Don't proceed if the input is empty

        // 1. Immediately display the user's question
        displayMessage(userText, "user-message");
        
        // 2. Clear the input field right away
        questionInput.value = "";

        try {
            // 3. Fetch the bot's answer from your API in the background
            const response = await fetch("http://127.0.0.1:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ video_id: videoId, question: userText })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.statusText}`);
            }
            
            const data = await response.json();
            const botResponse = data.answer || "Sorry, I couldn't find an answer.";
            
            // 4. Display the bot's answer when it arrives
            displayMessage(botResponse, "bot-message");

        } catch (err) {
            console.error("API Error:", err);
            displayMessage("Error: Could not connect to the backend service.", "bot-message");
        }
    }

    // --- Helper function to create and add message bubbles to the chat ---
    function displayMessage(text, className) {
        const messageBubble = document.createElement('div');
        messageBubble.classList.add('bubble', className);
        messageBubble.innerText = text;
        chatArea.appendChild(messageBubble);

        // Auto-scroll to the bottom to show the latest message
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    // --- Event Listeners ---
    // Handle clicking the "Ask" button
    askBtn.addEventListener("click", handleUserQuestion);

    // Handle pressing "Enter" in the text area
    questionInput.addEventListener("keyup", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault(); // Prevents adding a new line in the textarea
            handleUserQuestion();
        }
    });
});