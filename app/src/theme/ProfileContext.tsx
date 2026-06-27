import {
  createContext,
  useCallback,
  useContext,
  useLayoutEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";
import type { User, Match } from "../data/types";
import { bundledProfiles, defaultProfile } from "../data/profiles";
import type { ProfileEntry } from "../data/profiles";
import { buildMatches } from "../data/user";
import { validateUserResponse } from "../data/validate";
import type { ValidateResult } from "../data/validate";
import { deriveTheme } from "./deriveTheme";
import { applyTheme } from "./applyTheme";

const LS_ACTIVE = "astrana.activeId";
const LS_UPLOADED = "astrana.uploaded";

interface ProfileContextValue {
  user: User;
  matches: Match[];
  activeId: string;
  bundled: ProfileEntry[];
  uploaded: ProfileEntry[];
  selectProfile: (id: string) => void;
  loadFromJson: (json: unknown, label?: string) => ValidateResult;
}

const ProfileContext = createContext<ProfileContextValue | null>(null);

function readUploaded(): ProfileEntry[] {
  try {
    const raw = localStorage.getItem(LS_UPLOADED);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as ProfileEntry[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function ProfileProvider({ children }: { children: ReactNode }) {
  const [uploaded, setUploaded] = useState<ProfileEntry[]>(() => readUploaded());
  const [activeId, setActiveId] = useState<string>(() => {
    try {
      return localStorage.getItem(LS_ACTIVE) ?? defaultProfile.id;
    } catch {
      return defaultProfile.id;
    }
  });

  const all = useMemo(
    () => [...bundledProfiles, ...uploaded],
    [uploaded],
  );

  const active = useMemo(
    () => all.find((p) => p.id === activeId) ?? defaultProfile,
    [all, activeId],
  );

  const user = active.user;
  const matches = useMemo(() => buildMatches(user), [user]);

  useLayoutEffect(() => {
    applyTheme(deriveTheme(user));
  }, [user]);

  const selectProfile = useCallback((id: string) => {
    setActiveId(id);
    try {
      localStorage.setItem(LS_ACTIVE, id);
    } catch {
      /* ignore persistence errors */
    }
  }, []);

  const loadFromJson = useCallback(
    (json: unknown, label?: string): ValidateResult => {
      const result = validateUserResponse(json);
      if (!result.ok || !result.user) return result;

      const loadedUser = result.user;
      const id = `upload:${loadedUser.username || loadedUser.id}`;
      const entry: ProfileEntry = {
        id,
        label: label || loadedUser.first_name || "Uploaded",
        user: loadedUser,
      };

      setUploaded((prev) => {
        const next = [...prev.filter((p) => p.id !== id), entry];
        try {
          localStorage.setItem(LS_UPLOADED, JSON.stringify(next));
        } catch {
          /* ignore persistence errors */
        }
        return next;
      });
      selectProfile(id);
      return result;
    },
    [selectProfile],
  );

  const value: ProfileContextValue = {
    user,
    matches,
    activeId: active.id,
    bundled: bundledProfiles,
    uploaded,
    selectProfile,
    loadFromJson,
  };

  return (
    <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>
  );
}

export function useProfile(): ProfileContextValue {
  const ctx = useContext(ProfileContext);
  if (!ctx) {
    throw new Error("useProfile must be used within a ProfileProvider");
  }
  return ctx;
}

export function useUser(): User {
  return useProfile().user;
}
