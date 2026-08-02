function showSection(sectionId) {
    ["finder-section", "owner-section"].forEach((id) => {
        const section = document.getElementById(id);
        if (section) section.hidden = id !== sectionId;
    });

    const selected = document.getElementById(sectionId);
    if (selected) {
        selected.scrollIntoView({ behavior: "smooth", block: "start" });
        const firstField = selected.querySelector("input:not([type='hidden']), select, textarea");
        if (firstField) firstField.focus({ preventScroll: true });
    }
}

function hideSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) section.hidden = true;
}

function startClaim(button) {
    const itemId = button.dataset.itemId;
    const description = button.dataset.itemDesc;
    const idField = document.getElementById("claim-item-id");
    const nameField = document.getElementById("claim-item-name");
    if (!idField || !nameField || !itemId || !description) return;

    idField.value = itemId;
    nameField.value = description;
    showSection("owner-section");
}

function filterCategory(categoryName, activeButton) {
    const rows = document.querySelectorAll(".item-card");
    let visibleCount = 0;

    rows.forEach((row) => {
        const categoryMatches =
            categoryName === "All" || row.dataset.category === categoryName;
        const searchMatches = row.dataset.searchMatch !== "false";
        row.hidden = !(categoryMatches && searchMatches);
        if (!row.hidden) visibleCount += 1;
    });

    document.querySelectorAll(".filter-chip").forEach((button) => {
        button.classList.toggle("active", button === activeButton);
    });
    const empty = document.getElementById("filtered-empty");
    if (empty) empty.hidden = visibleCount !== 0;
}

function filterItems(searchTerm) {
    const normalized = searchTerm.trim().toLowerCase();
    const active = document.querySelector(".filter-chip.active");
    const category = active ? active.dataset.filter : "All";

    document.querySelectorAll(".item-card").forEach((card) => {
        card.dataset.searchMatch = String(
            !normalized || card.dataset.search.toLowerCase().includes(normalized)
        );
    });
    filterCategory(category, active);
}

function switchGatewayForm(showId, hideId) {
    const show = document.getElementById(showId);
    const hide = document.getElementById(hideId);
    if (hide) hide.hidden = true;
    if (show) {
        show.hidden = false;
        const firstField = show.querySelector("input, select");
        if (firstField) firstField.focus();
    }
}

function togglePasswordVisibility(inputId, button) {
    const field = document.getElementById(inputId);
    if (!field) return;
    const showing = field.type === "text";
    field.type = showing ? "password" : "text";
    if (button) {
        button.textContent = showing ? "Show" : "Hide";
        button.setAttribute("aria-label", showing ? "Show password" : "Hide password");
    }
}

function adjustIDPlaceholder(roleSelectId, inputId) {
    const roleSelect = document.getElementById(roleSelectId);
    const input = document.getElementById(inputId);
    if (!roleSelect || !input) return;

    const security = roleSelect.value === "security";
    input.placeholder = security
        ? "Enter 9-digit Security Badge ID"
        : "Enter 6-digit Student ID";
    input.pattern = security ? "\\d{9}" : "\\d{6}";
    input.maxLength = security ? 9 : 6;
}

function toggleAdminDetails(dossierId, button) {
    const row = document.getElementById(dossierId);
    if (!row) return;
    row.hidden = !row.hidden;
    if (button) {
        button.setAttribute("aria-expanded", String(!row.hidden));
        button.textContent = row.hidden ? "Open dossier" : "Close dossier";
    }
}

function filterTableRows(tableId, selectedStatus) {
    const table = document.getElementById(tableId);
    if (!table) return;
    table.querySelectorAll("tr.registry-row").forEach((row) => {
        const show = selectedStatus === "All" || row.dataset.status === selectedStatus;
        row.hidden = !show;
        const dossier = row.nextElementSibling;
        if (!show && dossier && dossier.classList.contains("dossier-row")) {
            dossier.hidden = true;
            const button = row.querySelector("[aria-expanded]");
            if (button) {
                button.setAttribute("aria-expanded", "false");
                button.textContent = "Open dossier";
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const authLayout = document.querySelector(".auth-layout");
    if (authLayout && authLayout.dataset.authMode === "signup") {
        switchGatewayForm("signup-box", "login-box");
    }

    const dashboard = document.querySelector(".dashboard-shell[data-open-panel]");
    if (dashboard && dashboard.dataset.openPanel) {
        const panelId = dashboard.dataset.openPanel === "owner"
            ? "owner-section"
            : "finder-section";
        showSection(panelId);
    }

    ["login-role", "reg-role"].forEach((roleId) => {
        const role = document.getElementById(roleId);
        if (role) adjustIDPlaceholder(roleId, roleId === "login-role" ? "login-id" : "reg-id");
    });
});
