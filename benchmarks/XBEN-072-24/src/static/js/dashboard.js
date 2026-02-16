/*
 * PrintHub dashboard logic.
 */
(function () {
    function loadJobs() {
        fetch("/api/jobs")
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var container = document.getElementById("jobs-list");
                if (!data.jobs || data.jobs.length === 0) {
                    container.innerHTML = "<p>No print jobs.</p>";
                    return;
                }
                var html = "<table class='table'><thead><tr><th>Name</th><th>Printer</th><th>Status</th><th>Progress</th></tr></thead><tbody>";
                data.jobs.forEach(function (job) {
                    html += "<tr><td>" + job.name + "</td><td>" + job.printer + "</td><td>" + job.status + "</td><td>" + job.progress + "%</td></tr>";
                });
                html += "</tbody></table>";
                container.innerHTML = html;
            })
            .catch(function () {
                document.getElementById("jobs-list").innerHTML = "<p class='error'>Failed to load jobs.</p>";
            });
    }

    function loadPrinterStatus() {
        fetch("/api/printer")
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var container = document.getElementById("printer-status");
                var html = "<p>State: <strong>" + data.state.text + "</strong></p>";
                html += "<p>Hotend: " + data.temperature.tool0.actual + "&deg;C / " + data.temperature.tool0.target + "&deg;C</p>";
                html += "<p>Bed: " + data.temperature.bed.actual + "&deg;C / " + data.temperature.bed.target + "&deg;C</p>";
                container.innerHTML = html;
            })
            .catch(function () {
                document.getElementById("printer-status").innerHTML = "<p class='error'>Offline</p>";
            });
    }

    function loadConnection() {
        fetch("/api/connection")
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var container = document.getElementById("connection-info");
                var html = "<p>State: " + data.current.state + "</p>";
                html += "<p>Port: " + data.current.port + "</p>";
                html += "<p>Baudrate: " + data.current.baudrate + "</p>";
                container.innerHTML = html;
            })
            .catch(function () {
                document.getElementById("connection-info").innerHTML = "<p class='error'>Connection error</p>";
            });
    }

    document.getElementById("share-btn").addEventListener("click", function () {
        var urlInput = document.getElementById("share-url");
        var resultDiv = document.getElementById("share-result");
        var url = urlInput.value.trim();

        if (!url) {
            resultDiv.innerHTML = "<p class='error'>Please enter a URL.</p>";
            return;
        }

        fetch("/api/share", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({url: url})
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.status === "queued") {
                resultDiv.innerHTML = "<p class='success'>Link submitted for admin review (ID: " + data.review_id + ")</p>";
            } else {
                resultDiv.innerHTML = "<p class='error'>" + (data.error || "Unknown error") + "</p>";
            }
        })
        .catch(function () {
            resultDiv.innerHTML = "<p class='error'>Failed to submit link.</p>";
        });
    });

    document.getElementById("logout-btn").addEventListener("click", function (e) {
        e.preventDefault();
        fetch("/api/logout", {method: "POST"})
            .then(function () { window.location.href = "/signin"; });
    });

    function checkNotifications() {
        fetch("/api/events?type=notification")
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.events && data.events.length > 0) {
                    var latest = data.events[data.events.length - 1];
                    if (latest) {
                        var el = document.createElement("div");
                        el.className = "alert alert-info in";
                        el.textContent = latest;
                        document.querySelector(".main-content").prepend(el);
                    }
                }
            })
            .catch(function () {});
    }

    // Initial load
    loadJobs();
    loadPrinterStatus();
    loadConnection();
    checkNotifications();

    // Periodic refresh
    setInterval(loadPrinterStatus, 30000);
    setInterval(checkNotifications, 15000);
})();
