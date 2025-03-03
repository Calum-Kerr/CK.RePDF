document.addEventListener('DOMContentLoaded', function() {
    const editor = document.getElementById('pdf-editor');
    const saveBtn = document.getElementById('save-btn');
    const downloadBtn = document.getElementById('download-btn');
    
    // Enable contenteditable on the PDF content
    if (editor) {
        // Add visual indicator when editing
        editor.addEventListener('focus', function() {
            this.classList.add('editing');
        });
        
        editor.addEventListener('blur', function() {
            this.classList.remove('editing');
        });
    }
    
    // Save button functionality
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            const content = editor.innerHTML;
            
            // Send edited content to server
            fetch('/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `content=${encodeURIComponent(content)}`
            })
            .then(response => response.text())
            .then(data => {
                alert('Changes saved successfully');
            })
            .catch(error => {
                alert('Error saving changes: ' + error);
            });
        });
    }
    
    // Download button functionality (placeholder for future implementation)
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            alert('This feature will be implemented in a future version.');
            // Future implementation could convert the HTML back to PDF
            // using a server-side conversion or a client-side library
        });
    }
});
