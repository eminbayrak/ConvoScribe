import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import themesData from './themes.json';

export interface ThemeColors {
    background: {
        primary: string;
        secondary: string;
        tertiary: string;
    };
    text: {
        primary: string;
        secondary: string;
        tertiary: string;
        muted: string;
    };
    border: {
        primary: string;
        secondary: string;
        focus: string;
    };
    button: {
        primary: {
            background: string;
            hover: string;
            text: string;
        };
        secondary: {
            background: string;
            hover: string;
            text: string;
        };
        danger: {
            background: string;
            hover: string;
            text: string;
        };
    };
    sidebar: {
        background: string;
        text: string;
        textMuted: string;
        hover: string;
        active: string;
        border: string;
    };
    chat: {
        userBubble: string;
        botBubble: string;
        userText: string;
        botText: string;
    };
    status: {
        success: string;
        warning: string;
        error: string;
        info: string;
    };
}

export interface Theme {
    name: string;
    colors: ThemeColors;
}

export interface ThemeData {
    light: Theme;
    dark: Theme;
}

// Type assertion for the imported JSON
const themes = themesData as ThemeData;

// Detect system theme preference
function getSystemTheme(): 'light' | 'dark' {
    if (!browser) return 'light';

    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
}

// Get stored theme preference or use system preference
function getInitialTheme(): 'light' | 'dark' {
    if (!browser) return 'light';

    const stored = localStorage.getItem('theme');
    if (stored === 'light' || stored === 'dark') {
        return stored;
    }

    return getSystemTheme();
}

// Create the theme store
export const themeMode = writable<'light' | 'dark'>(getInitialTheme());

// Create derived store for current theme colors
export const currentTheme = derived(themeMode, ($themeMode) => {
    return themes[$themeMode];
});

// Function to toggle theme
export function toggleTheme() {
    themeMode.update(current => {
        const newTheme = current === 'light' ? 'dark' : 'light';
        if (browser) {
            localStorage.setItem('theme', newTheme);
        }
        return newTheme;
    });
}

// Function to set specific theme
export function setTheme(theme: 'light' | 'dark') {
    themeMode.set(theme);
    if (browser) {
        localStorage.setItem('theme', theme);
    }
}

// Listen for system theme changes
if (browser) {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    mediaQuery.addEventListener('change', (e) => {
        // Only update if user hasn't manually set a preference
        const stored = localStorage.getItem('theme');
        if (!stored) {
            themeMode.set(e.matches ? 'dark' : 'light');
        }
    });
}

// Apply theme to document
export function applyTheme(theme: Theme) {
    if (!browser) return;

    const root = document.documentElement;

    // Apply CSS custom properties
    Object.entries(theme.colors).forEach(([category, colors]) => {
        if (typeof colors === 'object') {
            Object.entries(colors).forEach(([key, value]) => {
                if (typeof value === 'string') {
                    root.style.setProperty(`--color-${category}-${key}`, value);
                } else if (typeof value === 'object') {
                    Object.entries(value).forEach(([subKey, subValue]) => {
                        root.style.setProperty(`--color-${category}-${key}-${subKey}`, subValue as string);
                    });
                }
            });
        }
    });

    // Set data attribute for theme-based styling
    root.setAttribute('data-theme', theme.name.toLowerCase().includes('dark') ? 'dark' : 'light');
}

// Export themes for direct access
export { themes };
