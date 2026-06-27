import { Link } from "react-router-dom";
import { useProfile } from "../theme/ProfileContext";
import { revealsRemaining, revealsResetLabel } from "../lib/user";
import AvatarOrb from "../components/AvatarOrb";
import AlignmentMeter from "../components/AlignmentMeter";

export default function Matches() {
  const { user, matches } = useProfile();
  const remaining = revealsRemaining(user);

  return (
    <div className="page-enter">
      <header className="topbar">
        <h1 className="display h-lg">Matches</h1>
        <span className="chip solid mono">{remaining} reveals</span>
      </header>

      <p className="muted" style={{ margin: "0 4px 6px", fontSize: 14 }}>
        People whose stars align with yours. Spend a reveal to see who's behind
        a locked card.
      </p>
      <p className="mono faint" style={{ margin: "0 4px", fontSize: 12 }}>
        {revealsResetLabel(user)}
      </p>

      <div className="section-label">{"\u2727"} Your constellations</div>

      <div className="stack">
        {matches.map((m) => (
          <Link
            key={m.user.id}
            to={`/matches/${m.user.id}`}
            className={m.revealed ? "card match-row" : "card match-row locked"}
          >
            <div className="match-avatar">
              <AvatarOrb user={m.user} size={66} ring={false} />
              {!m.revealed && (
                <span className="lock" aria-hidden="true">
                  {"\u26AF"}
                </span>
              )}
            </div>
            <div className="grow">
              <h3 className="display h-md">
                {m.revealed ? m.user.first_name : "Hidden traveler"}
              </h3>
              <p className="muted" style={{ fontSize: 13 }}>
                {m.revealed
                  ? m.user.representation_profile.symbolism.archetype
                  : "Reveal to chart this connection"}
              </p>
              <div className="chips" style={{ marginTop: 8 }}>
                {m.shared_values.slice(0, 3).map((v) => (
                  <span key={v} className="chip">
                    {v}
                  </span>
                ))}
              </div>
            </div>
            <AlignmentMeter score={m.score} size={84} />
          </Link>
        ))}
      </div>
    </div>
  );
}
