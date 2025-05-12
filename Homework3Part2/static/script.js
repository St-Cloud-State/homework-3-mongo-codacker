// Add Application
document.getElementById('add-application-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const zipcode = document.getElementById('zipcode').value;

    const response = await fetch('/add_application', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: name,
            zipcode: zipcode,
        })
    });

    const result = await response.json();
    console.log(result);
});

// Check Status
document.getElementById('check-status-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const appId = document.getElementById('app-id-status').value;

    const response = await fetch(`/check_status/${appId}`, {
        method: 'GET',
    });

    const result = await response.json();
    document.getElementById('status-result').innerText = JSON.stringify(result);
});

// Change Status
document.getElementById('change-status-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const appId = document.getElementById('app-id-change').value;
    const newStatus = document.getElementById('new-status').value;

    const response = await fetch('/change_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            appId: appId,
            newStatus: newStatus,
        })
    });

    const result = await response.json();
    document.getElementById('status-change-result').innerText = JSON.stringify(result);
});
