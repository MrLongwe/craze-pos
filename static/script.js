// Cart State
let cart = [];
let cartOpen = false;
let currentMode = 'delivery';

// Toggle Cart Drawer
function toggleCart() {
    cartOpen = !cartOpen;
    const overlay = document.getElementById('cartOverlay');
    const drawer = document.getElementById('cartDrawer');
    
    if (cartOpen) {
        overlay.classList.add('open');
        drawer.classList.add('open');
        document.body.style.overflow = 'hidden';
    } else {
        overlay.classList.remove('open');
        drawer.classList.remove('open');
        document.body.style.overflow = '';
    }
}

// Set Delivery/Pickup Mode
function setMode(mode) {
    currentMode = mode;
    const buttons = document.querySelectorAll('.toggle-btn');
    buttons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(mode)) {
            btn.classList.add('active');
        }
    });
    
    // Show toast notification
    showToast(`${mode === 'delivery' ? '🚚' : '🏃'} ${mode.charAt(0).toUpperCase() + mode.slice(1)} mode selected`);
}

// Add to Cart
function addToCart(item) {
    const existingItem = cart.find(i => i.id === item.id);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ ...item, quantity: 1 });
    }
    
    updateCartUI();
    
    // Animate cart badge
    const badge = document.getElementById('cartCount');
    badge.style.animation = 'none';
    badge.offsetHeight; // Trigger reflow
    badge.style.animation = 'pop 0.3s ease';
    
    // Show mini notification
    showToast(`🍟 Added ${item.name} to cart`);
}

// Remove from Cart
function removeFromCart(itemId) {
    cart = cart.filter(item => item.id !== itemId);
    updateCartUI();
}

// Update Quantity
function updateQuantity(itemId, change) {
    const item = cart.find(i => i.id === itemId);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(itemId);
        } else {
            updateCartUI();
        }
    }
}

// Update Cart UI
function updateCartUI() {
    const cartItems = document.getElementById('cartItems');
    const cartCount = document.getElementById('cartCount');
    const cartTotal = document.getElementById('cartTotal');
    
    // Update count
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = totalItems;
    
    // Update items
    if (cart.length === 0) {
        cartItems.innerHTML = `
            <div style="text-align: center; padding: var(--spacing-xl); color: var(--muted-foreground);">
                <div style="font-size: 3rem; margin-bottom: var(--spacing-md);">🛒</div>
                <p>Your cart is empty</p>
                <p style="font-size: 0.875rem;">Add some crispy items to get started!</p>
            </div>
        `;
    } else {
        let itemsHtml = '';
        let total = 0;
        
        cart.forEach(item => {
            total += item.price * item.quantity;
            itemsHtml += `
                <div class="cart-item">
                    <img src="${item.image || 'https://via.placeholder.com/60'}" alt="${item.name}" class="cart-item-image">
                    <div class="cart-item-details">
                        <div class="cart-item-title">${item.name}</div>
                        <div class="cart-item-price">$${item.price.toFixed(2)}</div>
                        <div class="cart-item-actions">
                            <button class="cart-quantity-btn" onclick="updateQuantity('${item.id}', -1)">−</button>
                            <span style="min-width: 24px; text-align: center;">${item.quantity}</span>
                            <button class="cart-quantity-btn" onclick="updateQuantity('${item.id}', 1)">+</button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        cartItems.innerHTML = itemsHtml;
        cartTotal.textContent = `$${total.toFixed(2)}`;
        
        // Update points earned
        const pointsEarned = Math.floor(total * 10);
        document.getElementById('pointsEarned').textContent = `(+${pointsEarned} pts)`;
    }
}

// Checkout
function checkout() {
    if (cart.length === 0) {
        showToast('Your cart is empty!', 'error');
        return;
    }
    
    // Calculate total and points
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const pointsEarned = Math.floor(total * 10);
    
    // Show checkout confirmation
    if (confirm(`Ready to order?\n\nTotal: $${total.toFixed(2)}\nPoints to earn: ${pointsEarned}\n\nProceed to checkout?`)) {
        // Simulate order placement
        showToast('🎉 Order placed! Points added to your account.');
        cart = [];
        updateCartUI();
        toggleCart();
        
        // Trigger confetti for celebration
        celebrateOrder();
    }
}

// Show Toast Notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'success' ? 'var(--primary)' : 'var(--error)'};
        color: white;
        padding: 12px 24px;
        border-radius: var(--radius-full);
        font-family: var(--font-display);
        font-weight: 500;
        z-index: 1000;
        animation: slideUp 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideUp 0.3s reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Celebrate Order
function celebrateOrder() {
    const colors = ['hsl(22, 79%, 44%)', 'hsl(45, 100%, 51%)', 'white'];
    
    for (let i = 0; i < 30; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: fixed;
                top: -10px;
                left: ${Math.random() * 100}vw;
                width: ${Math.random() * 10 + 5}px;
                height: ${Math.random() * 10 + 5}px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                border-radius: 2px;
                animation: confetti ${Math.random() * 2 + 2}s ease-out forwards;
                z-index: 1001;
            `;
            document.body.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 3000);
        }, i * 50);
    }
}

// Add confetti animation
const style = document.createElement('style');
style.textContent = `
    @keyframes confetti {
        0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
        }
        100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
        }
    }
    
    @keyframes slideUp {
        from {
            transform: translate(-50%, 100%);
            opacity: 0;
        }
        to {
            transform: translate(-50%, 0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load sample menu items
    loadMenuItems();
    
    // Check for reward celebration on success page
    if (document.querySelector('.reward-celebration')) {
        celebrateOrder();
    }
    
    // Add stagger animation to cards
    const cards = document.querySelectorAll('.menu-item');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
});

// Load Menu Items (sample data)
function loadMenuItems() {
    const menuItems = [
        { id: 1, name: 'Classic Fries', price: 4.99, description: 'Crispy golden fries with sea salt', category: 'fries', image: '🍟' },
        { id: 2, name: 'Craze Chicken', price: 8.99, description: 'Signature spicy fried chicken', category: 'chicken', image: '🍗' },
        { id: 3, name: 'Loaded Fries', price: 7.99, description: 'Fries topped with cheese and bacon', category: 'fries', image: '🧀' },
        { id: 4, name: 'Chicken Tenders', price: 6.99, description: 'Hand-breaded chicken tenders', category: 'chicken', image: '🍗' },
        { id: 5, name: 'Curly Fries', price: 5.99, description: 'Seasoned curly fries', category: 'fries', image: '🍟' },
        { id: 6, name: 'Spicy Wings', price: 9.99, description: '6 pieces of spicy chicken wings', category: 'chicken', image: '🍗' }
    ];
    
    const menuGrid = document.querySelector('.menu-grid');
    if (menuGrid) {
        menuGrid.innerHTML = menuItems.map(item => `
            <div class="menu-item">
                <div class="menu-item-image" style="display: flex; align-items: center; justify-content: center; font-size: 3rem; background: var(--muted);">
                    ${item.image}
                </div>
                <div class="menu-item-content">
                    <div class="menu-item-header">
                        <span class="menu-item-title">${item.name}</span>
                        <span class="menu-item-price">$${item.price.toFixed(2)}</span>
                    </div>
                    <p class="menu-item-description">${item.description}</p>
                    <button class="add-to-cart" onclick='addToCart(${JSON.stringify(item).replace(/'/g, "\\'")})'>
                        <span>Add to Cart</span>
                        <span style="font-size: 1.2rem;">+</span>
                    </button>
                </div>
            </div>
        `).join('');
    }
}