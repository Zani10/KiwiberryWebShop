/*
Client-side search functionality for Kiwiberry Orchard
Provides dynamic filtering of product cards based on search input
*/

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const searchInput = document.getElementById('searchInput');
    const productsContainer = document.getElementById('productsContainer');
    const productCards = document.querySelectorAll('.product-card');

    // Debounce function to limit search frequency
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Main search function
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();

        if (!searchTerm) {
            // Show all products if search is empty
            showAllProducts();
            return;
        }

        let visibleCount = 0;

        productCards.forEach(card => {
            const productName = card.getAttribute('data-name');
            const productCultivar = card.getAttribute('data-cultivar');

            // Check if search term matches product name or cultivar
            const matchesName = productName.includes(searchTerm);
            const matchesCultivar = productCultivar.includes(searchTerm);

            if (matchesName || matchesCultivar) {
                card.style.display = 'block';
                card.classList.remove('hidden');
                visibleCount++;
            } else {
                card.style.display = 'none';
                card.classList.add('hidden');
            }
        });

        // Show "no results" message if no products match
        updateNoResultsMessage(visibleCount === 0);
    }

    // Show all products
    function showAllProducts() {
        productCards.forEach(card => {
            card.style.display = 'block';
            card.classList.remove('hidden');
        });
        updateNoResultsMessage(false);
    }

    // Update no results message visibility
    function updateNoResultsMessage(show) {
        let noResultsMsg = document.querySelector('.alert-info');

        if (show && !noResultsMsg) {
            // Create no results message if it doesn't exist
            noResultsMsg = document.createElement('div');
            noResultsMsg.className = 'alert alert-info text-center';
            noResultsMsg.innerHTML = '<i class="bi bi-info-circle"></i> No products found matching your search.';
            productsContainer.appendChild(noResultsMsg);
        } else if (!show && noResultsMsg) {
            // Remove no results message if it exists
            noResultsMsg.remove();
        }
    }

    // Add search event listener with debounce
    if (searchInput) {
        searchInput.addEventListener('input', debounce(performSearch, 300));

        // Clear search when escape is pressed
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                showAllProducts();
                this.blur();
            }
        });

        // Focus search input when '/' is pressed (common search shortcut)
        document.addEventListener('keydown', function(e) {
            if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }

    // Initialize by showing all products
    showAllProducts();

    // Add loading state management for future enhancements
    function setLoadingState(loading) {
        if (loading) {
            productsContainer.classList.add('loading');
        } else {
            productsContainer.classList.remove('loading');
        }
    }

    // Expose functions for potential future use
    window.KiwiberrySearch = {
        performSearch,
        showAllProducts,
        setLoadingState
    };
});
