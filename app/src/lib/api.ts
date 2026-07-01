import type { ApiResponse, Match, User } from "../data/types";
import { validateUserResponse } from "../data/validate";

const API_URL = (import.meta.env.VITE_API_URL as string | undefined)?.replace(
  /\/$/,
  "",
);

export const isApiMode = Boolean(API_URL);

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  if (!API_URL) {
    throw new Error("VITE_API_URL is not configured");
  }
  const res = await fetch(`${API_URL}${path}`, options);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || res.statusText);
  }
  return res.json() as Promise<T>;
}

export interface UserSummary {
  id: string;
  user_id: number;
  label: string;
}

export async function fetchUserSummaries(): Promise<UserSummary[]> {
  const res = await request<ApiResponse<UserSummary[]>>("/users");
  return res.data;
}

export async function fetchUser(userId: number): Promise<User> {
  const json = await request<ApiResponse<User>>(`/users/${userId}`);
  const result = validateUserResponse(json);
  if (!result.ok || !result.user) {
    throw new Error(result.errors.join(", "));
  }
  return result.user;
}

export async function fetchMatches(userId: number): Promise<Match[]> {
  const res = await request<ApiResponse<Match[]>>(`/users/${userId}/matches`);
  return res.data;
}

export async function importUser(json: unknown): Promise<User> {
  const res = await request<ApiResponse<User>>("/users/import", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ json }),
  });
  const result = validateUserResponse(res);
  if (!result.ok || !result.user) {
    throw new Error(result.errors.join(", "));
  }
  return result.user;
}

export async function generateAvatar(userId: number): Promise<User> {
  const res = await request<ApiResponse<User>>(
    `/users/${userId}/avatar/generate`,
    { method: "POST" },
  );
  const result = validateUserResponse(res);
  if (!result.ok || !result.user) {
    throw new Error(result.errors.join(", "));
  }
  return result.user;
}

export async function generateTheme(userId: number, user: User): Promise<void> {
  await request<ApiResponse<unknown>>(`/users/${userId}/ui/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ json: user }),
  });
}
