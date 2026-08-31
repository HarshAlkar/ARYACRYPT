/**
 * In-memory access token store (H8).
 * Refresh tokens live in HttpOnly cookies set by the API — never localStorage.
 */

let accessToken: string | null = null;

const SESSION_FLAG = 'aryacrypt_has_session';

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string | null): void {
  accessToken = token;
  if (token) {
    sessionStorage.setItem(SESSION_FLAG, '1');
  } else {
    sessionStorage.removeItem(SESSION_FLAG);
  }
}

export function clearAccessToken(): void {
  accessToken = null;
  sessionStorage.removeItem(SESSION_FLAG);
}

/** True if this tab previously established a session (cookie may still be valid). */
export function hadSession(): boolean {
  return sessionStorage.getItem(SESSION_FLAG) === '1';
}
