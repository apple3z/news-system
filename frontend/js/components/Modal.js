/**
 * Modal component - reusable modal overlay.
 */
const Modal = {
    props: {
        show: { type: Boolean, default: false },
        title: { type: String, default: '' }
    },
    emits: ['close'],
    template: `
    <div class="modal-overlay" :class="{ show: show }" @click.self="$emit('close')">
        <div class="modal-content">
            <div class="modal-title">{{ title }}</div>
            <slot></slot>
            <div class="modal-actions">
                <button class="btn" @click="$emit('close')">取消</button>
                <slot name="actions"></slot>
            </div>
        </div>
    </div>
    `
};
