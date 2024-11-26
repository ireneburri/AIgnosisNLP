let selectedModel = localStorage.getItem('selectedModel') || 'gpt-4o-mini';
document.getElementById('modelSelect').value = selectedModel;
document.getElementById('modelSelect').addEventListener('change', function() {
    selectedModel = this.value; 
    localStorage.setItem('selectedModel', selectedModel); 
    location.reload(); 
});

document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
        document.getElementById('user-input').disabled = true;
    }
});

function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    const model= document.getElementById('modelSelect').value;

    console.log('User input:', message);

    if (message === "") return;

    appendMessage('user', message);
    input.value = '';

    
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({answer: message, model: model})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.message === "Next Question" && data.question) {
            appendMessage('doctor', data.question);
            document.getElementById('user-input').disabled = false;
            document.getElementById('user-input').focus();

        } else if (data.message === "Diagnosis" && data.diagnosis) {
            appendMessage('doctor', data.diagnosis);
            console.log(data.diagnosis);
            
            // Optional: Disable input if it's the final diagnosis
            input.disabled = true;  
            document.getElementById('send-button').disabled = true;

            startAgain();
        } else {
            // Handle any unexpected cases
            appendMessage('system', 'Unexpected response from the server.');
        }
        const unityIframe = document.querySelector('.unity-section iframe');
        if (unityIframe && data.audio_url) {
            console.log("Call the Say function")
            unityIframe.contentWindow.postMessage({
                type: 'Say',
                audioUrl: data.audio_url
            }, '*');
        }
    })
    .catch(error => {
        appendMessage('system', 'There was a problem with your request.');
        console.error('Error:', error);
    });

}

function appendMessage(sender, message) {
    const chatLog = document.getElementById('chat-log');

    // Create the message container element
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);

    // Create the speech bubble
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');

    // Check if the message contains a diagnosis
    if (message.startsWith("**Diagnosis**")) {
        const diagnosisParts = message.split("\n");

        // Create content for the diagnosis
        diagnosisParts.forEach(part => {
            const textElement = document.createElement('div');

            if (part.startsWith("**Diagnosis**")) {
                textElement.innerHTML = `<strong>Diagnosis:</strong> ${part.replace("**Diagnosis**: ", "")}`;
            } else if (part.startsWith("**Recommendations**")) {
                textElement.innerHTML = `<strong>Recommendations:</strong> ${part.replace("**Recommendations**:", "")}`;
            } else if (part.startsWith("**Specialist**")) {
                textElement.innerHTML = `<strong>Specialist:</strong> ${part.replace("**Specialist**: ", "")}`;
            } else {
                textElement.textContent = part;
            }

            bubble.appendChild(textElement);
        });

        // Add "Save as PDF" button
        const pdfButton = document.createElement('button');
        pdfButton.textContent = 'Save as PDF';
        pdfButton.classList.add('pdf-button');
        pdfButton.style = 'border-radius: 4px; padding: 4px 8px; margin-top: 8px;';
        pdfButton.addEventListener('click', () => saveDiagnosisAsPDF(message));
        bubble.appendChild(pdfButton);
        
    } else {
        // Display as a regular message
        bubble.textContent = message;
    }

    // Add the speech bubble to the message container
    messageElement.appendChild(bubble);

    // Add the message to the chat log
    chatLog.appendChild(messageElement);

    // Automatically scroll to the bottom
    chatLog.scrollTop = chatLog.scrollHeight;
}

// Function to save diagnosis as PDF
function saveDiagnosisAsPDF(diagnosisText) {
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF();

    const lines = diagnosisText.split("\n").map(line => {
        // Format bold text in PDF
        if (line.startsWith("**Diagnosis**")) return `Diagnosis: ${line.replace("**Diagnosis**: ", "")}`;
        if (line.startsWith("**Recommendations**")) return `Recommendations: ${line.replace("**Recommendations**:", "")}`;
        if (line.startsWith("**Specialist**")) return `Specialist: ${line.replace("**Specialist**: ", "")}`;
        return line;
    });

    // Add text lines to PDF
    pdf.setFont("helvetica");
    pdf.setFontSize(12);
    lines.forEach((line, index) => {
        pdf.text(10, 10 + index * 10, line);  // Adjust vertical position for each line
    });

    // Save the PDF
    pdf.save('diagnosis.pdf');
}


