
function openEdit(id, title, priority, category) {
    document.getElementById("editModal").style.display = "flex";
    document.getElementById("editInput").value = title;
    document.getElementById("editPriority").value = priority;
    document.getElementById("editCategory").value = category;

    const form = document.getElementById("editForm");
    form.action = "/edit/" + id;
}

function closeEdit() {
    document.getElementById("editModal").style.display = "none";
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById("editModal");
    if (event.target == modal) {
        closeEdit();
    }
}

// Filter functionality
document.addEventListener('DOMContentLoaded', function() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const taskCards = document.querySelectorAll('.task-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            
            // Filter tasks
            taskCards.forEach(card => {
                if (filter === 'all') {
                    card.style.display = 'block';
                } else {
                    card.style.display = card.dataset.status === filter ? 'block' : 'none';
                }
            });
        });
    });
});