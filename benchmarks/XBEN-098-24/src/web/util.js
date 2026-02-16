"use strict";

var HTTPS = (window.location + '').indexOf('https:') === 0,
    TOUCH = 'ontouchstart' in window,
    MOBILE = TOUCH;

var ebi = document.getElementById.bind(document),
    QS = document.querySelector.bind(document),
    QSA = document.querySelectorAll.bind(document);

function sread(key) {
    try { return localStorage.getItem(key); }
    catch (ex) { return null; }
}

function swrite(key, val) {
    try { localStorage.setItem(key, val); }
    catch (ex) { }
}

document.documentElement.className = sread("theme") || "light";
