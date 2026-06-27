import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../theme/ProfileContext";

export default function EditProfile() {
  const user = useUser();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    bio: user.bio ?? "",
    gender: user.gender ?? "",
    place_of_birth: user.place_of_birth ?? "",
    current_location: user.current_location ?? "",
    dob: `${user.dob_year}-${String(user.dob_month).padStart(2, "0")}-${String(
      user.dob_day,
    ).padStart(2, "0")}`,
  });
  const [copied, setCopied] = useState(false);

  function update(field: keyof typeof form, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function copyReferral() {
    navigator.clipboard?.writeText(user.referral_code).then(() => {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    });
  }

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    // No backend yet — see Frontend Pages Plan.md s.13. Returns to Profile.
    navigate("/profile");
  }

  return (
    <div className="page-enter">
      <header className="topbar">
        <button
          className="btn btn-ghost back"
          onClick={() => navigate("/profile")}
        >
          {"\u2190"} Back
        </button>
        <span className="eyebrow">Edit profile</span>
      </header>

      <form className="stack" onSubmit={handleSave}>
        <label className="field">
          <span className="field-label">Bio</span>
          <textarea
            className="input"
            rows={2}
            value={form.bio}
            maxLength={140}
            onChange={(e) => update("bio", e.target.value)}
            placeholder="A line about you"
          />
        </label>

        <label className="field">
          <span className="field-label">Gender</span>
          <select
            className="input"
            value={form.gender}
            onChange={(e) => update("gender", e.target.value)}
          >
            <option value="">Prefer not to say</option>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="non-binary">Non-binary</option>
            <option value="other">Other</option>
          </select>
        </label>

        <label className="field">
          <span className="field-label">Date of birth</span>
          <input
            className="input"
            type="date"
            value={form.dob}
            onChange={(e) => update("dob", e.target.value)}
          />
        </label>

        <label className="field">
          <span className="field-label">Place of birth</span>
          <input
            className="input"
            type="text"
            value={form.place_of_birth}
            onChange={(e) => update("place_of_birth", e.target.value)}
            placeholder="City, country"
          />
        </label>

        <label className="field">
          <span className="field-label">Current location</span>
          <input
            className="input"
            type="text"
            value={form.current_location}
            onChange={(e) => update("current_location", e.target.value)}
            placeholder="Where you are now"
          />
        </label>

        <div className="card referral">
          <div className="grow">
            <p className="field-label">Invite code</p>
            <p className="mono referral-code">{user.referral_code}</p>
          </div>
          <button type="button" className="btn" onClick={copyReferral}>
            {copied ? "Copied" : "Share"}
          </button>
        </div>

        <button type="submit" className="btn btn-primary btn-block">
          Save changes
        </button>
      </form>
    </div>
  );
}
