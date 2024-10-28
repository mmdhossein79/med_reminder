//Flatpickr
var today = new Date();
var tomorrow = new Date();
tomorrow.setDate(today.getDate() + 1);
window.Date=window.JDate;
$("#checkin-date").flatpickr({
    defaultDate:today,
    "locale": "fa",
    "plugins": [new rangePlugin({ input: "#checkin-date" })]
});

$("#checkout-date").flatpickr({
    defaultDate:tomorrow
});