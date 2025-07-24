function validateInput() {
    let inputs = document.querySelectorAll("input[required]");
    for (let input of inputs) {
        if (input.value.trim() === "") {
            alert("Oi, fill in all the required stuff lah!");
            return false;
        }
    }
    return true;
}