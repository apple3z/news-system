/**
 * Pagination component.
 */
const Pagination = {
    props: {
        currentPage: { type: Number, default: 1 },
        totalPages: { type: Number, default: 1 }
    },
    emits: ['page-change'],
    computed: {
        pages() {
            const start = Math.max(1, this.currentPage - 2);
            const end = Math.min(this.totalPages, this.currentPage + 2);
            const arr = [];
            for (let p = start; p <= end; p++) arr.push(p);
            return arr;
        }
    },
    template: `
    <div class="pagination" v-if="totalPages > 1">
        <button class="page-btn" v-if="currentPage > 1" @click="$emit('page-change', currentPage - 1)">← 上一页</button>
        <button v-for="p in pages" :key="p" class="page-btn" :class="{ active: p === currentPage }" @click="$emit('page-change', p)">{{ p }}</button>
        <button class="page-btn" v-if="currentPage < totalPages" @click="$emit('page-change', currentPage + 1)">下一页 →</button>
    </div>
    `
};
