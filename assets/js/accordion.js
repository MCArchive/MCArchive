var accBtns = document.getElementsByClassName("accbtn");
for (i = 0; i < accBtns.length; i++) {
    accBtns[i].onclick = function() {
        this.classList.toggle("active");
        var div = this.nextElementSibling;
        // div.classList.toggle("hidden");
        if (div.style.maxHeight == 0) {
            div.style.maxHeight = div.scrollHeight + "px";
        } else {
            div.style.maxHeight = null;
        }
    };
}

var accs = document.getElementsByClassName("accordion");
for (i = 0; i < accs.length; i++) {
    accs[i].classList.add("hidden");
    accs[i].style.maxHeight = null;
}

