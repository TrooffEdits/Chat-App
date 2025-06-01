const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("msgInput");
const sendBtn = document.getElementById("sendBtn");

let lastConfirmTime = 0;
let lastMsgId = null;
let popup = document.getElementById("confirmPopup");

function renderMessages(data) {
  messagesEl.innerHTML = "";
  data.forEach(msg => {
    const div = document.createElement("div");
    div.className = "message " + (msg.user === user ? "you" : "other");

    if (msg.user === user) {
      const del = document.createElement("button");
      del.className = "del-btn";
      del.innerHTML = "🗑️";
      del.onclick = () => handleDelete(msg.id);
      div.appendChild(del);
    }

    const span = document.createElement("span");
    span.textContent = msg.text;
    div.appendChild(span);

    const time = document.createElement("small");
    time.textContent = msg.time;
    div.appendChild(time);

    messagesEl.appendChild(div);
  });

  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function handleDelete(msgId) {
  const now = Date.now();
  if (now - lastConfirmTime < 5000 && msgId === lastMsgId) {
    deleteMsg(msgId);
    return;
  }

  lastMsgId = msgId;
  popup.classList.remove("hidden");

  document.getElementById("confirmYes").onclick = () => {
    deleteMsg(msgId);
    popup.classList.add("hidden");
    lastConfirmTime = Date.now();
  };

  document.getElementById("confirmNo").onclick = () => {
    popup.classList.add("hidden");
  };
}

function deleteMsg(id) {
  fetch("/api/delete/" + id, { method: "POST" }).then(loadMessages);
}

function loadMessages() {
  fetch("/api/messages")
    .then(res => res.json())
    .then(renderMessages);
}

function sendMsg() {
  const text = inputEl.value.trim();
  if (!text) return;

  fetch("/api/send", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user, text }),
  }).then(() => {
    inputEl.value = "";
    inputEl.style.height = "auto";
    loadMessages();
  });
}

inputEl.addEventListener("input", () => {
  inputEl.style.height = "auto";
  inputEl.style.height = inputEl.scrollHeight + "px";
});

inputEl.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMsg();
  }
});

sendBtn.onclick = sendMsg;

window.onload = () => {
  loadMessages();
  setInterval(loadMessages, 2000);
};
