import { useState } from "react";
import { Link } from "react-router-dom";
import { useUser } from "../theme/ProfileContext";
import type { SignProfile } from "../data/types";
import { zodiacGlyph, horoscopeGlyph } from "../lib/user";
import { Chips, Meter, ListCard } from "../components/ui";
import PersonHero from "../components/PersonHero";

type Tab = "signs" | "mascot" | "story";

const TABS: { id: Tab; label: string }[] = [
  { id: "signs", label: "Signs" },
  { id: "mascot", label: "Mascot" },
  { id: "story", label: "Story" },
];

function SignBlock({
  title,
  glyph,
  sign,
  data,
}: {
  title: string;
  glyph: string;
  sign: string;
  data: SignProfile;
}) {
  return (
    <div className="card sign-block">
      <div className="row between" style={{ marginBottom: 6 }}>
        <div>
          <p className="eyebrow">{title}</p>
          <h3 className="display h-lg">
            <span className="sign-glyph">{glyph}</span> {sign}
            {data.element ? (
              <span className="muted" style={{ fontSize: 16 }}>
                {" "}
                · {data.element}
              </span>
            ) : null}
          </h3>
        </div>
      </div>
      <Chips items={data.personality_traits} />

      <p className="block-sub">Core values</p>
      <Chips items={data.values} solid />

      <p className="block-sub">Strengths</p>
      <ul className="trait-list">
        {data.strengths.map((s) => (
          <li key={s}>{s}</li>
        ))}
      </ul>

      <p className="block-sub">Growth edges</p>
      <ul className="trait-list">
        {data.weaknesses.map((s) => (
          <li key={s}>{s}</li>
        ))}
      </ul>

      <p className="block-sub">Rules to live by</p>
      <ul className="trait-list quote">
        {data.rules_to_live.map((s) => (
          <li key={s}>{s}</li>
        ))}
      </ul>
    </div>
  );
}

export default function Profile() {
  const user = useUser();
  const [tab, setTab] = useState<Tab>("signs");
  const { zodiac, horoscope } = user.character_profile;
  const rep = user.representation_profile;
  const sym = rep.symbolism;
  const vis = rep.visual_identity;
  const nar = rep.narrative_context;
  const per = rep.personality_profile;

  return (
    <div className="page-enter">
      <header className="topbar">
        <h1 className="display h-lg">My Character</h1>
        <Link to="/profile/edit" className="btn btn-ghost back">
          {"\u270E"} Edit
        </Link>
      </header>

      <PersonHero user={user} subtitle={user.bio} />

      <div className="tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={tab === t.id ? "tab active" : "tab"}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "signs" && (
        <div className="stack">
          <div className="card">
            <div className="section-label" style={{ margin: "0 0 6px" }}>
              {"\u263F"} Inner compass
            </div>
            <Meter
              leftLabel="Thinking"
              rightLabel="Feeling"
              value={per.thinking_feeling.scale}
            />
            <Meter
              leftLabel="Introvert"
              rightLabel="Extrovert"
              value={per.introversion_extroversion.scale}
            />
            <div className="row" style={{ marginTop: 10, gap: 8 }}>
              <span className="chip">{per.alignment}</span>
              <span className="chip">{per.dominant_emotion}</span>
            </div>
          </div>

          <SignBlock
            title="Chinese Zodiac"
            glyph={zodiacGlyph(zodiac.sign)}
            sign={zodiac.sign}
            data={zodiac}
          />
          <SignBlock
            title="Western Horoscope"
            glyph={horoscopeGlyph(horoscope.sign)}
            sign={horoscope.sign}
            data={horoscope}
          />
        </div>
      )}

      {tab === "mascot" && (
        <div className="stack">
          <div className="card">
            <p className="eyebrow">Archetype</p>
            <h3 className="display h-lg">{sym.archetype}</h3>
            <p className="mono faint" style={{ fontSize: 12, marginTop: 4 }}>
              {"\u266A"} {sym.theme_song}
            </p>
            <p className="muted" style={{ marginTop: 12 }}>
              {user.avatar_description}
            </p>
          </div>

          <div className="card">
            <div className="section-label" style={{ margin: "0 0 12px" }}>
              {"\u25C8"} Palette
            </div>
            <div className="swatches">
              {Object.entries(sym.color_meanings).map(([hex, meaning]) => (
                <div key={hex} className="swatch">
                  <span className="chipcolor" style={{ background: hex }} />
                  <div>
                    <p className="mono swatch-hex">{hex}</p>
                    <p className="faint swatch-meaning">{meaning}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <ListCard title="Carried with them" items={vis.accessories} />

          <div className="card">
            <div className="section-label" style={{ margin: "0 0 10px" }}>
              {"\u2756"} Core elements
            </div>
            <Chips items={sym.core_elements} />
            <p className="block-sub">Totem animals</p>
            <Chips items={sym.totemic_animals} />
            <p className="block-sub">Form variants</p>
            <Chips items={vis.form_variants} />
          </div>
        </div>
      )}

      {tab === "story" && (
        <div className="stack">
          <div className="card story-card">
            <p className="eyebrow">World</p>
            <h3 className="display h-lg">{nar.world.name}</h3>
            <p className="muted">{nar.world.type}</p>
            <p className="mono faint" style={{ fontSize: 12, marginTop: 8 }}>
              {nar.world.time_period}
            </p>
            <p className="block-sub">Terrain</p>
            <Chips items={nar.world.terrain} />
          </div>

          <div className="card">
            <p className="eyebrow">Origin</p>
            <p className="muted story-text">{nar.origin_story}</p>
          </div>

          <div className="card">
            <p className="eyebrow">Current mission</p>
            <p className="muted story-text">{nar.current_mission}</p>
            <div className="story-meta">
              <span className="chip">Ally · {nar.allegiance}</span>
            </div>
            <p className="block-sub">Nemesis</p>
            <p className="muted story-text">{nar.nemesis}</p>
          </div>

          <ListCard title="Quirks" items={per.quirks} />
          <ListCard title="Fears" items={per.fears} />
        </div>
      )}
    </div>
  );
}
