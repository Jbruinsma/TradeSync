const container = document.querySelector('.settings-container');

const userInfoTab = document.querySelector('.u-info');
const userSettingsTab = document.querySelector('.u-settings');
const userPasswordTab = document.querySelector('.u-password');

const userInfoDiv = document.querySelector('.user-info-div');
const userSettingsDiv = document.querySelector('.user-settings-div');
const userPasswordDiv = document.querySelector('.user-password-div');

function checkOtherTabs(tab1, tab2, activeTab) {
    if (tab1.classList.contains('active-tab')) {
        tab1.classList.remove('active-tab');
    }
    if (tab2.classList.contains('active-tab')) {
        tab2.classList.remove('active-tab');
    }
    activeTab.classList.add('active-tab');
}

function checkOtherDivs(div1, div2, activeDiv) {
    if (!div1.classList.contains('hidden')) {
        div1.classList.add('hidden');
    }        
    if (!div2.classList.contains('hidden')) {
        div2.classList.add('hidden');
    }
    activeDiv.classList.remove('hidden');
}

function loadUserInfoTab() {
    checkOtherDivs(userSettingsDiv, userPasswordDiv, userInfoDiv);
    checkOtherTabs(userSettingsTab, userPasswordTab, userInfoTab);
}

function loadUserSettingsTab() {
    checkOtherDivs(userInfoDiv, userPasswordDiv, userSettingsDiv);
    checkOtherTabs(userInfoTab, userPasswordTab, userSettingsTab);
}

function loadUserPasswordTab() {
    checkOtherDivs(userInfoDiv, userSettingsDiv, userPasswordDiv);
    checkOtherTabs(userInfoTab, userSettingsTab, userPasswordTab);
}

document.addEventListener('DOMContentLoaded', function() {
    loadUserInfoTab();
    userInfoTab.addEventListener('click', loadUserInfoTab);
    userSettingsTab.addEventListener('click', loadUserSettingsTab);
    userPasswordTab.addEventListener('click', loadUserPasswordTab);
})