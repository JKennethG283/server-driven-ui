import type { User } from "../data/types";
import { fullName, age, zodiacGlyph, horoscopeGlyph } from "../lib/user";
import AvatarOrb from "./AvatarOrb";

interface Props {
  user: User;
  subtitle?: string;
}

// Shared identity header for Profile and Match Detail.
export default function PersonHero({ user, subtitle }: Props) {
  const { zodiac, horoscope } = user.character_profile;
  const archetype = user.representation_profile.symbolism.archetype;
  const location = user.current_location;

  return (
    <div className="person-hero card">
      <div className="person-hero-glow" aria-hidden="true" />
      <AvatarOrb user={user} size={108} />
      <div className="grow">
        <h2 className="display h-lg">{fullName(user)}</h2>
        <p className="muted person-meta">
          {age(user)} · @{user.username}
          {location ? ` · ${location}` : ""}
        </p>
        <p className="archetype">{archetype}</p>
        <div className="sign-badges">
          <span className="sign-badge">
            <span className="glyph">{zodiacGlyph(zodiac.sign)}</span>
            {zodiac.sign}
            {zodiac.element ? ` · ${zodiac.element}` : ""}
          </span>
          <span className="sign-badge">
            <span className="glyph">{horoscopeGlyph(horoscope.sign)}</span>
            {horoscope.sign}
          </span>
        </div>
        {subtitle ? <p className="muted">{subtitle}</p> : null}
      </div>
    </div>
  );
}
