
document.addEventListener("DOMContentLoaded", function () {
    const stars = document.querySelectorAll("#star-select .star-icon");
    const ratingInput = document.getElementById("ratingInput");

    stars.forEach((star, index) => {
        star.addEventListener("click", () => {
            const rating = index + 1;
            ratingInput.value = rating;

            stars.forEach((s, i) => {
                if (i < rating) {
                    s.classList.remove("bi-star");
                    s.classList.add("bi-star-fill");
                } else {
                    s.classList.remove("bi-star-fill");
                    s.classList.add("bi-star");
                }
            });
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const addToCartBtn = document.getElementById('addToCartBtn');
    const variantId = addToCartBtn?.dataset?.variantId;

    // Lấy giỏ hàng từ localStorage
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');

    // Kiểm tra nếu sản phẩm đã có thì disable nút
    if (cart.some(item => item.variant_id == variantId)) {
        addToCartBtn.classList.add('disabled');
        addToCartBtn.innerHTML = '<i class="bi bi-check2-circle"></i> Đã có trong giỏ hàng';
    }

    // Xử lý click để thêm vào giỏ
    addToCartBtn?.addEventListener('click', function (e) {
        e.preventDefault();
        if (this.classList.contains('disabled')) return;

        addToCart(variantId, 1);

        // Cập nhật giao diện
        this.classList.add('disabled');
        this.innerHTML = '<i class="bi bi-check2-circle"></i> Đã có trong giỏ hàng';

    });
});


document.addEventListener('DOMContentLoaded', function () {
    const modalImage = document.getElementById('modalImage');
    document.querySelectorAll('[data-img-url]').forEach(el => {
        el.addEventListener('click', () => {
            modalImage.src = el.getAttribute('data-img-url');
        });
    });

});

function addToCart(variant_id, quantity) {

    let cart = JSON.parse(localStorage.getItem('cart') || '[]');

    if (!cart.some(item => item.variant_id == variant_id)) {


        // Thêm vào giỏ
        cart.push({
            variant_id: variant_id,
            quantity: 1
        });

        localStorage.setItem('cart', JSON.stringify(cart));
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const buyBtn = document.getElementById('buyBtn');

    if (buyBtn) {
        buyBtn.addEventListener('click', function () {
            const variantId = this.dataset.variantId;

            addToCart(variantId, 1);

            // Chuyển đến trang giỏ hàng
            window.location.href = "/cart/";
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const reviewForm = document.getElementById("reviewForm");

    reviewForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = {
            product_id: document.getElementById("productId").value,
            rating: document.getElementById("ratingInput").value,
            name: document.getElementById("name").value.trim(),
            phone: document.getElementById("phone").value.trim(),
            content: document.getElementById("content").value.trim()
        };

        fetch("/review/submit/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(data => {
            if (data.message) {
                showMessageModal('success', data.message, -1).show();
                reviewForm.reset();
                document.getElementById("ratingInput").value = "";
                bootstrap.Modal.getInstance(document.getElementById("reviewModal")).hide();
            } else {
                alert(data.error || "Có lỗi xảy ra.");
            }
        })
        .catch(err => {
            console.error(err);
            alert("Lỗi gửi đánh giá.");
        });
    });

    // CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});