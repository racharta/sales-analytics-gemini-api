import { streamGemini } from './gemini-api.js';

// Get the modal element
const modal = document.getElementById("modal");

// Get the history button element
const historyButton = document.getElementById("history-button");

// Get the close button element
const closeButton = document.getElementById("close-modal");

const output = document.getElementById('output');

const promptInput = document.getElementById('user-input');

// Open the modal when the history button is clicked
historyButton.addEventListener("click", () => {
  modal.classList.add("show");
});

// Close the modal when the close button is clicked
closeButton.addEventListener("click", () => {
  modal.classList.remove("show");
});

const chatForm = document.getElementById('chat-form')
chatForm.onsubmit = async (ev) => {
  ev.preventDefault();
  output.textContent = 'Generating...';
  try {

    // Assemble the prompt by combining the text with the chosen image
    let contents = [
      {
        role: 'user',
        parts: [
          { text: promptInput.value }
        ]
      },
    ];
    
    // Call the multimodal model, and get a stream of results
    let stream = streamGemini({
      model: 'gemini-1.5-flash', // or gemini-1.5-pro
      contents,
    });

    // Read from the stream and interpret the output as markdown
    let buffer = [];
    let md = new markdownit();
    for await (let chunk of stream) {
      buffer.push(chunk);
      output.innerHTML = md.render(buffer.join(''));
    }
  } catch (e) {
    output.innerHTML += '<hr>' + e;
  }
}