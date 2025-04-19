document.addEventListener("DOMContentLoaded", function() {
    console.log('modalManager loaded');
    const removeAccountBtns = document.querySelectorAll('.remove');
    const modal = document.getElementById("removeModal");
    const cancelRemoval = document.getElementById("cancelRemoval");
    const confirmRemoveBtn = document.getElementById('confirmRemoval');
    const accountNameSpan = document.querySelector('.account-to-be-removed');
    let accountId;
    let accountName;

    if (removeAccountBtns.length > 0){
        removeAccountBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                accountId = this.getAttribute("data-account-id");
                accountName = this.getAttribute("data-account-name");
                modal.classList.remove('hidden');
                accountNameSpan.textContent = accountName;
            })
        })
    }

    cancelRemoval.addEventListener('click', function(){
        modal.classList.add('hidden');
    })

    if (confirmRemoveBtn) {
        confirmRemoveBtn.addEventListener('click', function () {
            console.log('removing account...');
            console.log(accountId);
            const removalUrl = baseRemovalLink.replace('ACCOUNT_ID', accountId);
            window.location.href = removalUrl;
        })
    }

});
