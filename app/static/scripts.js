// utils/scripts.js

/**
 * Fetches data from an API endpoint
 * @param {string} endpoint - The API endpoint URL or route
 * @param {Object} options - Optional fetch configuration
 * @returns {Promise<any>} A promise that resolves to the parsed response data
 */
async function fetchApiData(endpoint, options = {}) {
    try {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };

        const response = await fetch(endpoint, defaultOptions);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
        }

        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            // Return as text if not JSON
            console.log(`Response content type is not JSON: ${contentType}`);
            return await response.text();
        }
    } catch (error) {
        console.error(`Error fetching data from ${endpoint}:`, error);
        throw error;
    }
}

/**
 * Convenience function for GET requests
 * @param {string} endpoint - The API endpoint URL or route
 * @returns {Promise<any>} A promise that resolves to the parsed response data
 */
async function getApiData(endpoint) {
    return fetchApiData(endpoint);
}

/**
 * Checks if a string is exactly 'application/vnd.google-apps.folder'
 * @param {string} str - The string to check
 * @returns {boolean} True if the string is exactly 'application/vnd.google-apps.folder', false otherwise
 */
function isGoogleDriveFolder(str) {
    // if (typeof str !== 'string') {
    //     return false;
    // }
    return str === 'application/vnd.google-apps.folder';
}

// function markUp()