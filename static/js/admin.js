document.addEventListener('DOMContentLoaded', function() {
    const eventSource = new EventSource("{{ url_for('stream') }}");
    
    eventSource.addEventListener('user_update', function(e) {
        const data = JSON.parse(e.data);
        document.getElementById('userCount').querySelector('.number').textContent = data.total;
        document.getElementById('userChange').querySelector('span').textContent = 
            `${data.today_new} nuevos hoy`;
        
        if (data.new_user) {
            addActivityItem('user', `Nuevo usuario registrado: ${data.new_user}`);
        }
    });

    eventSource.addEventListener('order_update', function(e) {
        const data = JSON.parse(e.data);
        document.getElementById('orderCount').querySelector('.number').textContent = data.total;
        document.getElementById('orderChange').querySelector('span').textContent = 
            `${data.today_new} nuevos hoy`;
        
        if (data.new_order) {
            addActivityItem('order', `Nuevo pedido realizado: #${data.new_order}`);
        }
    });

    eventSource.onerror = function() {
        console.log('SSE connection error');
        eventSource.close();
    };

    function addActivityItem(type, message) {
        const feed = document.getElementById('activityFeed');
        const item = document.createElement('div');
        item.className = 'activity-item';
        
        const icon = type === 'user' ? 'bi-person-plus' : 'bi-bag-plus';
        
        item.innerHTML = `
            <div class="activity-icon">
                <i class="bi ${icon}"></i>
            </div>
            <div class="activity-content">
                <p>${message}</p>
                <span class="activity-time">Ahora</span>
            </div>
        `;
        
        feed.insertBefore(item, feed.firstChild);
        
        if (feed.children.length > 10) {
            feed.removeChild(feed.lastChild);
        }
    }
});