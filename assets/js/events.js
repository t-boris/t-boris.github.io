/**
 * Events Page JavaScript
 * Handles filtering, calendar, and interactivity for /events page
 */

(function() {
  'use strict';

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    initCategoryFilters();
    initCalendar();
    updateStats();
  }

  /**
   * Category Filters
   */
  function initCategoryFilters() {
    const eventCards = document.querySelectorAll('.event-card');
    if (!eventCards.length) return;

    // Extract unique categories from events
    const categories = new Set();
    eventCards.forEach(card => {
      const category = card.dataset.category;
      if (category) categories.add(category);
    });

    // Create filter buttons
    const filtersContainer = document.getElementById('category-filters');
    if (!filtersContainer) return;

    categories.forEach(category => {
      const btn = document.createElement('button');
      btn.className = 'filter-btn';
      btn.dataset.category = category;
      btn.innerHTML = `<i class="fas fa-tag"></i> ${capitalizeFirst(category)}`;
      filtersContainer.appendChild(btn);

      btn.addEventListener('click', () => filterByCategory(category));
    });

    // Update category count in stats
    const categoryCount = document.getElementById('total-categories-count');
    if (categoryCount) {
      categoryCount.textContent = categories.size;
    }
  }

  function filterByCategory(category) {
    const eventCards = document.querySelectorAll('.event-card');
    const filterBtns = document.querySelectorAll('.filter-btn');

    // Update active button
    filterBtns.forEach(btn => {
      if (btn.dataset.category === category || (category === 'all' && btn.dataset.category === 'all')) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Filter cards
    eventCards.forEach(card => {
      if (category === 'all' || card.dataset.category === category) {
        card.style.display = '';
        card.classList.add('fade-in');
      } else {
        card.style.display = 'none';
        card.classList.remove('fade-in');
      }
    });
  }

  /**
   * Calendar / Archive
   */
  function initCalendar() {
    // This would need access to the events.json data
    // For now, we'll generate the selectors and populate available dates

    const monthSelect = document.getElementById('archive-month');
    const yearSelect = document.getElementById('archive-year');
    const datesList = document.getElementById('archive-dates-list');

    if (!monthSelect || !yearSelect || !datesList) return;

    // Populate month selector
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];

    months.forEach((month, index) => {
      const option = document.createElement('option');
      option.value = index + 1;
      option.textContent = month;
      monthSelect.appendChild(option);
    });

    // Set current month
    const now = new Date();
    monthSelect.value = now.getMonth() + 1;

    // Populate year selector (current year and previous years)
    const currentYear = now.getFullYear();
    for (let year = currentYear; year >= currentYear - 2; year--) {
      const option = document.createElement('option');
      option.value = year;
      option.textContent = year;
      yearSelect.appendChild(option);
    }

    // Event listeners
    monthSelect.addEventListener('change', updateArchiveDates);
    yearSelect.addEventListener('change', updateArchiveDates);

    // Initial population
    updateArchiveDates();
  }

  function updateArchiveDates() {
    const datesList = document.getElementById('archive-dates-list');
    const noArchivesMsg = document.getElementById('no-archives-message');

    if (!datesList) return;

    // Clear current list
    datesList.innerHTML = '';

    // Get markdown files from _data/events/
    // In a real implementation, this would fetch from events.json
    // For now, we'll show a placeholder

    // Check if there are any markdown files
    const hasArchives = checkForArchives();

    if (hasArchives) {
      if (noArchivesMsg) noArchivesMsg.style.display = 'none';

      // Example: Populate with dates
      // This should be populated from actual data
      populateExampleDates(datesList);
    } else {
      if (noArchivesMsg) noArchivesMsg.style.display = 'block';
    }
  }

  function checkForArchives() {
    // This would check if _data/events/*.md files exist
    // For now, return false as placeholder
    return false;
  }

  function populateExampleDates(container) {
    // This is a placeholder - in real implementation,
    // this would read from events.json and create links to markdown files
    const exampleDates = ['2025-11-01', '2025-10-31', '2025-10-30'];

    exampleDates.forEach(date => {
      const dateLink = document.createElement('a');
      dateLink.href = `/events/archive/${date}/`;
      dateLink.className = 'archive-date-link';
      dateLink.innerHTML = `
        <i class="far fa-calendar"></i>
        <span>${formatDate(date)}</span>
        <i class="fas fa-chevron-right"></i>
      `;
      container.appendChild(dateLink);
    });
  }

  /**
   * Stats Update
   */
  function updateStats() {
    const eventCards = document.querySelectorAll('.event-card');
    const totalCount = document.getElementById('total-events-count');

    if (totalCount) {
      totalCount.textContent = eventCards.length;
    }
  }

  /**
   * Utility Functions
   */
  function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  function formatDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  // Expose functions globally if needed
  window.eventsPage = {
    filterByCategory
  };

  console.log('✨ Events page initialized');

})();
