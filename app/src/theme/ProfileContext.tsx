import {
  createContext,
  useCallback,
  useContext,
  useEffect,
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
import {
  isApiMode,
  fetchUserSummaries,
  fetchUser,
  fetchMatches,
  importUser,
  generateAvatar,
  generateTheme,
} from "../lib/api";
import { deriveTheme } from "./deriveTheme";
import { applyTheme } from "./applyTheme";

const LS_ACTIVE = "astrana.activeId";
const LS_UPLOADED = "astrana.uploaded";
const POLL_MS = 3000;
const AVATAR_POLL_LIMIT = 120;

interface ProfileContextValue {
  user: User;
  matches: Match[];
  activeId: string;
  bundled: ProfileEntry[];
  uploaded: ProfileEntry[];
  loading: boolean;
  apiConnected: boolean;
  selectProfile: (id: string) => void;
  loadFromJson: (json: unknown, label?: string) => ValidateResult;
  regenerateAvatar: () => Promise<void>;
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

function entryFromUser(user: User, label?: string): ProfileEntry {
  return {
    id: String(user.id),
    label: label || user.first_name || String(user.id),
    user,
  };
}

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

export function ProfileProvider({ children }: { children: ReactNode }) {
  const [uploaded, setUploaded] = useState<ProfileEntry[]>(() => readUploaded());
  const [apiProfiles, setApiProfiles] = useState<ProfileEntry[]>([]);
  const [apiMatches, setApiMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(isApiMode);
  const [activeId, setActiveId] = useState<string>(() => {
    try {
      return localStorage.getItem(LS_ACTIVE) ?? defaultProfile.id;
    } catch {
      return defaultProfile.id;
    }
  });

  const bundled = isApiMode ? apiProfiles : bundledProfiles;

  const all = useMemo(
    () => [...bundled, ...uploaded],
    [bundled, uploaded],
  );

  const active = useMemo(
    () => all.find((p) => p.id === activeId) ?? bundled[0] ?? defaultProfile,
    [all, activeId, bundled],
  );

  const user = active.user;
  const staticMatches = useMemo(
    () => (isApiMode ? [] : buildMatches(user)),
    [user],
  );
  const matches = isApiMode ? apiMatches : staticMatches;

  useLayoutEffect(() => {
    applyTheme(deriveTheme(user));
  }, [user]);

  const upsertApiProfile = useCallback((entry: ProfileEntry) => {
    setApiProfiles((prev) => [
      ...prev.filter((p) => p.id !== entry.id),
      entry,
    ]);
  }, []);

  // Bootstrap users from API.
  useEffect(() => {
    if (!isApiMode) return;

    let cancelled = false;
    setLoading(true);

    fetchUserSummaries()
      .then(async (summaries) => {
        const entries: ProfileEntry[] = [];
        for (const summary of summaries) {
          const loaded = await fetchUser(summary.user_id);
          if (cancelled) return;
          entries.push({
            id: summary.id,
            label: summary.label,
            user: loaded,
          });
        }
        if (cancelled) return;
        setApiProfiles(entries);

        try {
          const saved = localStorage.getItem(LS_ACTIVE);
          const pick = entries.find((p) => p.id === saved) ?? entries[0];
          if (pick) setActiveId(pick.id);
        } catch {
          if (entries[0]) setActiveId(entries[0].id);
        }
      })
      .catch((err) => {
        console.error("Failed to load users from API:", err);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Load matches when the active user changes (API mode).
  useEffect(() => {
    if (!isApiMode || !user.id) return;

    let cancelled = false;
    fetchMatches(user.id)
      .then((data) => {
        if (!cancelled) setApiMatches(data);
      })
      .catch((err) => {
        console.error("Failed to load matches:", err);
      });

    return () => {
      cancelled = true;
    };
  }, [user.id]);

  // Poll while avatar generation is in progress.
  useEffect(() => {
    if (!isApiMode || user.avatar_status !== "generating") return;

    const refresh = async () => {
      try {
        const fresh = await fetchUser(user.id);
        upsertApiProfile(entryFromUser(fresh));
      } catch {
        /* ignore transient poll errors */
      }
    };

    const id = window.setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, [user.id, user.avatar_status, upsertApiProfile]);

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
      if (isApiMode) {
        const preview = validateUserResponse(json);
        if (!preview.ok || !preview.user) return preview;

        importUser(json)
          .then((loaded) => {
            const entry = entryFromUser(loaded, label);
            upsertApiProfile(entry);
            selectProfile(entry.id);
          })
          .catch((err) => {
            console.error("API import failed:", err);
          });
        return preview;
      }

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
    [selectProfile, upsertApiProfile],
  );

  const regenerateAvatar = useCallback(async () => {
    if (!isApiMode) return;
    const started = await generateAvatar(user.id);
    upsertApiProfile(entryFromUser(started));

    let fresh = started;
    for (let attempt = 0; attempt < AVATAR_POLL_LIMIT; attempt += 1) {
      if (fresh.avatar_status !== "generating") break;
      await wait(POLL_MS);
      fresh = await fetchUser(user.id);
      upsertApiProfile(entryFromUser(fresh));
    }

    if (fresh.avatar_status !== "completed") return;

    await generateTheme(user.id, fresh);
    const themed = await fetchUser(user.id);
    upsertApiProfile(entryFromUser(themed));
  }, [user.id, upsertApiProfile]);

  const value: ProfileContextValue = {
    user,
    matches,
    activeId: active.id,
    bundled,
    uploaded,
    loading,
    apiConnected: isApiMode,
    selectProfile,
    loadFromJson,
    regenerateAvatar,
  };

  if (loading) {
    return (
      <div className="app-frame">
        <div className="app-scroll gate">
          <p className="display h-md center">Connecting to API…</p>
        </div>
      </div>
    );
  }

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
