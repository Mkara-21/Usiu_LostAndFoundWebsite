function showSection(sectionId) {
    // Hide both forms first
    document.getElementById('finder-section').style.display = 'none';
    document.getElementById('owner-section').style.display = 'none';
    
    // Show the selected form cleanly
    document.getElementById(sectionId).style.display = 'block';
    
    // Smooth scroll down to the active form area
    document.getElementById(sectionId).scrollIntoView({ behavior: 'smooth' });
}

function filterCategory(categoryName) {
    // Grab all the item rows in the table
    const rows = document.querySelectorAll('.item-row');
    
    rows.forEach(row => {
        // If 'All' is clicked, show everything. Otherwise, match the category attribute
        if (categoryName === 'All' || row.getAttribute('data-category') === categoryName) {
            row.style.display = ''; // Shows the row
        } else {
            row.style.display = 'none'; // Hides the row
        }
    });
}

function toggleAdminDetails(itemId) {
    const detailsDiv = document.getElementById('details-' + itemId);
    if (detailsDiv.style.display === 'none' || !detailsDiv.style.display) {
        detailsDiv.style.display = 'block';
    } else {
        detailsDiv.style.display = 'none';
    }
}

// Switches visibility between the Login and Sign-Up boxes
function switchGatewayForm(showId, hideId) {
    document.getElementById(hideId).style.display = 'none';
    document.getElementById(showId).style.display = 'block';
}

// Flips password inputs between dot symbols and readable text
function togglePasswordVisibility(inputId) {
    const field = document.getElementById(inputId);
    if (field.type === 'password') {
        field.type = 'text';
    } else {
        field.type = 'password';
    }
}

// Changes placeholders dynamically based on selected user roles
function adjustIDPlaceholder(roleSelectId, inputId) {
    const selection = document.getElementById(roleSelectId).value;
    const inputField = document.getElementById(inputId);
    
    if (selection === 'security') {
        inputField.placeholder = "Enter 9-digit Officer Badge ID";
        inputField.removeAttribute('pattern');
    } else {
        inputField.placeholder = "Enter 6-digit ID";
        inputField.setAttribute('pattern', '\\d{6}');
    }
}

// Status Filter (Pending, Reviewed, Dismissed) for Security Tables
function filterTableRows(tableId, selectedStatus) {
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
    
    for (let i = 0; i < rows.length; i++) {
        // Skip details/dossier sliding panels during status screening
        if (rows[i].id && rows[i].id.includes('dossier')) continue;
        
        const status = rows[i].getAttribute('data-status');
        if (selectedStatus === "All" || status === selectedStatus) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
            // Also hide accompanying dossier drawer if it was open
            const nextRow = rows[i].nextElementSibling;
            if (nextRow && nextRow.id && nextRow.id.includes('dossier')) {
                nextRow.style.display = "none";
            }
        }
    }
}

// Category Filter for Master Recorded Registry
function filterRegistryCategory(selectedCategory) {
    const rows = document.getElementsByClassName('registry-row');
    for (let i = 0; i < rows.length; i++) {
        const cat = rows[i].getAttribute('data-category');
        if (selectedCategory === "All" || cat === selectedCategory) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
        }
    }
}

// Dossier Accordion Slider Toggle
function toggleAdminDetails(id) {
    const detailRow = document.getElementById(id);
    if (detailRow.style.display === "none") {
        detailRow.style.display = "table-row";
    } else {
        detailRow.style.display = "none";
    }
}