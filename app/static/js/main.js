/* ============================================================
   Zé Din Din — Main JavaScript
   ============================================================ */

'use strict';

document.addEventListener('DOMContentLoaded', function () {
    initFlashAutoDismiss();
    initSidebarToggle();
    initConfirmDialogs();
    initMoneyMask();
});

/**
 * Auto-dismiss flash messages after 5 seconds.
 */
function initFlashAutoDismiss() {
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(function (el) {
        setTimeout(function () {
            const alert = bootstrap.Alert.getOrCreateInstance(el);
            if (alert) alert.close();
        }, 5000);
    });
}

/**
 * Toggle sidebar: overlay on mobile, hide/show on desktop.
 */
function initSidebarToggle() {
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar   = document.getElementById('sidebar');
    const backdrop  = document.getElementById('sidebarBackdrop');

    if (!toggleBtn || !sidebar) return;

    function isMobile() {
        return window.innerWidth < 992;
    }

    function closeMobileSidebar() {
        sidebar.classList.remove('sidebar-mobile-open');
        if (backdrop) backdrop.classList.remove('show');
    }

    toggleBtn.addEventListener('click', function () {
        if (isMobile()) {
            sidebar.classList.toggle('sidebar-mobile-open');
            if (backdrop) backdrop.classList.toggle('show');
        } else {
            sidebar.classList.toggle('sidebar-collapsed');
        }
    });

    if (backdrop) {
        backdrop.addEventListener('click', closeMobileSidebar);
    }

    window.addEventListener('resize', function () {
        if (!isMobile()) {
            closeMobileSidebar();
        }
    });
}

/**
 * Attach confirmation dialogs to elements with data-confirm attribute.
 */
function initConfirmDialogs() {
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            const message = el.dataset.confirm || 'Tem certeza?';
            if (!confirm(message)) {
                e.preventDefault();
                e.stopImmediatePropagation();
            }
        });
    });
}

/**
 * Format a value in cents to Brazilian currency string.
 * @param {number} cents
 * @returns {string}
 */
function formatMoney(cents) {
    return (cents / 100).toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL',
    });
}

/**
 * Apply pt-BR money mask to inputs with class "money-input" or data-money attribute.
 * Formats as the user types: digits become X.XXX,XX
 */
function initMoneyMask() {
    document.querySelectorAll('input.money-input, input[data-money]').forEach(function (input) {
        input.addEventListener('input', function () {
            var raw = input.value.replace(/\D/g, '');
            if (!raw) { input.value = ''; return; }
            var cents = parseInt(raw, 10);
            var reais = Math.floor(cents / 100);
            var centavos = cents % 100;
            input.value = reais.toLocaleString('pt-BR') + ',' + String(centavos).padStart(2, '0');
        });
        input.addEventListener('focus', function () {
            input.select();
        });
    });
}
