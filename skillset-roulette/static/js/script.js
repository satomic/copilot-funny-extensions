// DOM selectors
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
// Removed unused selector for 'winnersList'
const currentPlayerNameElement = document.getElementById("currentPlayerName");
const currentPlayerPrizeElement = document.getElementById("currentPlayerPrize");

// Roulette configuration
let prizeMap = {};
let spinning = false;
let spinQueue = [];

// Draw the roulette wheel
function drawWheel() {
    const keys = Object.keys(prizeMap);
    const radius = canvas.width / 2;
    const sliceAngle = (2 * Math.PI) / keys.length;

    keys.forEach((prize, i) => {
        // Each slice color is prizeMap[prize].color
        ctx.beginPath();
        ctx.fillStyle = prizeMap[prize].color;
        ctx.moveTo(radius, radius);
        ctx.arc(radius, radius, radius, i * sliceAngle, (i + 1) * sliceAngle);
        ctx.fill();

        ctx.save();
        ctx.fillStyle = "#000";
        ctx.font = "2em Arial"; // Make text match h1 size
        ctx.translate(
            radius + Math.cos(sliceAngle * (i + 0.5)) * radius * 0.7,
            radius + Math.sin(sliceAngle * (i + 0.5)) * radius * 0.7
        );
        ctx.rotate(sliceAngle * (i + 0.5));
        ctx.fillText(prize, -25, 5);
        ctx.restore();
    });
}

// Start the roulette animation
function spinWheel(playerName, targetOption, onComplete) {
    // console.log(`Starting spin for player: ${playerName}, prize: ${targetOption}, function: spinWheel`);
    spinning = true;
    const keys = Object.keys(prizeMap);
    const totalRotations = 3; // Total number of rotations
    const degreesPerOption = 360 / keys.length;
    const targetIndex = keys.indexOf(targetOption);
    const targetDegrees = degreesPerOption * targetIndex;
    const finalDegrees = totalRotations * 360 + targetDegrees;

    let currentDegree = 0;

    // Show current player's info at the start of the animation
    currentPlayerNameElement.textContent = playerName || "Unknown Player";
    currentPlayerPrizeElement.textContent = "Spinning...";

    const spinInterval = setInterval(() => {
        try {
            currentDegree += 20; // Angle increment per spin
            if (currentDegree >= finalDegrees) {
                clearInterval(spinInterval);
                spinning = false;

                // Show winning info after the animation completes
                currentPlayerNameElement.textContent = playerName;
                currentPlayerPrizeElement.textContent = targetOption;
                if (onComplete) onComplete(); // Notify completion
                // console.log(`Completed spin  for player: ${playerName}, prize: ${targetOption}, function: spinWheel`);
            } else {
                ctx.setTransform(1, 0, 0, 1, 0, 0); // Replace resetTransform with setTransform
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.save();
                ctx.translate(canvas.width / 2, canvas.height / 2);
                ctx.rotate((currentDegree * Math.PI) / 180);
                ctx.translate(-canvas.width / 2, -canvas.height / 2);
                drawWheel();
                ctx.restore();
            }
        } catch (error) {
            console.error("Error during spinWheel execution:", error);
            clearInterval(spinInterval);
            spinning = false;
            showError("An error occurred during the spin. Please try again.");
        }
    }, 30); // Animation frame rate control
}

// Update historical winners list
function updateWinnersList(winners) {
    let text = "";
    winners.forEach(winner => {
        text += `${winner.name} - ${winner.prize}\n`;
    });
    document.getElementById("winnersBox").value = text;
}

// Show error message
function showError(message) {
    const errorMessageElement = document.getElementById("errorMessage");
    errorMessageElement.textContent = message;
    errorMessageElement.style.display = "block";
}

// Hide error message
function hideError() {
    const errorMessageElement = document.getElementById("errorMessage");
    errorMessageElement.textContent = "";
    errorMessageElement.style.display = "none";
}

function handleIncomingSpin(playerName, result) {
    console.log(`Received spin event: ${playerName} - ${result}`);
    spinQueue.push({ playerName, result });
    if (!spinning) {
        runNextSpin();
    }
}

function runNextSpin() {
    if (spinQueue.length === 0) return;
    const { playerName, result } = spinQueue.shift();
    console.log(`Starting spin for player: ${playerName}, prize: ${result}, function: runNextSpin`);
    spinWheel(playerName, result, () => {
        console.log(`Completed spin for player: ${playerName}, prize: ${result}, function: runNextSpin`);
        runNextSpin();
    });
}

// Initialize SSE to listen for backend push data
function initializeSSE() {
    const eventSource = new EventSource('/winners_stream');

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.result && data.name) {
            // Trigger roulette spin and update "current player winning" display area
            handleIncomingSpin(data.name, data.result);
        }

        if (data.winners) {
            // Update the historical winners list on the right
            updateWinnersList(data.winners);
        }
    };

    eventSource.onerror = function() {
        console.log("SSE connection error...");
    };
}

// Fetch the prize map, then draw
fetch("/prizes")
    .then(res => res.json())
    .then(data => {
        prizeMap = data;
        drawWheel();
    })
    .catch(err => console.error("Prize fetch error:", err));

initializeSSE();

// Load historical winners list
fetch("/winners")
    .then(response => response.json())
    .then(data => {
        updateWinnersList(data);
    })
    .catch(err => {
        console.error("Failed to load historical winners list:", err);
    });