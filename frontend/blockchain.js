
async function loadBlockchainRecords() {

    const tableBody = document.getElementById("recordsTableBody");
    const recordCount = document.getElementById("recordCount");

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/api/blockchain/records"
        );

        if (!response.ok) {
            throw new Error("Unable to retrieve records");
        }

        const data = await response.json();

        tableBody.replaceChildren();

        recordCount.textContent =
            "Total Blockchain Records: " + data.total_records;

        if (data.records.length === 0) {

            const row = tableBody.insertRow();
            const cell = row.insertCell();

            cell.colSpan = 7;
            cell.textContent = "No blockchain records found.";

            return;
        }

        data.records.forEach(record => {

            const row = tableBody.insertRow();

            const values = [
                record.medicine_id,
                record.name,
                record.batch_id,
                record.block_number,
                record.transaction_hash,
                record.created_at,
                record.status
            ];

            values.forEach((value, index) => {

                const cell = row.insertCell();

                cell.textContent = value ?? "N/A";

                if (index === 4) {
                    cell.classList.add("hash-cell");
                }

                if (index === 6) {
                    cell.classList.add("record-status");
                }

            });

        });

    } catch (error) {

        console.error(error);

        recordCount.textContent = "Unable to load blockchain records.";

        tableBody.replaceChildren();

        const row = tableBody.insertRow();
        const cell = row.insertCell();

        cell.colSpan = 7;
        cell.textContent = "Please check that the Flask backend is running.";

    }
}

document.addEventListener(
    "DOMContentLoaded",
    loadBlockchainRecords
);
