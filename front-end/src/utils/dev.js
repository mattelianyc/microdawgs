export const enableDevTools = () => {
    if (import.meta.env.DEV) {
        // Enable React DevTools
        window.__REACT_DEVTOOLS_GLOBAL_HOOK__ = true;
        
        // Add development helpers
        window.dev = {
            api: () => import('./services/api').then(m => m.default),
            clearStorage: () => localStorage.clear(),
            getToken: () => localStorage.getItem('auth_token'),
        };
    }
}; 