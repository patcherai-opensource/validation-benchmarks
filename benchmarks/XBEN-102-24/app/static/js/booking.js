/**
 * BookSchedule Booking Module
 * Handles the public booking form interactions
 */

var BookScheduleBooking = (function() {
    'use strict';

    var BASE_API_URL = '/api/v1';

    function loadProviders() {
        fetch('/booking/available-providers')
            .then(function(response) { return response.json(); })
            .then(function(providers) {
                var container = document.getElementById('provider-select');
                if (!container) return;
                providers.forEach(function(provider) {
                    var option = document.createElement('option');
                    option.value = provider.id;
                    option.textContent = provider.firstName + ' ' + provider.lastName;
                    container.appendChild(option);
                });
            });
    }

    function loadOfferings() {
        fetch('/booking/available-offerings')
            .then(function(response) { return response.json(); })
            .then(function(offerings) {
                var container = document.getElementById('offering-select');
                if (!container) return;
                offerings.forEach(function(offering) {
                    var option = document.createElement('option');
                    option.value = offering.id;
                    option.textContent = offering.name + ' (' + offering.duration + ' min - ' + offering.currency + ' ' + offering.price + ')';
                    container.appendChild(option);
                });
            });
    }

    return {
        init: function() {
            loadProviders();
            loadOfferings();
        }
    };
})();

document.addEventListener('DOMContentLoaded', BookScheduleBooking.init);
