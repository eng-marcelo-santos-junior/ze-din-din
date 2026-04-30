/* ============================================================
   Zé Din Din — Main JavaScript
   ============================================================ */

'use strict';

document.addEventListener('DOMContentLoaded', function () {
    initFlashAutoDismiss();
    initSidebarToggle();
    initConfirmDialogs();
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
 * Toggle sidebar collapse for dashboard layout.
 */
function initSidebarToggle() {
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar   = document.getElementById('sidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('sidebar-collapsed');
        });
    }
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
