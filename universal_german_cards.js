function loadSpoilers() {
    console.log('Load Spoilers');
    let spoilerIdCounter = 0;
    for (let spoiler of document.getElementsByClassName("spoiler")) {
        let parent = spoiler.parentElement;
        let spoilerId = spoiler.id;
        if (!spoilerId) {
            spoilerId = "spoiler-" + (spoilerIdCounter++);
            spoiler.id = spoilerId;
        }
        const oldHtml = parent.innerHTML;
        let hide = () => {
            parent.innerHTML = spoiler.outerHTML;
            document.getElementById(spoilerId).classList.remove("spoiler-open");
        };
        let show = () => {
            parent.innerHTML = oldHtml;
            document.getElementById(spoilerId).classList.add("spoiler-open");
        };
        let hideShow = function (event) {
            let clickedElement = document.elementFromPoint(event.x, event.y);
            while (clickedElement) {
                if (clickedElement.id == spoilerId) {
                    if (clickedElement.classList.contains("spoiler-open")) {
                        hide();
                    } else {
                        show();
                    }
                    break;
                }
                clickedElement = clickedElement.parentElement;
            }
        };
        hide();
        parent.onclick = hideShow;
    }
}
addEventListener("load", loadSpoilers);