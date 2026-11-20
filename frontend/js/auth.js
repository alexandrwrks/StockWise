let accessToken = null;
let refreshToken = null;
let refreshing = null;

export class ApiError extends Error {
    constructor(status, detail) {
        const message = Array.isArray(detail)
            ? detail.map(({ loc, msg }) => `${loc.slice(1).join(".")}: ${msg}`).join(" · ")
            : detail;
        super(typeof message === "string" ? message : `Ошибка API (${status})`);
        this.status = status;
    }
}

async function request(path, { method = "GET", query, body, token } = {}) {
    const { hostname, port, origin } = window.location;
    const apiOrigin = port === "63342" && ["localhost", "127.0.0.1", "[::1]"].includes(hostname)
        ? `http://${hostname}:8000`
        : origin;
    const url = new URL(path, apiOrigin);
    for (const [name, value] of Object.entries(query ?? {})) {
        if (value !== undefined && value !== null) url.searchParams.set(name, value);
    }

    const headers = new Headers();
    if (token) headers.set("Authorization", `Bearer ${token}`);
    if (body !== undefined) headers.set("Content-Type", "application/json");

    const response = await fetch(url, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
    });

    if (response.status === 204) return;
    const data = await response.json().catch(() => null);
    if (!response.ok) throw new ApiError(response.status, data?.detail);
    return data;
}

export function register(credentials) {
    return request("/auth/register", { method: "POST", query: credentials });
}

function saveTokens(tokens) {
    accessToken = tokens.access_token;
    refreshToken = tokens.refresh_token;
}

export async function login(credentials) {
    saveTokens(await request("/auth/login", { method: "POST", body: credentials }));
}

function refreshSession() {
    if (!refreshing) {
        const refresh = async () => {
            if (!refreshToken) throw new ApiError(401, "Войдите в аккаунт.");
            saveTokens(await request("/auth/refresh", { method: "POST", token: refreshToken }));
        };
        refreshing = refresh().finally(() => { refreshing = null; });
    }
    return refreshing;
}

export async function logout() {
    try {
        if (refreshing) await refreshing;
        if (refreshToken) await request("/auth/logout", { method: "POST", token: refreshToken });
    } catch (error) {
        if (error.status !== 401) throw error;
    }
    accessToken = null;
    refreshToken = null;
}

export async function api(path, options = {}) {
    const originalToken = accessToken;
    try {
        return await request(path, { ...options, token: originalToken });
    } catch (error) {
        if (error.status !== 401) throw error;
    }

    try {
        if (accessToken === originalToken) await refreshSession();
        return await request(path, { ...options, token: accessToken });
    } catch (error) {
        if (error.status === 401) {
            accessToken = null;
            refreshToken = null;
            window.dispatchEvent(new Event("session-expired"));
        }
        throw error;
    }
}
