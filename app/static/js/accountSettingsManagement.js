const overviewSectionButton = document.querySelector('.overview-btn');
const accountManagementSectionButton = document.querySelector('.account-management-btn');
const equityMonitorSectionButton = document.querySelector('.equity-monitor-btn');

const overviewSection = document.querySelector('.account-overview');
const accountManagementSection = document.querySelector('.account-account-management');
const equityMonitorSection = document.querySelector('.account-equity_monitor');

function removeActiveTabClass(btn1, btn2){
    btn1.classList.remove('active-tab');
    btn2.classList.remove('active-tab');
}

function hideSections(section1, section2){
    if (!section1.classList.contains('hidden')) {
        section1.classList.add('hidden');
    }
    if (!section2.classList.contains('hidden')) {
        section2.classList.add('hidden');
    }
}

function loadOverviewContent(){
    removeActiveTabClass(accountManagementSectionButton, equityMonitorSectionButton);
    overviewSectionButton.classList.add('active-tab');
    hideSections(accountManagementSection, equityMonitorSection);
    overviewSection.classList.remove('hidden');
}

function loadAccountManagementContent(){
    removeActiveTabClass(overviewSectionButton, equityMonitorSectionButton);
    accountManagementSectionButton.classList.add('active-tab');
    hideSections(overviewSection, equityMonitorSection);
    accountManagementSection.classList.remove('hidden');
}

function loadEquityMonitorContent(){
    removeActiveTabClass(overviewSectionButton, accountManagementSectionButton);
    equityMonitorSectionButton.classList.add('active-tab');
    hideSections(overviewSection, accountManagementSection);
    equityMonitorSection.classList.remove('hidden');
}

document.addEventListener('DOMContentLoaded', function(){
    loadOverviewContent();
});