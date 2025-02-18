

document.getElementById('materialForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const materialName = document.getElementById('materialName').value;

    fetch('/material-details', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({name: materialName}),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            showMessage(data.error, 'error');
            return;
        }
        
        // Update the UI with the material details
        updateMaterialDetails(data);
        
        // Show verification status
        if (data.verified) {
            showMessage('Material properties verified successfully', 'success');
        } else if (data.verificationFailed) {
            showMessage('Some properties could not be verified', 'warning');
        }
    })
    .catch((error) => {
        showMessage('Failed to fetch material details', 'error');
        console.error('Error:', error);
    });
});

function showMessage(message, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
    
    // Hide message after 5 seconds
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}
