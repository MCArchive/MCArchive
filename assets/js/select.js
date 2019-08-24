import Choices from 'choices.js';
window.Choices = Choices;

// Code to initialize the search form.
const GAMEVSN_ID = "gamevsn";
const AUTHOR_ID = "author";

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

