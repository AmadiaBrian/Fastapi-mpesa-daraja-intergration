const form = document.getElementById("mpesaForm");
const btn = document.getElementById("submitBtn");
const spinner = document.getElementById("spinner");
const btnText = document.getElementById("btnText");
const result = document.getElementById("result");
const showFormBtn = document.getElementById("showFormBtn");
const hideFormBtn = document.getElementById("hideFormBtn");

let checkoutRequestId = null;
let pollingInterval = null;

// Set current year in footer
document.getElementById("currentYear").textContent = new Date().getFullYear();

// Show form when Lipa na M-Pesa button is clicked
showFormBtn.addEventListener("click", () => {
    form.style.display = "block";
    showFormBtn.style.display = "none";
});

// Hide form when Cancel button is clicked
hideFormBtn.addEventListener("click", () => {
    form.style.display = "none";
    showFormBtn.style.display = "block";
    result.style.display = "none";
});

function showModal(modalId) {
    document.getElementById(modalId).style.display = "flex";
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = "none";
}

function closeSuccessModal() {
    closeModal('successModal');
    form.style.display = "none";
    showFormBtn.style.display = "block";
}

async function checkPaymentStatus(checkoutRequestID) {
    try {
        const res = await fetch(`/check-status/?checkout_request_id=${checkoutRequestID}`);
        const response = await res.json();

        console.log("Payment status check:", response);

        if (response.status === 'found') {
            if (response.result_code === 1032) {
                // Cancelled by user
                stopPolling();
                closeModal('initiatedModal');
                showModal('cancelledModal');
            } else if (response.result_code === 0) {
                // Successful
                stopPolling();
                closeModal('initiatedModal');
                showModal('successModal');
                // Hide form and show Lipa na M-Pesa button after successful payment
                setTimeout(() => {
                    form.style.display = "none";
                    showFormBtn.style.display = "block";
                }, 2000);
            } else if (response.result_code === 1037) {
                // Timeout
                stopPolling();
                closeModal('initiatedModal');
                showModal('timeoutModal');
            } else if (response.result_code === 1) {
                // Insufficient balance
                stopPolling();
                closeModal('initiatedModal');
                showModal('insufficientModal');
            } else if (response.result_code === 2001) {
                // Wrong PIN
                stopPolling();
                closeModal('initiatedModal');
                showModal('wrongPinModal');
            } else if (response.result_code === 2002) {
                // Invalid credentials
                stopPolling();
                closeModal('initiatedModal');
                showModal('invalidCredentialsModal');
            } else if (response.result_code === 2004) {
                // Invalid amount
                stopPolling();
                closeModal('initiatedModal');
                showModal('invalidAmountModal');
            } else if (response.result_code === 2005) {
                // Invalid phone number
                stopPolling();
                closeModal('initiatedModal');
                showModal('invalidPhoneModal');
            }
        }
        // If status is 'not_found', continue polling
    } catch (err) {
        console.error("Error checking payment status:", err);
    }
}

function startPolling(checkoutRequestID) {
    pollingInterval = setInterval(() => {
        checkPaymentStatus(checkoutRequestID);
    }, 3000); // Poll every 3 seconds
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    spinner.style.display = "block";
    btnText.textContent = "Processing...";
    btn.disabled = true;
    result.style.display = "none";

    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    if (data.phone.startsWith("0")) {
        data.phone = "254" + data.phone.substring(1);
    }

    try {
        const res = await fetch("/initiate/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams(data)
        });

        const response = await res.json();

        spinner.style.display = "none";
        btnText.textContent = "Send Payment Request";
        btn.disabled = false;

        result.style.display = "block";

        if (response.CheckoutRequestID) {
            checkoutRequestId = response.CheckoutRequestID;
            result.style.display = "none"; // Hide result div when modal is shown
            showModal('initiatedModal');
            startPolling(checkoutRequestId);
        } else {
            result.className = "result error";
            result.innerHTML = "Error: " + (response.error || "Request failed");
        }

    } catch (err) {
        spinner.style.display = "none";
        btnText.textContent = "Send Payment Request";
        btn.disabled = false;

        result.style.display = "block";
        result.className = "result error";
        result.innerHTML = "Error: " + err.message;
    }
});
