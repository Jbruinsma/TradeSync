const accountDetailsSection = document.querySelector('.account-details-content')

function toggleAccountDetails() {
    const toggleButtonIcon = document.getElementById('toggle-button-icon');
    const detailsSection = document.getElementById('accountDetails');

    if (detailsSection.classList.contains('hidden')) {
        toggleButtonIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />`;
        detailsSection.classList.remove('hidden');
    } else {
        toggleButtonIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88"></path>`;
        detailsSection.classList.add('hidden');
    }
}

function toggleUpdateAccountDiv() {
    const updateInfoSection = document.getElementById('update-account-form');

    if (updateInfoSection.classList.contains('hidden')) {
        updateInfoSection.classList.remove('hidden');
    } else {
        updateInfoSection.classList.add('hidden');
    }
}

function toggleConfirmation() {
    const removeButton = document.querySelector('.remove-btn');
    const warningText = document.querySelector('.warning-text');
    const cancelButton = document.querySelector('.remove-account-cancel-btn')
    const confirmButton = document.querySelector('.remove-account-confirm-btn')

    removeButton.classList.add('hidden');
    warningText.classList.remove('hidden');
    cancelButton.classList.remove('hidden');
    confirmButton.classList.remove('hidden');
}

function cancelConfirmation() {
    const removeButton = document.querySelector('.remove-btn');
    const warningText = document.querySelector('.warning-text');
    const cancelButton = document.querySelector('.remove-account-cancel-btn')
    const confirmButton = document.querySelector('.remove-account-confirm-btn')

    removeButton.classList.remove('hidden');
    warningText.classList.add('hidden');
    cancelButton.classList.add('hidden');
    confirmButton.classList.add('hidden');
}