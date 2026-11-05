import axios from "axios";


export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});


api.interceptors.request.use(
    (config) => {
        const token = sessionStorage.getItem(
            "agrofrota_token"
        );

        if (token) {
            config.headers.Authorization =
                `Bearer ${token}`;
        }

        return config;
    }
);

// Ignore responses from an older session after a new login.
api.interceptors.response.use(undefined, (error) => {
    const authorization = error.config?.headers?.Authorization;
    const currentToken = sessionStorage.getItem("agrofrota_token");
    if (error.response?.status === 401 && currentToken &&
        authorization === `Bearer ${currentToken}` &&
        !error.config?.url?.includes("/api/auth/login")) {
        window.dispatchEvent(new Event("agrofrota:session-expired"));
    }
    return Promise.reject(error);
});
