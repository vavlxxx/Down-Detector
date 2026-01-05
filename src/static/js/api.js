// API Configuration
const API_BASE_URL = '/api/v1';

class API {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw {
                    status: response.status,
                    message: data.detail || 'Произошла ошибка',
                    data,
                };
            }

            return data;
        } catch (error) {
            if (error.status) {
                throw error;
            }
            throw {
                status: 0,
                message: 'Ошибка сети. Проверьте подключение к интернету.',
            };
        }
    }

    // Resources
    async getResources() {
        return this.request('/resources/');
    }

    async getResource(id) {
        return this.request(`/resources/${id}`);
    }

    async createResource(url) {
        return this.request('/resources/', {
            method: 'POST',
            body: JSON.stringify({ url }),
        });
    }

    async deleteResource(id) {
        return this.request(`/resources/${id}`, {
            method: 'DELETE',
        });
    }

    async getResourceStatuses(id) {
        return this.request(`/resources/${id}/statuses`);
    }
}

const api = new API(API_BASE_URL);
