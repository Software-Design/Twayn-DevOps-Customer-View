// Search projects
function searchProjects() {
    const input = document.getElementById("searchInput").value.toUpperCase();
    const projectCards = document.querySelectorAll("#projectsHolder .card");

    projectCards.forEach(card => {
        const cardTitle = card.querySelector(".card-title").innerText || card.querySelector(".card-title").textContent;
        if (cardTitle.toUpperCase().includes(input)) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    });
}

function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}


document.addEventListener('DOMContentLoaded', function () {
    initializeTooltips();
    document.getElementById("searchInput")?.addEventListener('input', searchProjects);
});