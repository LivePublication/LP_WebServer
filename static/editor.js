// Send flow trigger to server
function openLidFlow() {
    // Reveal spinner
    document.getElementById("spinner").style.display = "block";
    // Trigger flow
    // window.location.href = '/editor';
    // Start polling status
    pollFlowStatus();
    // Disable button
    document.getElementById("trigger-flow-btn").disabled = true;
}

// Poll server for flow execution status
function pollFlowStatus() {
    fetch('https://api.livepup-globus.cloud.edu.au/flow_status')
        .then(response => response.json())
        .then(data => {
            // If the status is not complete, poll again
            if (data.status !== 'complete') {
                // Show time elapsed
                document.getElementById("time-elapsed").innerHTML = data.time_elapsed;
                // Show current task
                document.getElementById("current-task").innerHTML = data.current_task;
                // Poll
                setTimeout(pollFlowStatus, 1000);
            } else {
                // On flow finished
                // Hide spinner
                document.getElementById("spinner").style.display = "none";
                // Show results
                document.getElementById("results").style.display = "block";
                // Show the results
                document.getElementById("results").innerHTML = data.results;
                // Re-enable button
                document.getElementById("trigger-flow-btn").disabled = false;
            }
        })
        .catch(error => {
            console.log(error);
        });
}

// Highlight icons on click
function highlightIcon(icon, icon_class) {
    // Highlight the icon
    icon.classList.add("highlight");
    // TODO: set selected item for the flow
    // Unhighlight the other icons
    var icons = document.getElementsByClassName(icon_class);
    for (var i = 0; i < icons.length; i++) {
        if (icons[i] !== icon) {
            icons[i].classList.remove("highlight");
        }
    }
}


// On load, populate flow-icons div with icons
function populate_icons(container_id, icon_class, icon_img, icon_text) {
        // Get the flow-icons div
    var container_div = document.getElementById(container_id);
    // Add 5 divs
    for (var i = 0; i < 5; i++) {
        var icon = document.createElement("button");
        icon.classList.add(icon_class);
        // Add click handler
        icon.addEventListener("click", function() {
            highlightIcon(this, icon_class);
        });
        // Add an img and p to the icon div
        var img = document.createElement("img");
        img.src = icon_img;
        icon.appendChild(img);
        var p = document.createElement("p");
        p.innerHTML = icon_text + " " + i;
        icon.appendChild(p);
        // Add the icon to the container div
        container_div.appendChild(icon);
    }

}

document.addEventListener("DOMContentLoaded", () => {
    populate_icons(
        "flow-icons",
        "flow-icon",
        "https://img.icons8.com/ios/50/000000/flow-chart.png",
        "Flow")})

document.addEventListener("DOMContentLoaded", () => {
    populate_icons(
        "manuscript-icons",
        "manuscript-icon",
        "https://img.icons8.com/ios/50/000000/documents",
        "Manuscript")});

