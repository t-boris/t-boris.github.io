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
      console.error('❌ No eventsData found');
      showNoEventsMessage('current');
      showNoEventsMessage('upcoming');
      return;
    }

    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const currentList = document.getElementById('current-events-list');
    const upcomingList = document.getElementById('upcoming-events-list');

    console.log('📅 Today:', today);
    console.log('📊 Events data:', window.eventsData);

    let currentCount = 0;
    let upcomingCount = 0;

    // Iterate through all dates in events data
    Object.keys(window.eventsData).forEach(foundDate => {
      const events = window.eventsData[foundDate];

      events.forEach(event => {
        const eventDate = event.event_date;

        // Skip events in the past (older than 1 year for archive purposes)
        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
        const oneYearAgoStr = oneYearAgo.toISOString().split('T')[0];

        if (eventDate < oneYearAgoStr) {
          return; // Skip very old events
        }

        // Show in "Today's Events" if event is happening today
        if (eventDate === today) {
          console.log('✅ Today:', event.title);
          currentList.appendChild(createEventCard(event, true));
          currentCount++;
        }
        // Show in "Upcoming Events" if event is in the future
        else if (eventDate > today) {
          console.log('🔜 Upcoming:', event.title, 'on', eventDate);
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
    const monthSelect = document.getElementById('archive-month');
    const yearSelect = document.getElementById('archive-year');

    if (!datesList || !window.eventsData) return;

    // Get selected month and year
    const selectedMonth = parseInt(monthSelect.value);
    const selectedYear = parseInt(yearSelect.value);

    // Clear current list
    datesList.innerHTML = '';

    // Get all dates from eventsData that match selected month/year
    const matchingDates = Object.keys(window.eventsData)
      .filter(dateStr => {
        const date = new Date(dateStr + 'T00:00:00');
        return date.getMonth() + 1 === selectedMonth && date.getFullYear() === selectedYear;
      })
      .sort()
      .reverse(); // Most recent first

    if (matchingDates.length > 0) {
      if (noArchivesMsg) noArchivesMsg.style.display = 'none';

      matchingDates.forEach(dateStr => {
        const eventCount = window.eventsData[dateStr].length;
        const dateLink = document.createElement('a');
        dateLink.href = `/events/archive/${dateStr}/`;
        dateLink.className = 'archive-date-link';
        dateLink.innerHTML = `
          <i class="far fa-calendar"></i>
          <span>${formatDate(dateStr)} (${eventCount} events)</span>
          <i class="fas fa-chevron-right"></i>
        `;
        datesList.appendChild(dateLink);
      });
    } else {
      if (noArchivesMsg) noArchivesMsg.style.display = 'block';
    }
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
