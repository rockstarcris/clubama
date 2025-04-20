document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    const themeSwitch = document.getElementById('theme-switch');
    themeSwitch.addEventListener('change', function() {
        if (this.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        }
    });
    
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        themeSwitch.checked = true;
        document.body.classList.add('dark-mode');
    }
    
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            
            filterCards(filter);
        });
    });
    
    const searchInput = document.querySelector('.search-input');
    const searchClear = document.querySelector('.search-clear');
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        searchClear.style.display = searchTerm.length > 0 ? 'flex' : 'none';
        
        filterCardsBySearch(searchTerm);
    });
    
    searchClear.addEventListener('click', function() {
        searchInput.value = '';
        searchInput.dispatchEvent(new Event('input'));
        this.style.display = 'none';
    });
    
    document.querySelectorAll('.dropdown-item[data-sort]').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            document.querySelectorAll('.dropdown-item[data-sort]').forEach(i => i.classList.remove('active'));
            
            this.classList.add('active');
            
            sortCards(this.dataset.sort);
        });
    });
    
    document.querySelectorAll('.revert-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('¿Estás seguro de que deseas revertir este cambio?')) {
                alert('Cambio revertido con éxito');
            }
        });
    });
    
    document.getElementById('scrollToTop').addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    document.querySelector('.reset-btn').addEventListener('click', function() {
        document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
        document.querySelector('.filter-tab[data-filter="all"]').classList.add('active');
        
        document.querySelector('.search-input').value = '';
        document.querySelector('.search-clear').style.display = 'none';
        
        document.querySelectorAll('.activity-card').forEach(card => {
            card.style.display = 'flex';
        });
        
        document.querySelector('.empty-state').style.display = 'none';
    });
    
    function filterCards(filter) {
        const cards = document.querySelectorAll('.activity-card');
        let visibleCount = 0;
        
        cards.forEach(card => {
            if (filter === 'all' || card.dataset.type === filter) {
                card.style.display = 'flex';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        document.querySelector('.empty-state').style.display = visibleCount === 0 ? 'flex' : 'none';
    }
    
    function filterCardsBySearch(term) {
        const cards = document.querySelectorAll('.activity-card');
        let visibleCount = 0;
        
        cards.forEach(card => {
            const content = card.textContent.toLowerCase();
            if (content.includes(term)) {
                card.style.display = 'flex';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        document.querySelector('.empty-state').style.display = visibleCount === 0 ? 'flex' : 'none';
    }
    
    function sortCards(sortBy) {
        const cards = Array.from(document.querySelectorAll('.activity-card'));
        const feed = document.querySelector('.activity-feed');
        
        cards.sort((a, b) => {
            if (sortBy === 'newest') {
                return new Date(b.dataset.date) - new Date(a.dataset.date);
            } else if (sortBy === 'oldest') {
                return new Date(a.dataset.date) - new Date(b.dataset.date);
            } else if (sortBy === 'user-az') {
                return a.dataset.user.localeCompare(b.dataset.user);
            } else if (sortBy === 'user-za') {
                return b.dataset.user.localeCompare(a.dataset.user);
            }
            return 0;
        });
        
        feed.innerHTML = '';
        
        cards.forEach(card => {
            feed.appendChild(card);
        });
    }
});