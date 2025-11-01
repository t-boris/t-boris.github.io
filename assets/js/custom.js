/**
 * Custom JavaScript for blog.tsekinovsky.me
 * Modern enhancements and animations
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
    initAOS();
    initReadingProgress();
    initSmoothScroll();
    initSmartNavbar();
    initThemeToggle();
    initCurrentDate();
  }

  /**
   * Initialize AOS (Animate On Scroll)
   */
  function initAOS() {
    if (typeof AOS !== 'undefined') {
      AOS.init({
        duration: 800,
        easing: 'ease-out-cubic',
        once: true,
        offset: 100,
        delay: 50
      });
    }
  }

  /**
   * Reading Progress Bar
   */
  function initReadingProgress() {
    // Create progress bar if it doesn't exist
    let progressBar = document.getElementById('reading-progress-bar');

    if (!progressBar) {
      const progressContainer = document.createElement('div');
      progressContainer.className = 'reading-progress';
      progressContainer.innerHTML = '<div class="reading-progress__bar" id="reading-progress-bar"></div>';

      // Insert at the beginning of body
      document.body.insertBefore(progressContainer, document.body.firstChild);
      progressBar = document.getElementById('reading-progress-bar');
    }

    // Update progress on scroll
    window.addEventListener('scroll', updateProgress);

    function updateProgress() {
      const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (winScroll / height) * 100;
      progressBar.style.width = scrolled + '%';
    }

    // Initial update
    updateProgress();
  }

  /**
   * Smooth Scroll for anchor links
   */
  function initSmoothScroll() {
    // Add smooth scroll CSS
    document.documentElement.style.scrollBehavior = 'smooth';

    // Handle anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');

        // Skip if it's just "#"
        if (href === '#') return;

        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }

  /**
   * Smart Navbar - Hide on scroll down, show on scroll up
   */
  function initSmartNavbar() {
    let lastScroll = 0;
    const navbar = document.getElementById('topbar-wrapper');

    if (!navbar) return;

    window.addEventListener('scroll', () => {
      const currentScroll = window.pageYOffset;

      // Hide navbar on scroll down, show on scroll up
      if (currentScroll > lastScroll && currentScroll > 100) {
        navbar.style.transform = 'translateY(-100%)';
      } else {
        navbar.style.transform = 'translateY(0)';
      }

      // Add shadow when scrolled
      if (currentScroll > 50) {
        navbar.classList.add('navbar--scrolled');
      } else {
        navbar.classList.remove('navbar--scrolled');
      }

      lastScroll = currentScroll;
    });
  }

  /**
   * Enhanced Theme Toggle with animation
   */
  function initThemeToggle() {
    const themeToggle = document.querySelector('[data-toggle-mode]');

    if (!themeToggle) return;

    themeToggle.addEventListener('click', function() {
      // Add a smooth transition effect
      document.documentElement.style.setProperty('--transition-speed', '0.3s');

      setTimeout(() => {
        document.documentElement.style.removeProperty('--transition-speed');
      }, 300);
    });
  }

  /**
   * Display Current Date
   */
  function initCurrentDate() {
    const dateElement = document.getElementById('current-date-text');

    if (!dateElement) return;

    const options = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    };

    const today = new Date();
    const formattedDate = today.toLocaleDateString('en-US', options);

    dateElement.textContent = formattedDate;
  }

  /**
   * Scroll to Top Button (will be added with FAB menu)
   */
  function scrollToTop() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }

  // Expose scroll to top function globally
  window.scrollToTop = scrollToTop;

  /**
   * Enhanced code block features
   */
  function enhanceCodeBlocks() {
    document.querySelectorAll('pre code').forEach(block => {
      // Add copy button if not exists
      if (!block.parentElement.querySelector('.code-copy-btn')) {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'code-copy-btn';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.title = 'Copy code';

        copyBtn.addEventListener('click', () => {
          navigator.clipboard.writeText(block.textContent);
          copyBtn.innerHTML = '<i class="fas fa-check"></i>';
          copyBtn.classList.add('copied');

          setTimeout(() => {
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.classList.remove('copied');
          }, 2000);
        });

        block.parentElement.style.position = 'relative';
        block.parentElement.appendChild(copyBtn);
      }
    });
  }

  // Initialize code block enhancements after a short delay
  setTimeout(enhanceCodeBlocks, 500);

  /**
   * Image lazy loading enhancement
   */
  if ('loading' in HTMLImageElement.prototype) {
    const images = document.querySelectorAll('img[loading="lazy"]');
    images.forEach(img => {
      img.src = img.dataset.src || img.src;
    });
  } else {
    // Fallback for browsers that don't support native lazy loading
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
    document.body.appendChild(script);
  }

  /**
   * Performance: Preload links on hover
   */
  const links = document.querySelectorAll('a[href^="/"]');
  links.forEach(link => {
    link.addEventListener('mouseenter', function() {
      const href = this.getAttribute('href');

      // Create prefetch link
      if (href && !document.querySelector(`link[href="${href}"]`)) {
        const prefetch = document.createElement('link');
        prefetch.rel = 'prefetch';
        prefetch.href = href;
        document.head.appendChild(prefetch);
      }
    });
  });

  console.log('✨ Custom enhancements loaded');

})();

/**
 * Toast Notification System
 */
class Toast {
  constructor() {
    this.container = null;
    this.init();
  }

  init() {
    // Create toast container if it doesn't exist
    if (!document.getElementById('toast-container')) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    } else {
      this.container = document.getElementById('toast-container');
    }
  }

  show(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;

    const icon = this.getIcon(type);

    toast.innerHTML = `
      <div class="toast__icon">
        <i class="fas fa-${icon}"></i>
      </div>
      <div class="toast__content">
        <span class="toast__message">${message}</span>
      </div>
      <button class="toast__close" aria-label="Close">
        <i class="fas fa-times"></i>
      </button>
    `;

    this.container.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(() => {
      toast.classList.add('toast--visible');
    });

    // Close button handler
    const closeBtn = toast.querySelector('.toast__close');
    closeBtn.addEventListener('click', () => {
      this.hide(toast);
    });

    // Auto-hide
    if (duration > 0) {
      setTimeout(() => {
        this.hide(toast);
      }, duration);
    }

    return toast;
  }

  hide(toast) {
    toast.classList.remove('toast--visible');
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, 300);
  }

  getIcon(type) {
    const icons = {
      success: 'check-circle',
      error: 'exclamation-circle',
      warning: 'exclamation-triangle',
      info: 'info-circle'
    };
    return icons[type] || icons.info;
  }

  success(message, duration) {
    return this.show(message, 'success', duration);
  }

  error(message, duration) {
    return this.show(message, 'error', duration);
  }

  warning(message, duration) {
    return this.show(message, 'warning', duration);
  }

  info(message, duration) {
    return this.show(message, 'info', duration);
  }
}

// Create global toast instance
window.toast = new Toast();

// Global helper function
window.showToast = function(message, type = 'info', duration = 3000) {
  return window.toast.show(message, type, duration);
};
