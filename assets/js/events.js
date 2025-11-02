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
    renderEvents();
    initCategoryFilters();
    initCalendar();
    updateStats();
  }

  /**
   * Render Events from JSON data
   */
  function renderEvents() {
    if (!window.eventsData) {
      showNoEventsMessage('current');
      showNoEventsMessage('upcoming');
      return;
    }

    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const currentList = document.getElementById('current-events-list');
    const upcomingList = document.getElementById('upcoming-events-list');

    let currentCount = 0;
    let upcomingCount = 0;

    // Iterate through all dates in events data
    Object.keys(window.eventsData).forEach(foundDate => {
      const events = window.eventsData[foundDate];

      events.forEach(event => {
        const eventDate = event.event_date;

        // Skip events in the past
        if (eventDate !== 'unknown' && eventDate < today) {
          return; // Skip past events
        }

        // Show in "Today's Events" if event is happening today
        if (eventDate === today) {
          currentList.appendChild(createEventCard(event, true));
          currentCount++;
        }
        // Show in "Upcoming Events" if event is in the future OR unknown date
        else if (eventDate > today || eventDate === 'unknown') {
          upcomingList.appendChild(createEventCard(event, true));
          upcomingCount++;
        }
      });
    });

    if (currentCount === 0) showNoEventsMessage('current');
    if (upcomingCount === 0) showNoEventsMessage('upcoming');
  }

  function createEventCard(event, showDate) {
    const card = document.createElement('article');
    card.className = 'event-card card hover-lift';
    card.dataset.category = event.category.toLowerCase();
    card.dataset.eventDate = event.event_date;

    const categoryIcon = getCategoryIcon(event.category);

    card.innerHTML = `
      <div class="event-card__icon-wrapper">
        <div class="event-card__icon ${event.category.toLowerCase()}">
          <i class="${categoryIcon}"></i>
        </div>
      </div>
      <div class="event-card__content">
        <div class="event-card__header">
          <span class="event-category badge badge-primary">
            <i class="fas fa-tag"></i>
            ${event.category}
          </span>
          ${showDate && event.event_date !== 'unknown' ?
            `<span class="event-date">
              <i class="far fa-calendar"></i>
              ${formatEventDate(event.event_date)}
            </span>` : ''}
        </div>
        <h3 class="event-card__title">
          <a href="${event.link}" target="_blank" rel="noopener noreferrer">
            ${event.title}
          </a>
        </h3>
        <p class="event-card__description">
          ${event.description}
        </p>
        <div class="event-card__footer">
          ${event.tags && event.tags.length > 0 ? `
            <div class="event-tags">
              ${event.tags.slice(0, 3).map(tag => `<span class="event-tag">${tag}</span>`).join('')}
            </div>
          ` : ''}
          <a href="${event.link}" target="_blank" rel="noopener noreferrer" class="event-link-btn" aria-label="Read more">
            <i class="fas fa-external-link-alt"></i>
            Read More
          </a>
        </div>
      </div>
    `;

    return card;
  }

  function getCategoryIcon(category) {
    const icons = {
      'Culture': 'fas fa-theater-masks',
      'Community': 'fas fa-users',
      'News': 'fas fa-newspaper',
      'Food': 'fas fa-utensils',
      'Entertainment': 'fas fa-music',
      'Business': 'fas fa-briefcase',
      'Manufacturing': 'fas fa-industry',
      'Politics': 'fas fa-landmark',
      'Economy': 'fas fa-chart-line'
    };
    return icons[category] || 'fas fa-calendar-alt';
  }

  function showNoEventsMessage(type) {
    const container = type === 'current' ?
      document.getElementById('current-events-list') :
      document.getElementById('upcoming-events-list');

    const icon = type === 'current' ? 'calendar-times' : 'calendar-check';
    const message = type === 'current' ?
      'No events found for today' :
      'No upcoming events at this time';

    container.innerHTML = `
      <div class="no-events-message">
        <i class="fas fa-${icon}"></i>
        <p>${message}</p>
      </div>
    `;
  }

  function formatEventDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  /**
   * Category Filters
   */
  function initCategoryFilters() {
    const eventCards = document.querySelectorAll('.event-card');
    if (!eventCards.length) return;

    // Extract unique categories from events by reading the category badge
    const categories = new Set();
    eventCards.forEach(card => {
      const categoryBadge = card.querySelector('.event-category');
      if (categoryBadge) {
        const categoryText = categoryBadge.textContent.trim();
        categories.add(categoryText);
      }
    });

    // Create filter buttons
    const filtersContainer = document.getElementById('category-filters');
    if (!filtersContainer) return;

    // Add click handler to "All" button
    const allBtn = filtersContainer.querySelector('[data-category="all"]');
    if (allBtn) {
      allBtn.addEventListener('click', () => filterByCategory('all'));
    }

    // Sort categories alphabetically
    const sortedCategories = Array.from(categories).sort();

    sortedCategories.forEach(category => {
      const btn = document.createElement('button');
      btn.className = 'filter-btn';
      btn.dataset.category = category;
      btn.innerHTML = `<i class="fas fa-tag"></i> ${category}`;
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

    // Filter cards by category badge text
    eventCards.forEach(card => {
      const categoryBadge = card.querySelector('.event-category');
      const cardCategory = categoryBadge ? categoryBadge.textContent.trim() : '';

      if (category === 'all' || cardCategory === category) {
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
