import type { ApiResponse, User } from "./types";

// Auto-discover every profile in ./profiles/*.json so newly generated files
// (e.g. written by tools/avatar_gen/generate.py --apply-to-app) show up in the
// switcher without editing this registry.
const modules = import.meta.glob<ApiResponse<User>>("./profiles/*.json", {
  eager: true,
  import: "default",
});

export interface ProfileEntry {
  id: string;
  label: string;
  user: User;
}

// Keep the original demo profiles first; anything else follows alphabetically.
const PRIORITY = ["sample", "luna", "marcus", "aria"];

function idFromPath(path: string): string {
  return path.split("/").pop()!.replace(/\.json$/, "");
}

function rank(id: string): number {
  const i = PRIORITY.indexOf(id);
  return i === -1 ? PRIORITY.length : i;
}

export const bundledProfiles: ProfileEntry[] = Object.entries(modules)
  .map(([path, json]) => {
    const id = idFromPath(path);
    const user = json.data;
    return { id, label: user.first_name || id, user };
  })
  .sort((a, b) => rank(a.id) - rank(b.id) || a.label.localeCompare(b.label));

export const defaultProfile: ProfileEntry =
  bundledProfiles.find((p) => p.id === "sample") ?? bundledProfiles[0];
