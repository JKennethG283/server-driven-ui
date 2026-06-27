import { useParams, Link, useNavigate } from "react-router-dom";
import { getMatchById } from "../data/user";
import { useProfile } from "../theme/ProfileContext";
import { Chips, ListCard } from "../components/ui";
import PersonHero from "../components/PersonHero";
import AlignmentMeter from "../components/AlignmentMeter";

export default function MatchDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { matches } = useProfile();
  const match = id ? getMatchById(matches, Number(id)) : undefined;

  if (!match) {
    return (
      <div className="page-enter center" style={{ paddingTop: 80 }}>
        <p className="display h-md">This star has drifted away.</p>
        <Link to="/matches" className="btn" style={{ marginTop: 16 }}>
          Back to matches
        </Link>
      </div>
    );
  }

  const { user, score, shared_values } = match;
  const rel = user.character_profile.horoscope.relationship;

  return (
    <div className="page-enter">
      <header className="topbar">
        <button className="btn btn-ghost back" onClick={() => navigate(-1)}>
          {"\u2190"} Back
        </button>
        <span className="eyebrow">Match</span>
      </header>

      <PersonHero user={user} subtitle={user.bio} />

      <div className="card score-banner">
        <AlignmentMeter score={score} size={130} />
        <div className="grow">
          <p className="eyebrow">Alignment</p>
          <p className="muted" style={{ fontSize: 14 }}>
            You share {shared_values.length} core values with{" "}
            {user.first_name}.
          </p>
          <div className="chips" style={{ marginTop: 10 }}>
            <Chips items={shared_values} solid />
          </div>
        </div>
      </div>

      <div className="section-label">{"\u2661"} In a relationship</div>
      <ListCard title="Brings to a connection" items={rel.strengths} />
      <ListCard title="Watch-outs" items={rel.weaknesses} />

      <div className="section-label">{"\u2727"} Traits</div>
      <div className="card">
        <Chips items={user.character_profile.zodiac.personality_traits} />
      </div>

      <button className="btn btn-primary btn-block" style={{ marginTop: 18 }}>
        Connect on Telegram {"\u2197"}
      </button>
    </div>
  );
}
