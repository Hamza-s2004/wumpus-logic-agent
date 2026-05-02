let rows, cols;
let agent = {x: 0, y: 0};

function createGrid() {
    rows = +document.getElementById("rows").value;
    cols = +document.getElementById("cols").value;

    let grid = document.getElementById("grid");
    grid.innerHTML = "";
    grid.style.gridTemplateColumns = `repeat(${cols}, 50px)`;

    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            let cell = document.createElement("div");
            cell.classList.add("cell");
            cell.id = `cell-${i}-${j}`;
            cell.onclick = () => moveAgent(i, j);
            grid.appendChild(cell);
        }
    }

    agent = {x: 0, y: 0};
    updateUI();
}

async function moveAgent(x, y) {
    let res = await fetch("/check", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({x, y})
    });

    let data = await res.json();

    let cell = document.getElementById(`cell-${x}-${y}`);

    if (data.safe) {
        agent = {x, y};
        cell.classList.add("safe");

        document.getElementById("info").innerText =
            `SAFE | Breeze:${data.breeze} | Stench:${data.stench}`;
    } else {
        cell.classList.add("danger");

        document.getElementById("info").innerText =
            `NOT SAFE`;
    }

    document.getElementById("steps").innerText =
        "Inference Steps: " + data.steps;

    updateUI();
}

function updateUI() {
    document.querySelectorAll(".cell").forEach(c => {
        c.classList.remove("agent");
        c.innerText = "";
    });

    let id = `cell-${agent.x}-${agent.y}`;
    let cell = document.getElementById(id);
    cell.classList.add("agent");
    cell.innerText = "A";
}