document.addEventListener("DOMContentLoaded", function() {
    const multiplierInput = document.querySelector('.multiplier-factor');
    const childAccountRiskAmount = document.querySelector('.child-risk-amount');
    const lotsWord = document.querySelector('.lots-word');

    multiplierInput.addEventListener('input', function() {
        let value = parseFloat(multiplierInput.value);

        if (!isNaN(value) && value >= 0.01) {
            childAccountRiskAmount.textContent = value.toFixed(2);
            lotsWord.textContent = (value === 1) ? "Lot" : "Lots";
        } else {
            childAccountRiskAmount.textContent = "1";
            lotsWord.textContent = "Lot";
        }
    });
});
