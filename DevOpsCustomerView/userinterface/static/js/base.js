// Search projects
function searchProjects() {
    input = document.getElementById("searchInput").value.toUpperCase();
    holder = document.getElementById("projectsHolder").getElementsByClassName("card-title");
    for (i = 0; i < holder.length; i++) {
        if (holder[i].innerHTML.toUpperCase().indexOf(input) > -1) {
            holder[i].parentNode.parentNode.style.display = "";
        } else {
            holder[i].parentNode.parentNode.style.display = "none";
        }
    }
}