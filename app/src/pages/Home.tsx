import { Link } from "react-router-dom";
import { useProfile } from "../theme/ProfileContext";
import {
  revealsRemaining,
  revealsResetLabel,
  primaryAccent,
} from "../lib/user";
import AvatarOrb from "../components/AvatarOrb";
import AlignmentMeter from "../components/AlignmentMeter";

export default function Home() {
  const { user, matches } = useProfile();
  const remaining = revealsRemaining(user);
  const accent = primaryAccent(user);
  const topMatch = matches[0];
  const archetype = user.representation_profile.symbolism.archetype;
  const themeSong = user.representation_profile.symbolism.theme_song;

  return (
    <div className="page-enter">
      <header className="topbar">
        <div className="wordmark">
          <span className="spark">{"\u2727"}</span> Astrana
        </div>
        <span className="eyebrow">@{user.username}</span>
      </header>

      <section className="home-hero">
        <div className="grow">
          <p className="eyebrow">Good evening</p>
          <h1 className="display h-xl">{user.first_name}.</h1>
          <p className="muted archetype">{archetype}</p>
        </div>
        <AvatarOrb user={user} size={92} />
      </section>

      <section className="card daily-card">
        <div className="section-label" style={{ margin: "0 0 10px" }}>
          {"\u2600"} Daily inspiration
        </div>
        {user.daily_inspiration ? (
          <p className="daily-text">{user.daily_inspiration}</p>
        ) : (
          <p className="daily-text faint">
            The sky is quiet today. Your next inspiration is still being
            charted — check back after your stars realign.
          </p>
        )}
        <p className="mono faint" style={{ marginTop: 12, fontSize: 12 }}>
          {"\u266A"} {themeSong}
        </p>
      </section>

      <section className="card reveals-card" style={{ ["--accent" as string]: accent }}>
        <div className="row between">
          <div>
            <p className="reveals-count display">{remaining}</p>
            <p className="muted">reveals left today</p>
          </div>
          <div className="reveals-orbit" aria-hidden="true">
            {Array.from({ length: 5 }, (_, i) => (
              <span
                key={i}
                className={i < remaining ? "pip on" : "pip"}
              />
            ))}
          </div>
        </div>
        <p className="mono faint" style={{ fontSize: 12, marginTop: 10 }}>
          {revealsResetLabel(user)}
          {user.bonus_reveals > 0 ? ` · +${user.bonus_reveals} bonus` : ""}
        </p>
        <Link to="/matches" className="btn btn-primary btn-block" style={{ marginTop: 14 }}>
          Find who aligns {"\u2192"}
        </Link>
      </section>

      <div className="section-label">{"\u269D"} Closest alignment</div>
      <Link to={`/matches/${topMatch.user.id}`} className="card top-match">
        <AvatarOrb user={topMatch.user} size={64} ring={false} />
        <div className="grow">
          <h3 className="display h-md">{topMatch.user.first_name}</h3>
          <p className="muted" style={{ fontSize: 13 }}>
            {topMatch.user.representation_profile.symbolism.archetype}
          </p>
        </div>
        <AlignmentMeter score={topMatch.score} size={96} />
      </Link>
    </div>
  );
}
