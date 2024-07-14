(() => {
    let hiddenParentHtml = {};

    function hide(spoilerId) {
        let spoiler = document.getElementById(spoilerId);
        if (hiddenParentHtml[spoiler.id]) {
            return;
        }
        spoiler.classList.remove("spoiler-open");
        let parent = spoiler.parentElement;
        hiddenParentHtml[spoiler.id] = parent.innerHTML;
        parent.innerHTML = spoiler.outerHTML;
    }

    function show(spoilerId) {
        if (!hiddenParentHtml[spoilerId]) {
            return;
        }
        let parent = document.getElementById(spoilerId).parentElement;
        parent.innerHTML = hiddenParentHtml[spoilerId];
        delete hiddenParentHtml[spoilerId];
        document.getElementById(spoilerId).classList.add("spoiler-open");
    }

    function hideOrShow(event) {
        // if (!event.target.id || !event.target.classList.contains("spoiler")) {
        //     return;
        // }
        event.stopPropagation();
        if (event.target.classList.contains("spoiler-open")) {
            hide(event.target.id);
        } else {
            show(event.target.id);
        }
    }

    //document.getElementsByTagName("body").item(0).addEventListener("click", hideOrShow);

    let spoilerIdCounter = 0;

    let knownSpoilers = {};

    function generateSpoilers() {
        for (let spoiler of document.getElementsByClassName("spoiler")) {
            if (!spoiler.id) {
                spoiler.id = "spoiler-" + (spoilerIdCounter++);
                hide(spoiler.id);
            }
            spoiler.removeEventListener("click", hideOrShow);
            spoiler.removeEventListener("touchstart", hideOrShow);
            spoiler.addEventListener("click", hideOrShow);
            spoiler.addEventListener("touchstart", hideOrShow);
        }
    }

    const observer = new MutationObserver(generateSpoilers);
    observer.observe(document.getElementsByTagName("body").item(0), {childList: true, subtree: true});
    generateSpoilers();
})();