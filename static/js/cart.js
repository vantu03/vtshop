class CartManager {
    constructor() {
        this.cart = [];
        this.cartContainer = document.getElementById('cartContainer');
        this.emptyCartMessage = document.getElementById('emptyCartMessage');
        this.cartTotalEl = document.getElementById('cartTotal');
        this.init();
    }

    init() {
        this.cart = JSON.parse(localStorage.getItem('cart') || '[]');
        const promises = [];
        this.cartContainer.innerHTML = '';

        for (let item of this.cart) {
            const wrapper = document.createElement('div');
            wrapper.className = 'd-flex bg-white shadow-sm p-3 rounded align-items-center justify-content-between flex-wrap gap-3';
            wrapper.dataset.variantId = item.variant_id;
            this.cartContainer.appendChild(wrapper);

            const promise = new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('GET', `/get/variant/${item.variant_id}/`, true);
                xhr.onreadystatechange = () => {
                    if (xhr.readyState === 4) {
                        if (xhr.status === 200) {
                            const data = JSON.parse(xhr.responseText);
                            wrapper.dataset.price = data.price;

                            const img = document.createElement('img');
                            img.src = data.thumbnail;
                            img.alt = data.product_name;
                            img.style = 'width: 80px; height: 80px; object-fit: contain;';
                            img.className = 'rounded';

                            const info = document.createElement('div');
                            info.className = 'flex-grow-1';
                            const name = document.createElement('div');
                            name.className = 'fw-bold mb-1';
                            const link = document.createElement('a');
                            link.href = `/product/${data.product_slug}/`;
                            link.className = 'text-decoration-none text-dark';
                            link.textContent = data.product_name;
                            name.appendChild(link);
                            info.appendChild(name);

                            const variantInfo = document.createElement('div');
                            variantInfo.className = 'small text-muted';
                            variantInfo.innerHTML = data.variant_name;
                            info.appendChild(variantInfo);

                            const right = document.createElement('div');
                            right.className = 'text-end';

                            const price = document.createElement('div');
                            price.className = 'text-danger fw-bold mb-2';
                            price.textContent = `${data.price.toLocaleString()}₫`;

                            const qtyGroup = document.createElement('div');
                            qtyGroup.className = 'input-group input-group-sm mb-2';
                            qtyGroup.style = 'width: 120px;';

                            const minusBtn = document.createElement('button');
                            minusBtn.className = 'btn btn-outline-secondary';
                            minusBtn.type = 'button';
                            minusBtn.textContent = '−';

                            const qtyInput = document.createElement('input');
                            qtyInput.type = 'number';
                            qtyInput.className = 'form-control text-center';
                            qtyInput.min = 1;
                            qtyInput.value = item.quantity;
                            qtyInput.dataset.variantId = item.variant_id;

                            const plusBtn = document.createElement('button');
                            plusBtn.className = 'btn btn-outline-secondary';
                            plusBtn.type = 'button';
                            plusBtn.textContent = '+';

                            qtyGroup.append(minusBtn, qtyInput, plusBtn);

                            const removeBtn = document.createElement('button');
                            removeBtn.className = 'btn btn-sm btn-outline-danger';
                            removeBtn.innerHTML = '<i class="bi bi-trash"></i> Xoá';
                            removeBtn.dataset.variantId = item.variant_id;

                            right.append(price, qtyGroup, removeBtn);
                            wrapper.append(img, info, right);

                            plusBtn.onclick = () => {
                                item.quantity += 1;
                                this.update();
                            };
                            minusBtn.onclick = () => {
                                item.quantity = Math.max(1, item.quantity - 1);
                                this.update();
                            };
                            qtyInput.onchange = () => {
                                item.quantity = parseInt(qtyInput.value);
                                this.update();
                            };

                            removeBtn.onclick = () => {

                                const confirmModal = new bootstrap.Modal(document.getElementById('confirmRemoveModal'));
                                const confirmMessage = document.getElementById('confirmRemoveMessage');
                                const confirmBtn = document.getElementById('confirmRemoveBtn');

                                confirmBtn.onclick = null;

                                confirmBtn.onclick = () => {
                                    wrapper.remove();
                                    this.cart = this.cart.filter(p => p.variant_id != item.variant_id);
                                    this.update();
                                    confirmModal.hide();
                                };

                                confirmModal.show();
                            };

                            resolve();
                        } else {
                            reject();
                        }
                    }
                };
                xhr.send();
            });

            promises.push(promise);
        }

        // Chờ tất cả request xong mới update tổng tiền
        Promise.all(promises).then(() => this.update());
    }

    update() {
        let total = 0;
        this.cart.forEach(item => {
            if (item.quantity < 1) item.quantity = 1;

            const row = document.querySelector(`[data-variant-id="${item.variant_id}"]`);
            if (row) {
                const price = parseFloat(row.dataset.price);
                total += price * item.quantity;
                const input = row.querySelector('input[type="number"]');
                if (input) input.value = item.quantity;
            }
        });

        this.cartTotalEl.textContent = `Tạm tính: ${total.toLocaleString()}₫`;

        if (this.cart.length === 0) {
            this.cartContainer.style.display = 'none';
            this.emptyCartMessage.style.display = 'block';
        }

        localStorage.setItem('cart', JSON.stringify(this.cart));
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const cartManager = new CartManager();

    const submitBtn = document.getElementById('submitOrderBtn');

    document.getElementById('checkoutForm').addEventListener('submit', function (e) {
        e.preventDefault();

        // Lấy dữ liệu từ form
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());

        if (!formData.get('full_name') || !formData.get('phone_number') || !formData.get('address')) {
            return;
        }


        bootstrap.Modal.getInstance(document.getElementById('checkoutModal')).hide();
            fetch('/order/submit/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    full_name: formData.get('full_name'),
                    phone_number: formData.get('phone_number'),
                    email: formData.get('email'),
                    address: formData.get('address'),
                    note: formData.get('note'),
                    items: cartManager.cart,
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    showMessageModal('success', data.message, -1).show();
                    localStorage.removeItem('cart');
                    cartManager.init();
                }
            });

    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            // Kiểm tra chuỗi cookie bắt đầu bằng tên cần tìm
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
