/*
 * PrintHub sign-in page logic.
 */
(function () {
    var overlayElement = document.getElementById("signin-overlay");
    var errorElement = document.getElementById("signin-error");
    var buttonElement = document.getElementById("signin-button");

    buttonElement.addEventListener("click", function () {
        var usernameElement = document.getElementById("signin-user");
        var passwordElement = document.getElementById("signin-password");
        var rememberElement = document.getElementById("signin-remember");

        var username = usernameElement.value;
        var password = passwordElement.value;
        var remember = rememberElement.checked;

        overlayElement.classList.add("in");
        errorElement.classList.remove("in");

        fetch(BASE_URL + "api/auth", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                user: username,
                pass: password,
                remember: remember
            })
        })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            }
            throw new Error("Login failed");
        })
        .then(function (data) {
            window.location.href = NEXT_URL;
        })
        .catch(function () {
            usernameElement.value = USER_ID || "";
            passwordElement.value = "";

            if (USER_ID) {
                passwordElement.focus();
            } else {
                usernameElement.focus();
            }

            overlayElement.classList.remove("in");
            errorElement.classList.add("in");
        });

        return false;
    });

    /* Access request form toggle */
    var toggleLink = document.getElementById("toggle-access-form");
    var accessForm = document.getElementById("access-form");
    if (toggleLink && accessForm) {
        toggleLink.addEventListener("click", function (e) {
            e.preventDefault();
            accessForm.style.display = accessForm.style.display === "none" ? "block" : "none";
        });
    }

    var reqSubmit = document.getElementById("req-submit");
    if (reqSubmit) {
        reqSubmit.addEventListener("click", function () {
            var name = document.getElementById("req-name").value;
            var reason = document.getElementById("req-reason").value;
            var callback = document.getElementById("req-callback").value;
            var resultDiv = document.getElementById("req-result");

            fetch(BASE_URL + "api/access-request", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    name: name,
                    reason: reason,
                    callback_url: callback
                })
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.status === "submitted") {
                    resultDiv.innerHTML = "<p class='success'>Request submitted (ID: " + data.request_id + "). An admin will review shortly.</p>";
                } else {
                    resultDiv.innerHTML = "<p class='error'>" + (data.error || "Failed to submit") + "</p>";
                }
            })
            .catch(function () {
                resultDiv.innerHTML = "<p class='error'>Network error.</p>";
            });
        });
    }
})();
