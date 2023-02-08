// ==UserScript==
// @name         Remove Descriptions
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://brightspace.uakron.edu/d2l/le/activities*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=uakron.edu
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    // Get the current text of the title tag
    var title = document.querySelector("head > title").textContent;

    // Function to run when the title text changes
    function onTitleChange() {
        openDropdown();
    }



    function openDropdown() {
        try {
            document.querySelector(".d2l-token-receiver").shadowRoot.querySelector("d2l-consistent-evaluation-page").shadowRoot.querySelector("#evaluation-template > div:nth-child(3) > consistent-evaluation-right-panel").shadowRoot.querySelector("div > d2l-consistent-evaluation-rubric").shadowRoot.querySelector("#pop-out-evaluation-template > div > d2l-rubric").shadowRoot.querySelector("d2l-rubric-adapter").shadowRoot.querySelector("div > d2l-labs-accordion > d2l-labs-accordion-collapse").shadowRoot.querySelector("#trigger > d2l-icon").click();
        }
        catch (error) {
            setTimeout(openDropdown, 50);
        }
    }

    function removeElement() {
        try {
            var element = document.querySelector(".d2l-token-receiver").shadowRoot.querySelector("d2l-consistent-evaluation-page").shadowRoot.querySelector("#evaluation-template > div:nth-child(3) > consistent-evaluation-right-panel").shadowRoot.querySelector("div > d2l-consistent-evaluation-rubric").shadowRoot.querySelector("#pop-out-evaluation-template > div > d2l-rubric").shadowRoot.querySelector("d2l-rubric-adapter > div.d2l-rubric-print-container > div > d2l-rubric-criteria-groups").shadowRoot.querySelector("d2l-rubric-criteria-group-mobile").shadowRoot.querySelector("#\\30 ").shadowRoot.querySelector("#description");
            var element1 = document.querySelector(".d2l-token-receiver").shadowRoot.querySelector("d2l-consistent-evaluation-page").shadowRoot.querySelector("#evaluation-template > div:nth-child(3) > consistent-evaluation-right-panel").shadowRoot.querySelector("div > d2l-consistent-evaluation-rubric").shadowRoot.querySelector("#pop-out-evaluation-template > div > d2l-rubric").shadowRoot.querySelector("d2l-rubric-adapter > div.d2l-rubric-print-container > div > d2l-rubric-criteria-groups").shadowRoot.querySelector("d2l-rubric-criteria-group-mobile").shadowRoot.querySelector("#\\31 ").shadowRoot.querySelector("#description");
            var element2 = document.querySelector(".d2l-token-receiver").shadowRoot.querySelector("d2l-consistent-evaluation-page").shadowRoot.querySelector("#evaluation-template > div:nth-child(3) > consistent-evaluation-right-panel").shadowRoot.querySelector("div > d2l-consistent-evaluation-rubric").shadowRoot.querySelector("#pop-out-evaluation-template > div > d2l-rubric").shadowRoot.querySelector("d2l-rubric-adapter > div.d2l-rubric-print-container > div > d2l-rubric-criteria-groups").shadowRoot.querySelector("d2l-rubric-criteria-group-mobile").shadowRoot.querySelector("#\\32 ").shadowRoot.querySelector("#description");

            element.remove();
            element1.remove();
            element2.remove();
        } catch (error) {
            setTimeout(removeElement, 100);
            // Expected output: ReferenceError: nonExistentFunction is not defined
            // (Note: the exact output may be browser-dependent)
        }
    }

    removeElement();

    // Set up an interval to poll for changes in the title text
    setInterval(function () {
        var newTitle = document.querySelector("head > title").textContent;
        if (newTitle !== title) {
            title = newTitle;
            onTitleChange();
        }
    }, 500);

})();