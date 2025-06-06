const statusEl = document.getElementById("status");
const txContainer = document.getElementById("transactions");

const ws = new WebSocket("ws://localhost:8765");

ws.onopen = () => {
  statusEl.textContent = "Connected to Catcoin node";
  ws.send(JSON.stringify({ op: "unconfirmed_sub" }));
  ws.send(JSON.stringify({ op: "blocks_sub" }));
};

ws.onclose = () => {
  statusEl.textContent = "Connection closed";
};

ws.onerror = (e) => {
  statusEl.textContent = "Connection error";
  console.error("WebSocket error", e);
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.op === "utx") {
    const value = data.x.out.reduce((sum, output) => sum + output.value, 0);
    const amount = value / 100000000; // satoshis to Catcoin

    const div = document.createElement("div");
    div.className = "tx";
    div.textContent = `💰 New transaction: ${amount.toFixed(8)} CAT`;
    txContainer.prepend(div);

    // Optional: play a sound or show animation
  } else if (data.op === "block") {
    const blockHeight = data.x.height;
    const div = document.createElement("div");
    div.className = "tx";
    div.textContent = `📦 New block: Height ${blockHeight}`;
    txContainer.prepend(div);
  }
};
