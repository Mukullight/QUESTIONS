// Open a specific modal by ID
function openModal(modalId) {
    document.querySelectorAll('.modal').forEach(modal => modal.style.display = 'none');
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'flex';
}

// Close a specific modal by ID and hide its success message
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
    const successMessage = document.getElementById('success-message-' + modalId.split('-')[1]);
    if (successMessage) successMessage.style.display = 'none';
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.className === 'modal') {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
            const index = modal.id.split('-')[1];
            const successMessage = document.getElementById('success-message-' + index);
            if (successMessage) successMessage.style.display = 'none';
        });
    }
};

// Handle form submission with AJAX and prepend response to history
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.modal form').forEach(form => {
        form.addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent default form submission
            const modalId = this.closest('.modal').id;
            const modalIndex = modalId.split('-')[1];
            const successMessage = document.getElementById('success-message-' + modalIndex);
            const responseList = this.closest('.brutalist-card__message').querySelector('ul');
            const userInput = this.querySelector('textarea[name="user_input"]').value.trim();

            if (userInput) {
                // Show success message
                if (successMessage) successMessage.style.display = 'block';

                // Prepend response to history list (newest first)
                const newResponse = document.createElement('li');
                newResponse.style.backgroundColor = '#222';
                newResponse.style.color = '#fff';
                newResponse.style.padding = '10px';
                newResponse.style.marginBottom = '5px';
                newResponse.style.border = '1px solid #fff';
                newResponse.style.borderRadius = '4px';
                newResponse.textContent = userInput;
                responseList.insertBefore(newResponse, responseList.firstChild);

                // Clear the textarea
                this.querySelector('textarea[name="user_input"]').value = '';

                // Send form data to backend via AJAX
                const formData = new FormData(this);
                const actionUrl = this.action;
                try {
                    const response = await fetch(actionUrl, {
                        method: 'POST',
                        body: formData
                    });
                    if (!response.ok) {
                        console.error('Submission failed:', response.statusText);
                        if (successMessage) successMessage.style.display = 'none';
                        alert('Failed to save response. Please try again.');
                        // Remove the prepended response if backend fails
                        responseList.removeChild(newResponse);
                    }
                } catch (error) {
                    console.error('Error submitting form:', error);
                    if (successMessage) successMessage.style.display = 'none';
                    alert('Error submitting form. Please try again.');
                    // Remove the prepended response if backend fails
                    responseList.removeChild(newResponse);
                }
            }
        });
    });

    // Open modal after page load if modal_index is set (e.g., after page refresh)
    const modalIndex = '{{ modal_index }}';
    if (modalIndex && modalIndex !== 'None') {
        const modalId = 'modal-' + modalIndex;
        const successMessageId = 'success-message-' + modalIndex;
        openModal(modalId);
        const successMessage = document.getElementById(successMessageId);
        if (successMessage) {
            successMessage.style.display = 'block';
            // No setTimeout, success message stays visible until modal is closed
        }
    }
});