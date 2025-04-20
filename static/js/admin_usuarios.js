document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById('searchInput');
    const roleFilter = document.getElementById('roleFilter');
    const filterButton = document.getElementById('filtrarButton'); 
    const tableRows = document.querySelectorAll('.data-table tbody tr');

    function filterTable() {
        const searchQuery = searchInput.value.toLowerCase();
        const selectedRole = roleFilter.value.toLowerCase();

        tableRows.forEach(row => {
            const username = row.querySelector('.user-name').textContent.toLowerCase();
            const email = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
            const role = row.querySelector('td:nth-child(3) .badge').textContent.toLowerCase();

            const matchesSearch = username.includes(searchQuery) || email.includes(searchQuery);
            const matchesRole = selectedRole === "" || role.includes(selectedRole);

            if (matchesSearch && matchesRole) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    
    searchInput.addEventListener('input', function() {
        filterTable(); 
    });

    
    filterButton.addEventListener('click', function() {
        filterTable(); 
    });

    filterTable(); 
});