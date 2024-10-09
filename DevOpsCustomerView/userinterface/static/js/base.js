// Search projects
function searchProjects() {
    const input = document.getElementById("searchInput").value.toUpperCase();
    const holder = document.getElementById("projectsHolder").getElementsByClassName("card-title");

    for (let i = 0; i < holder.length; i++) {
        if (holder[i].innerHTML.toUpperCase().indexOf(input) > -1) {
            holder[i].parentNode.parentNode.style.display = "";
        } else {
            holder[i].parentNode.parentNode.style.display = "none";
        }
    }
}

function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function delayedSearch() {
    setTimeout(searchProjects, 1000);
}

document.addEventListener('DOMContentLoaded', function () {
    initializeTooltips();
    document.getElementById("searchInput").addEventListener('input', delayedSearch);
    document.getElementById("searchInput").addEventListener('change', searchProjects);
});