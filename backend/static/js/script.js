function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('-translate-x-full');
}

// Custom UI Design Alerts (Confirm/Delete)
window.uiConfirm = function(title, message, onConfirm) {
    const container = document.getElementById('modal-container');
    container.innerHTML = `
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all animate-scale-in">
            <div class="p-6">
                <div class="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full mb-4">
                    <i class="fas fa-exclamation-triangle text-red-600"></i>
                </div>
                <h3 class="text-lg font-bold text-center text-slate-900">${title}</h3>
                <p class="mt-2 text-sm text-center text-slate-500">${message}</p>
            </div>
            <div class="flex border-t border-slate-100">
                <button onclick="closeModal()" class="flex-1 px-4 py-3 text-sm font-medium text-slate-600 hover:bg-slate-50 border-r border-slate-100 transition-colors">取消</button>
                <button id="confirm-btn" class="flex-1 px-4 py-3 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors">确认删除</button>
            </div>
        </div>
    `;
    container.classList.remove('hidden');
    document.getElementById('confirm-btn').onclick = function() {
        onConfirm();
        closeModal();
    };
};

window.closeModal = function() {
    document.getElementById('modal-container').classList.add('hidden');
};

// Support for smooth transitions and hover effects
document.querySelectorAll('.btn-primary').forEach(btn => {
    btn.classList.add('px-4', 'py-2', 'bg-primary', 'text-white', 'rounded-lg', 'hover:bg-opacity-90', 'transition-all', 'duration-300');
});
