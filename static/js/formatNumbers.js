// Selecciona todos los campos con la clase 'numeric-input'
document.querySelectorAll('.numeric-input').forEach(input => {
    input.addEventListener('input', (e) => {
        let value = e.target.value;

        // Elimina cualquier formato existente (puntos o comas)
        value = value.replace(/\./g, '').replace(/,/g, '');

        // Aplica el formato con separadores de miles
        e.target.value = new Intl.NumberFormat('es-ES').format(value);
    });
});
