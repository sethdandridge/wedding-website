document.addEventListener('DOMContentLoaded', function() {

    const form = document.querySelector('form'); // Select the form
    if (!form) return;
    const submitButton = document.getElementById('submit-button'); // Get the submit button
    const submitButtonDiv = document.getElementById('submit-button-div');
    if (!submitButton) return;
    const isVisible = elem => !!elem && !!( elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length );

    const checkInputs = () => {
        // Get all input elements within the form that are not hidden and are required
        const neverHiddenInputs = form.querySelectorAll('.never-hidden-input');
        // Create list of lists of neverHiddenInputs, grouped by the name attribute
        const neverHiddenInputsGrouped = Array.from(neverHiddenInputs).reduce((acc, input) => {
            if (!acc[input.name]) {
                acc[input.name] = [];
            }
            acc[input.name].push(input);
            return acc;
        }, {});
        // Make sure there is at least one selection for each group in neverHiddenInputsGrouped
        let allFilled = Object.values(neverHiddenInputsGrouped).every(group => {
            return group.some(input => input.checked);
        });
        //let allFilled = !Array.from(neverHiddenInputs).every(input => {return !input.checked});
        const possiblyHiddenInputDivs = form.querySelectorAll('.possibly-hidden-input');

        possiblyHiddenInputDivs.forEach(inputDiv => {
            if (isVisible(inputDiv)) {
                let inputs = inputDiv.querySelectorAll('input');
                if (inputs[0].attributes.type.value === 'radio' && !inputs[0].checked && !inputs[1].checked) {
                    allFilled = false;
                }
                if (inputs[0].attributes.type.value === 'text' && inputs[0].value === '') {
                    allFilled = false;
                }
            }
        });

        // Toggle the display of the submit button based on whether all conditions are met
        if (allFilled) {
            submitButtonDiv.classList.remove('d-none');
        } else {
            submitButtonDiv.classList.add('d-none');
        }
    };

    const checkSubmitText = () => {
        const neverHiddenInputs = form.querySelectorAll('.never-hidden-input');
        // Create a list of neverHiddenInputs only if the id ends in 'yes'
        const neverHiddenInputsYes = Array.from(neverHiddenInputs).filter(input => input.id.endsWith('yes'));
        // Check if any of the yes inputs are checked
        const anyYesChecked = neverHiddenInputsYes.some(input => input.checked);
        if (!submitButton.classList.contains('dont-toggle')) {
            anyYesChecked ? submitButton.innerText = 'Next Event' : submitButton.innerText = 'Submit';
        }
    };

    // Event listener for changes on radio inputs to handle visibility of related fields
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
          checkInputs();
          checkSubmitText();
        });
    });

    document.querySelectorAll('.possibly-hidden-input').forEach(radio=> {
        radio.addEventListener('change', function() {
          checkInputs();
        });
    });

    // Listener for input events on all inputs
    form.addEventListener('input', checkInputs);

    // Initial check on load
    checkInputs();
});
