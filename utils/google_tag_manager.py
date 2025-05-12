#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# 2024-04-22: Created GTM injection function for Streamlit app analytics
# 2024-05-15: Fixed script injection logic to prevent duplication and file growth
# 2024-05-15: Updated timeout script to use Deploy button for countdown display
# 2024-05-15: Enhanced script to work in both dev and production environments

1. Cole este código o mais alto possível no <head> da página:
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-MTGRS9GF');</script>
<!-- End Google Tag Manager -->

2. Cole este código imediatamente após a tag de abertura <body>:
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-MTGRS9GF"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->

"""

import pathlib
import logging
import shutil
import streamlit as st
from bs4 import BeautifulSoup

# --- Configure Logging (Optional but good practice) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Define JavaScript Snippets ---

# GTM script for head section - Removed unnecessary escaping in noscript
GTM_JS = """
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-MTGRS9GF');</script>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-MTGRS9GF"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
"""

TIMEOUT_JS = """
<script type="text/javascript">
/* Timeout script - Displays countdown timer */
console.log('🔄 Inactivity Timeout Script loaded');

(function() {
  console.log('⏱️ Initializing timeout functionality');
  let lastActivity = Date.now();
  const INACTIVITY_DELAY = 60 * 1000 * 15; // 15 minutes
  const REDIRECT_URL = "https://creatorsengine.com.br/timeout";
  let countdownInterval = null;
  let countdownElement = null;

  // Try different selectors for buttons in both dev and production
  const POSSIBLE_ELEMENTS = [
    // Dev environment - Deploy button
    '.stAppDeployButton button .st-emotion-cache-1wbqy5l span',
    '.stAppDeployButton button span',
    '[data-testid="stAppDeployButton"] span',
    'button[data-testid="stBaseButton-header"] span',

    // Production environment - Various UI elements
    '[data-testid="stToolbarActions"]',                 // Toolbar actions container
    '.stToolbarActions',                                // Toolbar actions by class
    'header .stAppHeader',                              // Header element
    '[data-testid="stHeader"]',                         // Header by test ID
    '.stToolbar',                                       // Toolbar element
    'button[kind="header"]',                            // Any header button
    '.stMainMenu'                                       // Main menu container
  ];

  // Create our own countdown element if we can't find a suitable target
  function createCountdownElement() {
    console.log('Creating custom countdown element');
    const elem = document.createElement('div');
    elem.id = 'inactivity-countdown';
    elem.style.position = 'fixed';
    elem.style.top = '10px';
    elem.style.right = '10px';
    elem.style.background = 'rgba(255, 245, 230, 0.9)';
    elem.style.color = '#333';
    elem.style.padding = '6px 12px';
    elem.style.borderRadius = '4px';
    elem.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
    elem.style.zIndex = '999999';
    elem.style.fontWeight = 'bold';
    elem.style.fontSize = '14px';
    elem.style.fontFamily = 'sans-serif';
    elem.textContent = 'Initializing...';
    document.body.appendChild(elem);
    return elem;
  }

  // Find or create an element to display the countdown
  function findOrCreateCountdownElement() {
    // First try to find an existing element
    for (const selector of POSSIBLE_ELEMENTS) {
      const element = document.querySelector(selector);
      if (element) {
        console.log('Found element for countdown:', selector);
        // For container elements, create a child span for the countdown
        if (element.tagName !== 'SPAN') {
          // If it's not a span, let's add our own child element
          const span = document.createElement('span');
          span.id = 'timeout-countdown-text';
          span.style.marginLeft = '8px';
          span.style.background = 'rgba(255, 245, 230, 0.9)';
          span.style.padding = '3px 6px';
          span.style.borderRadius = '3px';
          element.appendChild(span);
          return span;
        }
        return element;
      }
    }

    // If no suitable element found, create our own
    if (document.body) {
      return createCountdownElement();
    }

    // If body not ready, wait for it
    return null;
  }

  // Function to find or create an element and update it with the countdown
  function initializeCountdown() {
    console.log('Initializing countdown display');

    // Try to find or create an element immediately
    countdownElement = findOrCreateCountdownElement();
    if (countdownElement) {
      console.log('Countdown element found/created, starting timer');
      startCountdown();
      return;
    }

    console.log('No suitable element found yet, setting up observer');

    // Use MutationObserver to detect when elements are added to the DOM
    const observer = new MutationObserver(function(mutations) {
      if (!countdownElement) {
        countdownElement = findOrCreateCountdownElement();
        if (countdownElement) {
          console.log('Found element via observer, starting countdown');
          observer.disconnect();
          startCountdown();
        }
      }
    });

    // Start observing the document with the configured parameters
    observer.observe(document.documentElement, {
      childList: true,
      subtree: true
    });
  }

  function startCountdown() {
    // Update the countdown immediately
    updateCountdown();

    // Set interval to update countdown regularly
    if (countdownInterval) {
      clearInterval(countdownInterval);
    }

    countdownInterval = setInterval(checkTimeoutAndRedirect, 1000);
    console.log('Countdown interval started');
  }

  function updateCountdown() {
    if (!countdownElement) return;

    let remaining = Math.max(0, INACTIVITY_DELAY - (Date.now() - lastActivity));
    const seconds = Math.ceil(remaining/1000);

    countdownElement.textContent = seconds + 's';
  }

  function checkTimeoutAndRedirect() {
    const inactiveTime = Date.now() - lastActivity;
    const remaining = Math.max(0, INACTIVITY_DELAY - inactiveTime);

    if (inactiveTime >= INACTIVITY_DELAY) {
      console.log('⚠️ Inactivity timeout reached, redirecting to:', REDIRECT_URL);
      if (countdownInterval) clearInterval(countdownInterval);
      window.location.href = REDIRECT_URL;
    } else {
      if (remaining % 30000 === 0) { // Log every 30 seconds
        console.log(`Still active, ${remaining/1000}s remaining`);
      }
      updateCountdown();
    }
  }

  function resetActivityTimer() {
    lastActivity = Date.now();
  }

  // Add listeners for user activity
  ['mousemove', 'keypress', 'scroll', 'click', 'touchstart'].forEach(evt => {
    document.addEventListener(evt, resetActivityTimer, { passive: true });
  });

  // Start the process - both on DOM ready and immediately
  document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded, initializing countdown');
    initializeCountdown();
  });

  // Try immediately if DOM is already loaded
  if (document.readyState === 'interactive' || document.readyState === 'complete') {
    console.log('Document already ready, initializing now');
    initializeCountdown();
  }

  // Last resort - try again after a few seconds
  setTimeout(function() {
    console.log('Fallback initialization after timeout');
    if (!countdownElement) {
      initializeCountdown();
    }
  }, 3000);
})();
</script>
"""
# Combined GTM and Timeout script
# GTM_JS_TIMEOUT = GTM_JS + "\n" + TIMEOUT_JS
GTM_JS_TIMEOUT = TIMEOUT_JS + "\n" + GTM_JS

def inject_gtm(mode='both'):
    """
    Injects Google Tag Manager and/or inactivity timeout script into Streamlit's index.html.
    mode: 'gtm' (GTM only), 'timeout' (timeout only), 'both' (default: both scripts)

    Checks if scripts are already present before injecting to prevent duplication.
    """
    GTM_ID = "GTM-MTGRS9GF"
    TIMEOUT_MARKER = "INACTIVITY_DELAY"

    # Get Streamlit's index.html path
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'Checking {index_path}')

    # Read the current content
    content = index_path.read_text()

    # Select which script(s) to inject
    if mode == 'gtm':
        inject_code = GTM_JS
        already_present = GTM_ID in content
    elif mode == 'timeout':
        inject_code = TIMEOUT_JS
        already_present = TIMEOUT_MARKER in content
    else:
        inject_code = GTM_JS_TIMEOUT
        already_present = GTM_ID in content and TIMEOUT_MARKER in content

    # Only inject if scripts are not already present
    if not already_present:
        # Create backup if it doesn't exist
        bck_index = index_path.with_suffix('.bck')
        if not bck_index.exists():
            shutil.copy(index_path, bck_index)
            logging.info(f'Created backup at {bck_index}')

        # Insert script(s) right after the <head> tag
        new_content = content.replace('<head>', f'<head>\n{inject_code}', 1)

        # Write the modified content back to the file
        index_path.write_text(new_content)
        logging.info(f'Script(s) injected successfully with mode: {mode}')
    else:
        logging.info(f'Static Scripts present, skipping injection for mode: {mode}')
