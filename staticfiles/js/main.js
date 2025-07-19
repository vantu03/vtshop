function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    const countEl = document.getElementById('cartItemCount');

    if (countEl) {
        countEl.textContent = count;
        countEl.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    updateCartCount();
});
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.clearable-input').forEach(function (input) {
        const wrapper = document.createElement('div');
        wrapper.className = 'position-relative w-100';

        const clearBtn = document.createElement('i');
        clearBtn.className = 'bi bi-x-lg position-absolute end-0 top-50 translate-middle-y me-2 d-none text-secondary fs-5';
        clearBtn.style.cursor = 'pointer';
        clearBtn.setAttribute('role', 'button');

        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        wrapper.appendChild(clearBtn);

        input.addEventListener('input', function () {
            clearBtn.classList.toggle('d-none', !this.value.length);
        });

        clearBtn.addEventListener('click', function () {
            input.value = '';
            input.focus();
            clearBtn.classList.add('d-none');
        });
    });
});
