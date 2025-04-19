function initiateReveal(){
    const riskTypeContentDiv1 = document.querySelector('.risk-type-settings-div');
    const riskTypeContentDiv2 = document.querySelector('.risk-type-content');

    if (riskTypeContentDiv2 == null && riskTypeContentDiv1 != null) {
        revealDiv(riskTypeContentDiv1);
        return riskTypeContentDiv1;
    } else if (riskTypeContentDiv1 == null && riskTypeContentDiv2 != null) {
        revealDiv(riskTypeContentDiv2);
        return riskTypeContentDiv2;
    } else {
        console.log('error, no risk types found.');
        return null;
    }
}

function revealDiv(contentDiv) {
     if (contentDiv.classList.contains('hidden')) {
        contentDiv.classList.remove('hidden');
    }
}

function monitorRiskType() {
    const riskTypeSelect = document.getElementById("risk-type");

    function updateRiskType(div) {
        const selectedValue = riskTypeSelect.value;
        if (selectedValue === "fixed") {
            console.log('fixed risk type');
            const div = initiateReveal()
            div.innerHTML = `<div class="title-container">
        <h2>Fixed Lot Settings</h2>
    </div>
    <label for="fixed-lot-size">Fixed Lot Size:</label>
    <input type="number" id="fixed-lot-size" name="fixed_lot_size" step="0.01" min="0.01" placeholder="">
    <label for="fixed-sl">Fixed Stop Loss (pips):</label>
    <input type="number" id="fixed-sl" name="fixed_sl" step="1" min="0" placeholder="">
    <label for="fixed-tp">Fixed Take Profit (pips):</label>
    <input type="number" id="fixed-tp" name="fixed_tp" step="1" min="0" placeholder="">`;

        } else if (selectedValue === "multiplier") {
            console.log('multiplier');
            const div = initiateReveal();
            div.innerHTML = `<div class="title-container">
               <h2>Multiplier Settings</h2>
            </div>
            <label for="multiplier-factor">Multiplier Factor:</label>
            <input type="number" id="multiplier-factor" name="multiplier_factor" step="0.1" min="0.1" placeholder="1.0">
            <label class="switch">
            <span>Enable Account Balance Scaling:</span>
            <input type="checkbox" checked>
            <span class="slider round"></span>
            </label>`;

        }
    }

    riskTypeSelect.addEventListener("change", updateRiskType);
}

monitorRiskType();