function startAgain() {
    const chatLog = document.getElementById('chat-log');

    // Message prompt
    const finalMessage = document.createElement('div');
    finalMessage.classList.add('message', 'doctor');
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.textContent = 'Do you have any more issues you would like to talk about?';
    finalMessage.appendChild(bubble);
    chatLog.appendChild(finalMessage);

    // Yes Button
    const yesButton = document.createElement('button');
    yesButton.textContent = 'Yes';
    yesButton.classList.add('response-button');
    yesButton.addEventListener('click', function() {
        window.location.reload();  // Restart the conversation
    });

    // No Button
    const noButton = document.createElement('button');
    noButton.textContent = 'No';
    noButton.classList.add('response-button');
    noButton.addEventListener('click', function() {
        appendMessage('doctor', 'I hope I was able to help. See you next time!');
        noButton.remove();
    });

    // Container for buttons
    const buttonContainer = document.createElement('div');
    buttonContainer.classList.add('button-container');
    buttonContainer.appendChild(yesButton);
    buttonContainer.appendChild(noButton);

    // Append buttons to chat log
    chatLog.appendChild(buttonContainer);

    // Scroll to bottom to make new content visible
    chatLog.scrollTop = chatLog.scrollHeight;
}

document.getElementById('author-btn').addEventListener('mouseover', function() {
    // Create the tooltip element
    const tooltip = document.createElement('div');
    tooltip.textContent = 'This project was created by Irene Burri and Simon Scherello for the Natural Language Processing course of Reykjavik University to help patients get a preliminary diagnosis. The project uses the OpenAI API to generate responses based on the user input.';
    
    // Style the tooltip
    tooltip.style.position = 'absolute';
    tooltip.style.bottom = '40px';
    tooltip.style.left = '-10px';
    tooltip.style.backgroundColor = 'lightgrey';
    tooltip.style.border = '1px solid black';
    tooltip.style.padding = '8px';
    tooltip.style.boxShadow = '0px 4px 8px rgba(0, 0, 0, 0.1)';
    tooltip.style.whiteSpace = 'pre-wrap'; // Enable multi-line text display
    tooltip.style.color = 'black';
    tooltip.style.width = '200px';
    tooltip.style.borderRadius = '4px';

    this.appendChild(tooltip);
    this.addEventListener('mouseout', function() {
        tooltip.remove();
    });
});

initial_greetings = ["Hello, what seems to be the issue today?",
    "Good morning! How can I assist you with your health today?",
    "Hi, what brings you to see me today?",
    "Hello! What can I help you with today?",
    "Good afternoon. What concerns do you have that you'd like to discuss?",
    "Hi there! How can I support your health today?",
    "Hello, what has brought you in today?",
    "Good morning! How are you feeling, and what can I do for you?",
    "Hi! What’s been bothering you that you'd like me to check out?",
    "Good day. How can I be of assistance with your health concerns today?"]

// main.js (Add at the end of the document)
window.onload = function() {
    document.getElementById('user-input').focus();
    appendMessage('doctor', initial_greetings[Math.floor(Math.random() * initial_greetings.length)]);
};

let typingTimeout;
let isTyping = false;

function startTyping() {
    if (!isTyping) {
        isTyping = true;
        sendMessageToUnity('listen');  // Call the Unity "listen" function when typing starts
    }

    clearTimeout(typingTimeout);

    // Set a timeout to detect when the user has stopped typing
    typingTimeout = setTimeout(() => {
        isTyping = false;
        sendMessageToUnity('idle');  // Set Unity avatar to idle after typing stops
    }, 2000);  // 2-second delay after the last keystroke
}

// Attach the startTyping function to keypress events in the input field
document.getElementById('user-input').addEventListener('input', startTyping);

// Function to send messages to Unity for actions like "listen" or "idle"
function sendMessageToUnity(action) {
    const unityIframe = document.querySelector('.unity-section iframe');
    if (unityIframe && action) {
        unityIframe.contentWindow.postMessage({
            type: action
        }, '*');
    }
}


