document.addEventListener('DOMContentLoaded', function() {
    // Handle dropdown toggles
    const dropdowns = document.querySelectorAll('.custom-dropdown');
    
    dropdowns.forEach(dropdown => {
        const header = dropdown.querySelector('.dropdown-header');
        
        header.addEventListener('click', () => {
            // Close all other dropdowns
            dropdowns.forEach(d => {
                if (d !== dropdown) {
                    d.classList.remove('active');
                }
            });
            
            // Toggle current dropdown
            dropdown.classList.toggle('active');
        });
        
        // Update header text based on selections
        const content = dropdown.querySelector('.dropdown-content');
        const checkboxes = content.querySelectorAll('input[type="checkbox"]');
        
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                updateDropdownHeader(dropdown);
            });
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.custom-dropdown')) {
            dropdowns.forEach(d => d.classList.remove('active'));
        }
    });
    
    // Handle "All" checkbox logic
    function handleAllCheckbox(container) {
        const allCheckbox = container.querySelector('input[type="checkbox"]');
        const otherCheckboxes = Array.from(container.querySelectorAll('input[type="checkbox"]')).slice(1);
        
        allCheckbox.addEventListener('change', () => {
            // When "All" is selected, uncheck all other options
            if (allCheckbox.checked) {
                otherCheckboxes.forEach(cb => {
                    cb.checked = false;
                });
                updateDropdownHeader(container.closest('.custom-dropdown')); // Update header after changes
            }
        });
        
        otherCheckboxes.forEach(cb => {
            cb.addEventListener('change', () => {
                // If all individual options are selected, uncheck them and check "All"
                const allIndividualChecked = otherCheckboxes.every(cb => cb.checked);
                if (allIndividualChecked) {
                    otherCheckboxes.forEach(cb => {
                        cb.checked = false;
                    });
                    allCheckbox.checked = true;
                    updateDropdownHeader(container.closest('.custom-dropdown')); // Update header after changes
                }
                // If "All" is checked and an individual option is selected, uncheck "All"
                if (allCheckbox.checked && cb.checked) {
                    allCheckbox.checked = false;
                    updateDropdownHeader(container.closest('.custom-dropdown')); // Update header after changes
                }
            });
        });
    }
    
    // Initialize "All" checkbox logic for both dropdowns
    document.querySelectorAll('.dropdown-content').forEach(handleAllCheckbox);
});

function updateDropdownHeader(dropdown) {
    const header = dropdown.querySelector('.dropdown-header');
    const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');
    const allCheckbox = checkboxes[0];
    const otherCheckboxes = Array.from(checkboxes).slice(1);
    
    // Check if all individual options are selected
    const allIndividualChecked = otherCheckboxes.every(cb => cb.checked);
    
    if (allCheckbox.checked || allIndividualChecked) {
        header.textContent = 'All';
        // If all individuals are checked, switch to "All" checkbox
        if (allIndividualChecked && !allCheckbox.checked) {
            otherCheckboxes.forEach(cb => { cb.checked = false; });
            allCheckbox.checked = true;
        }
    } else {
        const selectedCheckboxes = otherCheckboxes.filter(cb => cb.checked);
        if (selectedCheckboxes.length === 0) {
            header.textContent = 'Select Options';
        } else {
            const labels = selectedCheckboxes.map(cb => cb.nextElementSibling.textContent);
            header.textContent = labels.join(', ');
        }
    }
} 