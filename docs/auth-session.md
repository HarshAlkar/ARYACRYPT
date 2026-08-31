# Auth session model (security H8)

## Browser client

1. **Access token** — kept in process memory only (`tokenStore`). Never written to `localStorage` / `sessionStorage`.
2. **Refresh token** — set by the API as HttpOnly cookie `aryacrypt_refresh` (`path=/api/v1/auth`, `SameSite=Lax`). Not readable by JS.
3. Login/register responses may still include `refresh_token` in JSON for non-browser clients; the SPA ignores it and relies on the cookie + `withCredentials: true`.
4. On full page reload, `ProtectedRoute` calls `POST /auth/refresh` with credentials to mint a new access token from the cookie.
5. Password change increments `token_version` and revokes refresh tokens; the SPA clears memory and redirects to login.
6. Production: set `REFRESH_COOKIE_SECURE=true` and serve the API over HTTPS. Set `VITE_API_BASE_URL` to your API `/api/v1` origin and extend CSP `connect-src` accordingly.

## API clients (curl / mobile)

Pass `refresh_token` in the JSON body to `/auth/refresh` and `/auth/logout` if cookies are unavailable.
