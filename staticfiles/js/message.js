function showMessageModal(type = 'info', content = '', duration = -1, headerText = 'Thông báo', modalID = 'messageModal_' + Date.now()) {
    // Tạo modal container
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = modalID;
    modal.tabIndex = -1;
    modal.setAttribute('aria-hidden', 'true');
    modal.setAttribute('aria-labelledby', 'messageModalLabel');

    // Modal dialog
    const dialog = document.createElement('div');
    dialog.className = 'modal-dialog modal-dialog-centered';
    modal.appendChild(dialog);

    // Modal content
    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content border-0 shadow';
    dialog.appendChild(modalContent);

    // Header
    const header = document.createElement('div');
    header.className = `modal-header ${getTextColorClass(type)}`;
    modalContent.appendChild(header);

    const title = document.createElement('h5');
    title.className = 'modal-title';
    title.id = 'messageModalLabel';

    if (type) {
        const iconClass = getIconClass(type);

        if (iconClass) {
            const icon = document.createElement('i');
            icon.className = iconClass + ' me-2';
            title.appendChild(icon);
        }
    }

    const textNode = document.createTextNode(headerText || '');
    title.appendChild(textNode);

    header.appendChild(title);


    const closeBtn = document.createElement('button');
    closeBtn.className = 'btn-close btn-close-white';
    closeBtn.setAttribute('data-bs-dismiss', 'modal');
    closeBtn.setAttribute('aria-label', 'Đóng');
    header.appendChild(closeBtn);

    // Body
    const body = document.createElement('div');
    body.className = 'modal-body';
    body.innerHTML = content;
    modalContent.appendChild(body);

    // Thêm modal vào DOM
    document.body.appendChild(modal);

    // Hiển thị modal
    const bootstrapModal = new bootstrap.Modal(modal);

    // Tự động ẩn nếu có thời gian
    if (duration !== -1) {
        setTimeout(() => {
            bootstrapModal.hide();
        }, duration);
    }

    return bootstrapModal;

    function getTextColorClass(type) {
        if (!type) {
            return `bg-${type} text-dark`;
        }
        switch (type) {
            case 'light':
            case 'white':
            case 'body':
            case 'transparent':
                return `bg-${type} text-dark`;
            default:
                return `bg-${type} text-white`;
        }
    }

    function getIconClass(type) {
        switch (type) {
            case 'success':
                return 'bi bi-check-circle-fill';
            case 'danger':
                return 'bi bi-x-circle-fill';
            case 'warning':
                return 'bi bi-exclamation-triangle-fill';
            case 'info':
                return 'bi bi-info-circle-fill';
            case 'primary':
                return 'bi bi-info-circle-fill';
            case 'secondary':
                return 'bi bi-shield-fill-check';
            case 'dark':
                return 'bi bi-moon-fill';
            case 'light':
            case 'white':
            case 'body':
            case 'transparent':
                return 'bi bi-circle';
            default:
                return 'bi bi-bell-fill';
        }
    }

}