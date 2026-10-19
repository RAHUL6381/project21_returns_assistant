
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");
const chatBody = document.getElementById("chatBody");
const sendButton = document.getElementById("sendButton");
const chatWidget = document.getElementById("chatWidget");

const HISTORY_KEY = "returns_assistant_history";
const MAX_PAIRS = 7;

let history = [];

try {
    history = JSON.parse(sessionStorage.getItem(HISTORY_KEY) || "[]");

    if (!Array.isArray(history)) {
        history = [];
    }
} catch {
    history = [];
}

function saveHistory() {
    history = history.slice(-MAX_PAIRS);

    try {
        sessionStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    } catch (error) {
        console.warn("Chat history could not be saved.", error);
    }
}

function scrollToLatest() {
    chatBody.scrollTop = chatBody.scrollHeight;
}

function createMessage(role, text, time = new Date()) {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${role}`;

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = text;

    const timestamp = document.createElement("span");
    timestamp.className = "message-time";
    timestamp.textContent = time.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });

    wrapper.append(bubble, timestamp);
    chatMessages.appendChild(wrapper);

    return wrapper;
}

function renderHistory() {
    chatMessages.replaceChildren();

    history.slice(-MAX_PAIRS).forEach((item) => {
        createMessage("user", item.question, new Date(item.time));

        createMessage(
            "assistant",
            item.answer,
            new Date(item.time)
        );
    });

    scrollToLatest();
}

function showTyping() {
    const typing = createMessage("assistant", "Thinking...");

    typing.classList.add("typing-message");
    return typing;
}

async function sendQuestion(question) {
    question = question.trim();

    if (!question || sendButton.disabled) {
        return;
    }

    // Hide quick questions after the first question
    document.querySelector(".quick-questions").style.display = "none";

    createMessage("user", question);
    chatInput.value = "";
    sendButton.disabled = true;

    const typingMessage = showTyping();
    scrollToLatest();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question })
        });

        const data = await response.json();
        typingMessage.remove();

        if (!response.ok) {
            createMessage(
                "assistant",
                data.error || "Sorry, I couldn't answer that question."
            );
            return;
        }

        const time = new Date();

        history.push({
            question,
            answer: data.answer,
            time: time.toISOString()
        });

        saveHistory();

        createMessage("assistant", data.answer, time);
        scrollToLatest();

    } catch (error) {
        typingMessage.remove();

        createMessage(
            "assistant",
            "Unable to connect to the server. Please try again."
        );
    } finally {
        sendButton.disabled = false;
        chatInput.focus();
    }
}

chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    sendQuestion(chatInput.value);
});

document.querySelectorAll(".quick-question").forEach((button) => {
    button.addEventListener("click", () => {
        sendQuestion(button.textContent);
    });
});

document.getElementById("minimizeChat").addEventListener("click", () => {
    chatWidget.classList.toggle("minimized");
});

document.getElementById("openChat").addEventListener("click", () => {
    chatWidget.classList.remove("minimized");
});

document.getElementById("clearChat").addEventListener("click", () => {
    history = [];
    saveHistory();
    renderHistory();
    document.querySelector(".quick-questions").style.display = "flex";
});

renderHistory();
