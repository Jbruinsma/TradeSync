function showAccountTable(){
    const accountButton = document.querySelector('.account-btn');
    const openPositionsButton = document.querySelector('.open-positions-btn');
    const accountSection = document.getElementById("account-section");
    const openPositionsSection = document.getElementById("open-positions-section");

    openPositionsButton.classList.remove('active');
    accountButton.classList.add('active');
    openPositionsSection.classList.add('hidden');
    accountSection.classList.remove('hidden');
}

function showOpenPositionsTable(){
    const accountButton = document.querySelector('.account-btn');
    const openPositionsButton = document.querySelector('.open-positions-btn');
    const accountSection = document.getElementById("account-section");
    const openPositionsSection = document.getElementById("open-positions-section");

    accountButton.classList.remove('active');
    openPositionsButton.classList.add('active');
    accountSection.classList.add('hidden');
    openPositionsSection.classList.remove('hidden');

}
