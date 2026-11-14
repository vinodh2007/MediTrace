
const verifyForm = document.getElementById("verifyForm");
const medicineInput = document.getElementById("medicine_id");
const resultBox = document.getElementById("verificationResult");

// Verify medicine
async function verifyMedicine(medicineId) {

    if (!medicineId) {
        resultBox.textContent = "Please enter a Medicine ID.";
        return;
    }

    resultBox.textContent = "Verifying medicine...";

    try {

        const response = await fetch("/api/verify", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                medicine_id: medicineId
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "Verification failed");
        }

        resultBox.innerHTML = "";

        if (data.authentic) {

            // SUCCESS MESSAGE
            const success = document.createElement("div");
            success.className = "verification-success";

            const heading = document.createElement("h3");
            heading.textContent = "✓ Medicine Record Verified";

            const message = document.createElement("p");
            message.textContent = data.message;

            success.appendChild(heading);
            success.appendChild(message);
            resultBox.appendChild(success);

            // CRYPTOGRAPHIC RESULTS
            const cryptoDetails = document.createElement("div");
            cryptoDetails.className = "crypto-details";

            const cryptoHeading = document.createElement("h4");
            cryptoHeading.textContent = "Cryptographic Results";

            cryptoDetails.appendChild(cryptoHeading);

            const results = [
                ["Medicine ID", data.medicine_id],
                ["SHA-256 Hash Match", data.hash_matches ? "Valid" : "Invalid"],
                ["RSA Digital Signature", data.signature_valid ? "Valid" : "Invalid"],
                ["Ethereum Verification", data.blockchain_verified ? "Valid" : "Invalid"],
                ["Stored Hash", data.stored_hash]
            ];

            results.forEach(([label, value]) => {

                const paragraph = document.createElement("p");
                const strong = document.createElement("strong");

                strong.textContent = label + ": ";

                paragraph.appendChild(strong);
                paragraph.appendChild(
                    document.createTextNode(value ?? "Not available")
                );

                cryptoDetails.appendChild(paragraph);
            });

            resultBox.appendChild(cryptoDetails);

            // MEDICINE DETAILS
            if (data.medicine_details) {

                const details = document.createElement("div");
                details.className = "crypto-details";

                const detailsHeading = document.createElement("h4");
                detailsHeading.textContent = "Medicine Details";

                details.appendChild(detailsHeading);

                const fields = [
                    ["Medicine Name", "medicine_name"],
                    ["Medicine ID", "medicine_id"],
                    ["Batch ID", "batch_id"],
                    ["Manufacturer", "manufacturer"],
                    ["Manufacturing Date", "manufacturing_date"],
                    ["Expiry Date", "expiry_date"],
                    ["Available Quantity", "available_quantity"],
                    ["Availability", "availability"]
                ];

                fields.forEach(([label, key]) => {

                    const paragraph = document.createElement("p");
                    const strong = document.createElement("strong");

                    strong.textContent = label + ": ";

                    paragraph.appendChild(strong);

                    paragraph.appendChild(
                        document.createTextNode(
                            data.medicine_details[key] ?? "Not available"
                        )
                    );

                    details.appendChild(paragraph);
                });

                resultBox.appendChild(details);
            }

            // QR CODE DISPLAY
            if (data.qr_code_url) {

                const qrSection = document.createElement("div");
                qrSection.className = "crypto-details";

                const qrHeading = document.createElement("h3");
                qrHeading.textContent = "Medicine QR Code";

                const qrDescription = document.createElement("p");
                qrDescription.textContent =
                    "Scan this QR code using your mobile phone to view medicine details.";

                const qrImage = document.createElement("img");

                qrImage.src = data.qr_code_url;
                qrImage.alt = "Medicine QR Code";
                qrImage.style.width = "220px";
                qrImage.style.maxWidth = "100%";
                qrImage.style.display = "block";
                qrImage.style.margin = "20px auto";

                const downloadLink = document.createElement("a");

                downloadLink.href = data.qr_code_url;
                downloadLink.download = data.qr_code || "medicine-qr.png";
                downloadLink.textContent = "Download QR Code";

                downloadLink.style.display = "block";
                downloadLink.style.textAlign = "center";

                qrSection.appendChild(qrHeading);
                qrSection.appendChild(qrDescription);
                qrSection.appendChild(qrImage);
                qrSection.appendChild(downloadLink);

                resultBox.appendChild(qrSection);

            } else {

                resultBox.appendChild(
                    document.createTextNode("QR code could not be generated.")
                );
            }

        } else {

            const failed = document.createElement("div");
            failed.className = "verification-failed";

            const heading = document.createElement("h3");
            heading.textContent = "⚠ Verification Failed";

            const message = document.createElement("p");
            message.textContent = data.message;

            failed.appendChild(heading);
            failed.appendChild(message);

            resultBox.appendChild(failed);
        }

    } catch (error) {

        resultBox.innerHTML = "";

        const failed = document.createElement("div");
        failed.className = "verification-failed";

        const heading = document.createElement("h3");
        heading.textContent = "Verification Error";

        const message = document.createElement("p");
        message.textContent = error.message;

        failed.appendChild(heading);
        failed.appendChild(message);

        resultBox.appendChild(failed);
    }
}


// FORM SUBMISSION
verifyForm.addEventListener("submit", function(event) {

    event.preventDefault();

    const medicineId = medicineInput.value.trim();

    verifyMedicine(medicineId);

});
