import Choices from 'choices.js';
window.Choices = Choices;

// Code to initialize the search form.
const GAMEVSN_ID = "gamevsn";
const AUTHOR_ID = "author";
const SEL_FILE_ID = "select_file";
const UPLOAD_ROW_ID = "upload_row";

if (document.getElementById(GAMEVSN_ID) && document.getElementById(AUTHOR_ID)) {
    var gvsn = new Choices("#" + GAMEVSN_ID, {
        placeholder: true,
    });
    var author = new Choices("#" + AUTHOR_ID, {
        placeholder: true,
    });

    gvsn.ajax(function(callback) {
        fetch('/gamevsns.json')
            .then(function(response) {
                response.json().then(function(data) {
                    console.log(data)
                    callback(data, 'name', 'name');
                });
            })
            .catch(function(error) {
                console.log(error);
            });
    });

    author.ajax(function(callback) {
        fetch('/authors.json')
            .then(function(response) {
                response.json().then(function(data) {
                    console.log(data)
                    callback(data, 'name', 'name');
                });
            })
            .catch(function(error) {
                console.log(error);
            });
    });
}

if (document.getElementById(SEL_FILE_ID)) {
    var upload_row = document.getElementById(UPLOAD_ROW_ID)
    var sel_file = new Choices("#" + SEL_FILE_ID, { });

    sel_file.passedElement.element.addEventListener(
        'change',
        function(event) {
            console.log(event.detail.value);
            if (upload_row) {
                if (event.detail.value >= 0) {
                    upload_row.style.display = 'none';
                } else {
                    upload_row.style.display = 'table-row';
                }
            }
        },
        false,
    );
}

