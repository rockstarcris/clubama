document.querySelectorAll('.toggle-text').forEach(button => {
    button.addEventListener('click', function() {
        const shortText = this.previousElementSibling.previousElementSibling;
        const fullText = this.previousElementSibling;
        
        if (fullText.classList.contains('d-none')) {
            fullText.classList.remove('d-none');
            shortText.classList.add('d-none');
            this.textContent = "Ver menos";
        } else {
            fullText.classList.add('d-none');
            shortText.classList.remove('d-none');
            this.textContent = "Ver más";
        }
    });
});

function previewAddImage(input) {
    const preview = document.getElementById('preview-add-image');
    const placeholder = document.getElementById('placeholder-add-icon');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
            placeholder.style.display = 'none';
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

function previewEditImage(input, productId) {
    const preview = document.getElementById(`preview-edit-image-${productId}`);
    const placeholder = document.getElementById(`placeholder-edit-icon-${productId}`);
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
            if (placeholder) {
                placeholder.style.display = 'none';
            }
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

document.querySelectorAll('form[action*="delete_product"]').forEach(form => {
    form.addEventListener('submit', function(e) {
        if (!confirm('¿Estás seguro de eliminar este producto?')) {
            e.preventDefault();
        }
    });
});