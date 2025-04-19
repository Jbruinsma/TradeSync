document.addEventListener('DOMContentLoaded', function(){
    const logoutButton = document.querySelector('.u-logout');
    const modal = document.getElementById("logoutModal");
    const cancelLogout = document.getElementById("cancelLogout");

    if (logoutButton){
        logoutButton.addEventListener('click', function(){
          modal.classList.remove('hidden');
        })
    }

    cancelLogout.addEventListener("click", function() {
        modal.classList.add('hidden')
    });

    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
})