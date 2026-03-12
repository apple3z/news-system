/**
 * Centralized API client for all fetch operations.
 */
const API = {
    async _request(url, options) {
        try {
            const res = await fetch(url, options);
            if (!res.ok) {
                console.error(`API error: ${res.status} ${res.statusText} - ${url}`);
                return { code: res.status, message: res.statusText };
            }
            return res.json();
        } catch (e) {
            console.error(`API network error: ${url}`, e);
            return { code: 500, message: '网络请求失败' };
        }
    },
    async get(url) {
        return this._request(url);
    },
    async post(url, data) {
        return this._request(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    },
    async put(url, data) {
        return this._request(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    },
    async del(url) {
        return this._request(url, { method: 'DELETE' });
    }
};
