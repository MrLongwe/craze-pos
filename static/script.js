// Confetti celebration
function celebrateReward() {
    const colors = ['#C4511A', '#FFC107', '#FFFFFF'];
    for (let i = 0; i < 50; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + 'vw';
            confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.width = Math.random() * 10 + 5 + 'px';
            confetti.style.height = confetti.style.width;
            confetti.style.animationDuration = Math.random() * 2 + 2 + 's';
            document.body.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 3000);
        }, i * 50);
    }
}

// Form validation
function validatePIN(pin) {
    return /^\d{4}$/.test(pin);
}

function validateUsername(username) {
    return /^[a-zA-Z0-9_]{3,20}$/.test(username);
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.background = type === 'success' ? '#C4511A' : '#dc3545';
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideUp 0.3s reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Animate progress bar
function animateProgressBar(percent) {
    const bar = document.querySelector('.progress-fill');
    if (bar) {
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = percent + '%';
        }, 100);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add floating animation to icons
    const icons = document.querySelectorAll('.accent');
    icons.forEach(icon => {
        icon.style.animation = 'float 3s ease-in-out infinite';
    });
    
    // Check for reward celebration
    if (document.querySelector('.reward-celebration')) {
        celebrateReward();
    }
});