function revealDiv() {
    const riskTypeContentDiv = document.querySelector('.risk-type-settings-div');
    if (riskTypeContentDiv.classList.contains('hidden')) {
        riskTypeContentDiv.classList.remove('hidden');
    }
}

function monitorRiskType() {
    const riskTypeSelect = document.getElementById("risk-type");
    const riskTypeContentDiv = document.querySelector('.risk-type-settings-div');

    function updateRiskType() {
        const selectedValue = riskTypeSelect.value;
        if (selectedValue === "fixed") {
            console.log('fixed risk type');
            revealDiv();
            riskTypeContentDiv.innerHTML = `<div class="settings-label">
                <label>Risk Type: </label>
               Fixed Lot
            </div>
            <div class="form-group">
               <label for="fixed-lot-size">Fixed Lot Size:</label>
               <input type="number" id="fixed-lot-size" name="fixed_lot_size" step="0.01" min="0.01" placeholder="">
            </div>
            <div class="form-group">
               <label for="fixed-sl">Fixed Stop Loss (pips):</label>
               <input type="number" id="fixed-sl" name="fixed_sl" step="1" min="0" placeholder="">
            </div>
            <div class="form-group">
               <label for="fixed-tp">Fixed Take Profit (pips):</label>
               <input type="number" id="fixed-tp" name="fixed_tp" step="1" min="0" placeholder="">
            </div>
         </div>`;

        } else if (selectedValue === "multiplier") {
            console.log('multiplier');
            revealDiv();
            riskTypeContentDiv.innerHTML = `<div class="settings-label">
               Risk Type: Multiplier
            </div>
             <div class="form-group">
            <label for="multiplier-factor">Multiplier Factor:</label>
            <input type="number" id="multiplier-factor" name="multiplier_factor" step="0.1" min="0.1" placeholder="1.0">
            <span class="conversion-rate"></span>
             </div>
             <div class="form-group">
                 <label class="switch">
            <span>Enable Account Balance Scaling:</span>
            <input type="checkbox" checked>
            <span class="slider round"></span>
            </label>
             </div>`;

        }
    }

    riskTypeSelect.addEventListener("change", updateRiskType);
}

monitorRiskType();