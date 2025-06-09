import axios from "axios";

const API_URL =
    import.meta.env.VUE_APP_API_URL || "/api";

const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

apiClient.interceptors.response.use(
    (response) => response,
    async(error) => {
        const originalRequest = error.config;
        if (
            error.response &&
            error.response.status === 401 &&
            !originalRequest._retry
        ) {
            originalRequest._retry = true;
            const refreshToken = localStorage.getItem("refresh_token");
            if (refreshToken) {
                try {
                    const res = await axios.post(`${API_URL}/token/refresh/`, {
                        refresh: refreshToken,
                    });
                    const newAccess = res.data.access;
                    localStorage.setItem("access_token", newAccess);
                    originalRequest.headers[
                        "Authorization"
                    ] = `Bearer ${newAccess}`;
                    return apiClient(originalRequest);
                } catch (err) {
                    localStorage.removeItem("access_token");
                    localStorage.removeItem("refresh_token");
                    window.location = "/login";
                    return Promise.reject(err);
                }
            }
        }
        return Promise.reject(error);
    }
);

apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
});

export default apiClient;