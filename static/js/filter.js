function filterProducts(min, max, btn) {
    const cards = document.querySelectorAll('.card');
    const buttons = document.querySelectorAll('.fp');
    let count = 0;

    // Toggle button states
    buttons.forEach(b => b.classList.remove('on'));
    btn.classList.add('on');

    // Filter cards using if-else conditions
    cards.forEach(card => {
        const price = parseInt(card.getAttribute('data-price'));
        if (price >= min && price <= max) {
            card.style.display = 'block';
            count++;
        } else {
            card.style.display = 'none';
        }
    });

    // Update count display
    const itemCount = document.getElementById('item-count');
    if (itemCount) {
        itemCount.textContent = count + (count === 1 ? ' item' : ' items');
    }
    
    // Update range label
    const rangeLabel = document.getElementById('range-label');
    if (rangeLabel) {
        if (min === 0 && max > 1000) {
            rangeLabel.textContent = 'All Items';
        } else {
            rangeLabel.textContent = 'Ksh ' + min + ' – ' + max;
        }
    }
}
