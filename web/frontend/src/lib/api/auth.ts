import { apiFetch } from "./client";
import type { User } from "@/types";

export interface LoginPayload {
  email: string;
  password: string;
  remember_me?: boolean;
}

export function login(payload: LoginPayload) {
  return apiFetch<{ access_token: string; token_type: string }>("/api/auth/login", { method: "POST", json: payload });
}

export function logout() {
  return apiFetch<{ ok: boolean }>("/api/auth/logout", { method: "POST" });
}

export function me() {
  return apiFetch<User>("/api/auth/me");
}

export function updateProfile(payload: { full_name?: string }) {
  return apiFetch<User>("/api/auth/me", { method: "PATCH", json: payload });
}

export function changePassword(payload: { current_password: string; new_password: string }) {
  return apiFetch<{ ok: boolean }>("/api/auth/me/password", { method: "POST", json: payload });
}

export function requestAccess(payload: { email: string; full_name: string; message?: string }) {
  return apiFetch<{ ok: boolean; message: string }>("/api/auth/request-access", { method: "POST", json: payload });
}
