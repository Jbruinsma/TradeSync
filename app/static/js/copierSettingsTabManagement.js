const generalSettingsTab = document.querySelector('.general-btn');
const copyingPreferencesTab = document.querySelector('.copying-preferences-btn');
const riskManagementTab = document.querySelector('.risk-management-btn');
const executionsTab = document.querySelector('.executions-btn');

const contentContainer = document.querySelector('.settings-div');
const riskTypeSettingsDiv = document.querySelector('.risk-type-settings-div');

function switchTabState(btn1, btn2, btn3, activeTab) {
    if (btn1.classList.contains('active-tab')) {
        btn1.classList.remove('active-tab');
    }
    if (btn2.classList.contains('active-tab')) {
        btn2.classList.remove('active-tab');
    }
    if (btn3.classList.contains('active-tab')) {
        btn3.classList.remove('active-tab');
    }

    activeTab.classList.add('active-tab');

    if (!riskTypeSettingsDiv.classList.contains('hidden')) {
        riskTypeSettingsDiv.classList.add('hidden');
    }

}

function loadGeneralSettingsTab() {
    switchTabState(copyingPreferencesTab, riskManagementTab, executionsTab, generalSettingsTab);
    contentContainer.innerHTML = `<form action="/your-form-action" method="POST">
                   <div class="form-group">
                   <label for="account-name">Custom Account Name:</label>
                   <input type="text" id="account-name" name="account_name" placeholder="{{ account_name }}">
                   </div>
            <div class="form-group">
                <label for="master-account">Master Account:</label>
                <select id="master-account" name="master-account" required>
                    <option value="" disabled>Select a master account</option>
                    <option value="" selected>None</option>
                    <option value="">ACCOUNT NULL</option>
                </select>
            </div>
           <button class="username-change-submit submit-btn" type="submit">Update</button>
        </form>`;
}

function loadCopyingPreferencesTab() {
    switchTabState(generalSettingsTab, riskManagementTab, executionsTab, copyingPreferencesTab);
    contentContainer.innerHTML = `<form action="/your-form-action" method="POST">
            <div class="form-group">
                <label for="trade-types">Trade Types:</label>
                <select id="trade-types" name="trade-types" required>
                    <option value="" disabled>Select executable trade types</option>
                    <option value="all" selected>All</option>
                    <option value="buy">Buy</option>
                    <option value="sell">Sell</option>
                </select>
            </div>
                   <div class="form-group">
                   <label for="order-types">Trade Types:</label>
                <select id="order-types" name="order-types" required>
                    <option value="" disabled>Select executable order types</option>
                    <option value="all" selected>All</option>
                    <option value="market">Market</option>
                    <option value="limit">Limit</option>
                    <option value="stop">Stop</option>
                </select>
                   </div>
           <button class="username-change-submit submit-btn" type="submit">Update</button>
        </form>`;
}

function loadRiskManagementTab() {
    switchTabState(generalSettingsTab, copyingPreferencesTab, executionsTab, riskManagementTab);
    contentContainer.innerHTML = `<form action="/your-form-action" method="POST">
            <div class="form-group">
               <label for="min-trade-size">Minimum Trade Size (lots):</label>
               <input type="number" id="min-trade-size" name="min_trade_size" step="0.01" min="0.01" placeholder="0.01">
            </div>
            <div class="form-group">
               <label for="max-trade-size">Maximum Trade Size (lots):</label>
               <input type="number" id="max-trade-size" name="max_trade_size" step="0.01" min="0.01">
            </div>
            <div class="form-group">
               <label for="max-open-positions">Maximum Open Positions:</label>
               <input type="number" id="max-open-positions" name="max_open_positions" min="1" value="" placeholder="">
            </div>
            <div class="form-group">
               <label for="risk-type">Risk Type:</label>
               <select id="risk-type" name="risk_type">
                  <option value="fixed">Fixed Lots</option>
                  <option value="multiplier">Multiplier</option>
               </select>
            </div>
            <button class="username-change-submit submit-btn" type="submit">Update</button>
        </form>`;
    let script = document.createElement("script");
    script.src = riskSettingsScript;
    script.async = true;
    document.body.appendChild(script);
}

function loadExecutionsTab() {
    switchTabState(generalSettingsTab, copyingPreferencesTab, riskManagementTab, executionsTab)
    contentContainer.innerHTML = `<form action="/your-form-action" method="POST">
              <div class="form-group">
              <label for="trade-closure">Trade Closure Handling:</label>
        <select id="trade-closure" name="trade_closure">
            <option value="" disabled selected>Select a trade closure approach</option>
            <option value="auto">Follow Master</option>
            <option value="manual">Manage Independently</option>
        </select>
              </div>
          </form>`;
}

generalSettingsTab.addEventListener('click', loadGeneralSettingsTab);
copyingPreferencesTab.addEventListener('click', loadCopyingPreferencesTab);
riskManagementTab.addEventListener('click', loadRiskManagementTab);
executionsTab.addEventListener('click', loadExecutionsTab);

document.addEventListener('DOMContentLoaded', loadGeneralSettingsTab);