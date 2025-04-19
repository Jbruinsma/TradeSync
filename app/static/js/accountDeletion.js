function deleteAccount(){
    const deleteAccountButton = document.querySelector('.delete-btn');
    const cancelButton = document.querySelector('.delete-btn-cancel');
    const confirmButton = document.querySelector('.delete-btn-confirm');

    deleteAccountButton.classList.add('hidden');
    cancelButton.classList.remove('hidden');
    confirmButton.classList.remove('hidden');
}

function cancelDeletion(){
    const deleteAccountButton = document.querySelector('.delete-btn');
    const cancelButton = document.querySelector('.delete-btn-cancel');
    const confirmButton = document.querySelector('.delete-btn-confirm');

    deleteAccountButton.classList.remove('hidden');
    cancelButton.classList.add('hidden');
    confirmButton.classList.add('hidden');
}