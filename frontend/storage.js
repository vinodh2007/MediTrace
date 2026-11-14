
async function loadStorageDashboard() {
    try {
        const response = await fetch(
            "http://127.0.0.1:5000/api/storage"
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Unable to load medicines");
        }

        // Update dashboard summary cards
        document.getElementById("totalMedicines").textContent =
            data.total_medicines;

        document.getElementById("totalStock").textContent =
            data.total_stock;

        document.getElementById("availableMedicines").textContent =
            data.available_medicines;

        document.getElementById("expiredMedicines").textContent =
            data.expired_medicines;

        document.getElementById("lowStockMedicines").textContent =
            data.low_stock_medicines;

        document.getElementById("expiringSoonMedicines").textContent =
            data.expiring_soon_medicines;

        // Display medicine records
        const table = document.getElementById("medicineTable");

        if (data.medicines.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="6">No medicine records found.</td>
                </tr>
            `;
            return;
        }

        table.innerHTML = "";

        data.medicines.forEach(medicine => {
            const row = document.createElement("tr");

            const values = [
                medicine.medicine_id,
                medicine.name,
                medicine.batch_id,
                medicine.quantity,
                medicine.expiry_date,
                medicine.status
            ];

            values.forEach((value, index) => {
                const cell = document.createElement("td");
                cell.textContent = value ?? "";

                if (index === 5) {
                    const status = String(value).toLowerCase();

                    if (status === "low stock") {
                        cell.style.backgroundColor = "#fef08a";
                        cell.style.color = "#854d0e";
                    }
                    else if (status === "available") {
                        cell.style.backgroundColor = "#dcfce7";
                        cell.style.color = "#15803d";
                    }
                    else if (status === "expired") {
                        cell.style.backgroundColor = "#fee2e2";
                        cell.style.color = "#dc2626";
                    }
                    else if (status === "expiring soon") {
                        cell.style.backgroundColor = "#ffedd5";
                        cell.style.color = "#c2410c";
                    }
                    else if (status === "out of stock") {
                        cell.style.backgroundColor = "#e2e8f0";
                        cell.style.color = "#475569";
                    }

                    cell.style.fontWeight = "bold";
                }

                row.appendChild(cell);
            });

            table.appendChild(row);
        });

    } catch (error) {
        console.error("Storage dashboard error:", error);

        document.getElementById("medicineTable").innerHTML = `
            <tr>
                <td colspan="6">
                    Unable to load medicine records. Check Flask backend.
                </td>
            </tr>
        `;
    }
}

// Load records when the page opens
document.addEventListener("DOMContentLoaded", loadStorageDashboard);
