document.getElementById('projectForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Collect form data
    const formData = new FormData(this);
    const data = Object.fromEntries(formData);
    
    // Show loading state
    const submitBtn = document.querySelector('.submit-btn');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '🧠 Initiating Elite Analysis...';
    submitBtn.disabled = true;
    
    // Submit to backend
    fetch('/submit_project', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/status/' + data.project_id;
        } else {
            alert('Error: ' + data.message);
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    })
    .catch(error => {
        alert('Error submitting project. Please try again.');
        console.error('Fetch error:', error); // Log detailed error
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
});