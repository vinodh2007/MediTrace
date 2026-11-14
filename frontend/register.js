
const medicineForm = document.getElementById("medicineForm");

medicineForm.addEventListener("submit", async function(event) {

    event.preventDefault();

    const message = document.getElementById("message");

    const submitButton = medicineForm.querySelector(
        'button[type="submit"]'
    );

    const medicineData = {

        name: document.getElementById("name").value.trim(),

        batch_id: document.getElementById("batch_id").value.trim(),

        manufacturer: document.getElementById("manufacturer").value.trim(),

        manufacturing_date:
            document.getElementById("manufacturing_date").value,

        expiry_date:
            document.getElementById("expiry_date").value,

        quantity:
            document.getElementById("quantity").value

    };

    message.innerText = "Registering medicine...";
    message.className = "form-message";

    submitButton.disabled = true;

    try {

        const response = await fetch("http://127.0.0.1:5000/api/medicines", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(medicineData)

        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || "Registration failed");
        }

        message.className = "form-message success";

        message.innerText =
            result.message + " Medicine ID: " + result.medicine_id;

        medicineForm.reset();

    }

    catch (error) {

        message.className = "form-message error";

        message.innerText = error.message;

        console.error(error);

    }

    finally {

        submitButton.disabled = false;

    }

});
