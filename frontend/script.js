
// --------------------------------------------------
// LOAD DASHBOARD DATA
// --------------------------------------------------


async function loadDashboard() {

    try {

        const response = await fetch("/api/dashboard");

        if (!response.ok) {
            throw new Error("Unable to load dashboard data");
        }

        const data = await response.json();

        // Display statistics
        document.getElementById("totalMedicines").textContent =
            data.total_medicines;

        document.getElementById("verifiedBatches").textContent =
            data.verified_batches;

        document.getElementById("suspiciousBatches").textContent =
            data.suspicious_batches;

        document.getElementById("storageAlerts").textContent =
            data.storage_alerts;

        // Display medicine records
        const table = document.getElementById("medicineTable");

        table.innerHTML = "";

        data.medicines.forEach(medicine => {

            const row = document.createElement("tr");

            const statusClass = {
                "Verified": "verified",
                "Pending": "pending",
                "Suspicious": "suspicious",
                "Registered": "registered"
            }[medicine.status] || "pending";

            const values = [
                medicine.name,
                medicine.batch,
                medicine.manufacturer,
                medicine.status
            ];

            values.forEach((value, index) => {

                const cell = document.createElement("td");

                if (index === 3) {

                    const badge = document.createElement("span");
                    badge.className = "status " + statusClass;
                    badge.textContent = value || "Unknown";

                    cell.appendChild(badge);

                } else {

                    cell.textContent = value || "-";

                }

                row.appendChild(cell);

            });

            table.appendChild(row);

        });

        // Update old storage monitoring elements only if they exist
        const temperature = document.getElementById("temperature");
        const humidity = document.getElementById("humidity");
        const condition = document.getElementById("condition");

        if (temperature && data.storage) {
            temperature.textContent = data.storage.temperature + " °C";
        }

        if (humidity && data.storage) {
            humidity.textContent = data.storage.humidity + " %";
        }

        if (condition && data.storage) {
            condition.textContent = data.storage.condition;
        }

        console.log("MediTrace dashboard loaded successfully!");

    }

    catch (error) {

        console.error("Dashboard Error:", error);

        document.getElementById("medicineTable").innerHTML =
            '<tr><td colspan="4">Unable to load dashboard data.</td></tr>';

    }

}


// --------------------------------------------------
// LIVE BLOCKCHAIN NETWORK STATUS
// --------------------------------------------------

async function loadBlockchainStatus() {

    const panel = document.getElementById("blockchain");

    if (!panel) {
        console.error("Blockchain panel not found!");
        return;
    }

    const badge = panel.querySelector(".network-status");

    // Display loading status

    if (badge) {
        badge.innerText = "Checking...";
    }

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/api/blockchain/status"
        );

        const data = await response.json();

        if (!response.ok || !data.connected) {
            throw new Error(data.message || "Blockchain unavailable");
        }

        // Update connection badge

        if (badge) {
            badge.innerText = "Connected";
            badge.classList.add("connected");
            badge.classList.remove("disconnected");
        }

        // Create blockchain information container

        let details = document.getElementById("blockchainDetails");

        if (!details) {

            details = document.createElement("div");

            details.id = "blockchainDetails";
            details.className = "blockchain-details";

            panel.appendChild(details);

        }

        // Clear old information

        details.innerHTML = "";

        // Display live blockchain information

        const blockchainInfo = [
            ["Network", data.network],
            ["Chain ID", data.chain_id],
            ["Latest Block", data.latest_block],
            ["Smart Contract", data.contract_deployed ? "Deployed" : "Not Deployed"],
            ["Contract Address", data.contract_address]
        ];

        blockchainInfo.forEach(([label, value]) => {

            const item = document.createElement("div");

            item.className = "blockchain-info-item";

            const heading = document.createElement("strong");
            heading.innerText = label + ": ";

            const content = document.createElement("span");
            content.innerText = value ?? "Unavailable";

            item.appendChild(heading);
            item.appendChild(content);

            details.appendChild(item);

        });

        console.log("Live blockchain information loaded successfully!");

    }

    catch (error) {

        console.error("Blockchain Status Error:", error);

        if (badge) {
            badge.innerText = "Disconnected";
            badge.classList.remove("connected");
            badge.classList.add("disconnected");
        }

        let details = document.getElementById("blockchainDetails");

        if (!details) {

            details = document.createElement("div");
            details.id = "blockchainDetails";
            details.className = "blockchain-details";

            panel.appendChild(details);

        }

        details.innerText =
            "Unable to retrieve blockchain information. Check Ganache and Flask.";

    }

}


// --------------------------------------------------
// QUICK ACTION NOTIFICATION
// --------------------------------------------------

function showNotice(feature) {

    document.getElementById("notice").innerText =
        feature + " will be implemented in the next development stage.";

}


// --------------------------------------------------
// LOAD DASHBOARD WHEN WEBPAGE OPENS
// --------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    loadDashboard();

    loadStorageSummary();

    loadBlockchainStatus();

});

// Load real Storage Dashboard summary from Flask API

async function loadStorageSummary() {

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/api/storage"
        );

        if (!response.ok) {
            throw new Error("Unable to load storage summary");
        }

        const data = await response.json();

        document.getElementById("storageTotalMedicines").textContent =
            data.total_medicines;

        document.getElementById("storageTotalStock").textContent =
            data.total_stock;

        document.getElementById("storageExpiringSoon").textContent =
            data.expiring_soon_medicines;

        document.getElementById("storageLowStock").textContent =
            data.low_stock_medicines;

    } catch (error) {

        console.error("Storage summary error:", error);

        document.getElementById("storageTotalMedicines").textContent = "--";
        document.getElementById("storageTotalStock").textContent = "--";
        document.getElementById("storageExpiringSoon").textContent = "--";
        document.getElementById("storageLowStock").textContent = "--";

    }
}
