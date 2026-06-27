import { useRef, useState } from "react";
import type { DragEvent } from "react";
import { useProfile } from "../theme/ProfileContext";
import { themeSummary } from "../theme/deriveTheme";
import type { ProfileEntry } from "../data/profiles";

export default function ProfileSwitcher() {
  const { bundled, uploaded, activeId, selectProfile, loadFromJson } =
    useProfile();
  const [open, setOpen] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function ingest(file: File | undefined) {
    setErrors([]);
    if (!file) return;
    let json: unknown;
    try {
      json = JSON.parse(await file.text());
    } catch {
      setErrors([`"${file.name}" is not valid JSON.`]);
      return;
    }
    const result = loadFromJson(json, file.name.replace(/\.json$/i, ""));
    if (!result.ok) {
      setErrors(result.errors);
      return;
    }
    setOpen(false);
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    setDragOver(false);
    void ingest(e.dataTransfer.files?.[0]);
  }

  function ProfileButton({ entry }: { entry: ProfileEntry }) {
    const palette =
      entry.user.representation_profile.visual_identity.color_palette ?? [];
    const active = entry.id === activeId;
    return (
      <button
        className={active ? "switch-row active" : "switch-row"}
        onClick={() => {
          selectProfile(entry.id);
          setOpen(false);
        }}
      >
        <span className="switch-swatches" aria-hidden="true">
          {palette.slice(0, 5).map((c, i) => (
            <span key={i} style={{ background: c }} />
          ))}
        </span>
        <span className="grow">
          <span className="switch-name">{entry.label}</span>
          <span className="switch-sub mono">{themeSummary(entry.user)}</span>
        </span>
        {active ? <span className="switch-check">{"\u2713"}</span> : null}
      </button>
    );
  }

  return (
    <>
      <button
        className="switch-fab"
        onClick={() => setOpen(true)}
        aria-label="Switch profile and theme"
      >
        {"\u25C9"}
      </button>

      {open ? (
        <div className="switch-overlay" onClick={() => setOpen(false)}>
          <div
            className="switch-sheet"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-label="Profiles"
          >
            <div className="row between">
              <h2 className="display h-md">Profiles & themes</h2>
              <button
                className="btn btn-ghost back"
                onClick={() => setOpen(false)}
              >
                {"\u2715"}
              </button>
            </div>
            <p className="faint" style={{ fontSize: 13, marginTop: 4 }}>
              Each profile re-themes the whole app from its own data.
            </p>

            <div className="section-label" style={{ margin: "16px 0 10px" }}>
              {"\u2727"} Bundled
            </div>
            <div className="switch-list">
              {bundled.map((entry) => (
                <ProfileButton key={entry.id} entry={entry} />
              ))}
            </div>

            {uploaded.length > 0 ? (
              <>
                <div className="section-label" style={{ margin: "16px 0 10px" }}>
                  {"\u2191"} Uploaded
                </div>
                <div className="switch-list">
                  {uploaded.map((entry) => (
                    <ProfileButton key={entry.id} entry={entry} />
                  ))}
                </div>
              </>
            ) : null}

            <div className="section-label" style={{ margin: "16px 0 10px" }}>
              {"\u2191"} Load your own
            </div>
            <div
              className={dragOver ? "dropzone over" : "dropzone"}
              onClick={() => inputRef.current?.click()}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={onDrop}
            >
              <p className="display h-md">Drop a profile .json</p>
              <p className="faint" style={{ fontSize: 13 }}>
                or tap to choose a file. It is validated against the schema.
              </p>
              <input
                ref={inputRef}
                type="file"
                accept="application/json,.json"
                hidden
                onChange={(e) => void ingest(e.target.files?.[0])}
              />
            </div>

            {errors.length > 0 ? (
              <div className="switch-errors">
                <p className="switch-err-title">Could not load this file</p>
                <ul>
                  {errors.map((err, i) => (
                    <li key={i} className="mono">
                      {err}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        </div>
      ) : null}
    </>
  );
}
