// This file contains JavaScript that is only relevant to the editor.

// For hashing files clientside.
const FILE_ID = "file";
const HASH_ID = "file_hash";

// Code to hash files clientside before uploading in order to ensure integrity.
if (document.getElementById(FILE_ID) && document.getElementById(HASH_ID)) {
    var fileSelect = document.getElementById(FILE_ID);
    var fileHashInput = document.getElementById(HASH_ID);

    var reader = new FileReader();
    reader.onload = (event) => {
        crypto.subtle.digest('SHA-256', reader.result).then((digest) => {
            var array = Array.from(new Uint8Array(digest));
            var hexdigest = array.map(b => b.toString(16).padStart(2, '0')).join('');
            console.log('Hash of selected file: ' + hexdigest);
            fileHashInput.value = hexdigest;
        })
    }

    fileSelect.addEventListener('change', (event) => {
        reader.readAsArrayBuffer(event.target.files[0]);
    });
}

