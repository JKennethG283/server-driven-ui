import type { User } from "../data/types";
import { isAvatarReady, primaryAccent } from "../lib/user";

interface Props {
  user: User;
  size?: number;
  ring?: boolean;
}

// Renders the avatar with a celestial halo. Falls back to a "generating"
// state driven by avatar_status (sample.json) when the image isn't ready.
export default function AvatarOrb({ user, size = 96, ring = true }: Props) {
  const ready = isAvatarReady(user);
  const accent = primaryAccent(user);

  return (
    <div
      className={ring ? "avatar-orb ring" : "avatar-orb"}
      style={{
        width: size,
        height: size,
        ["--accent" as string]: accent,
      }}
    >
      {ready ? (
        <img src={user.avatar_picture} alt={user.avatar_description} />
      ) : (
        <div className="avatar-generating" role="status">
          <span className="spinner" />
          <span className="mono">conjuring…</span>
        </div>
      )}
    </div>
  );
}
