import { useState } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import AppShell from "./components/AppShell";
import Starfield from "./components/Starfield";
import ProfileSwitcher from "./components/ProfileSwitcher";
import Home from "./pages/Home";
import Matches from "./pages/Matches";
import MatchDetail from "./pages/MatchDetail";
import Profile from "./pages/Profile";
import EditProfile from "./pages/EditProfile";
import { useUser } from "./theme/ProfileContext";

// Route guard (Frontend Pages Plan.md s.4). The onboarding screens themselves
// are out of scope for this build, so the gate stands in for the quiz + goal
// flow and lets you enter the post-onboarding app.
function OnboardingGate({ onEnter }: { onEnter: () => void }) {
  const user = useUser();
  const needsQuiz = !user.has_completed_quiz;
  const needsGoal = !user.has_set_goal;

  return (
    <div className="app-frame">
      <Starfield motes={14} />
      <div className="app-scroll gate">
        <div className="wordmark" style={{ fontSize: 26 }}>
          <span className="spark">{"\u2727"}</span> Astrana
        </div>
        <h1 className="display h-xl" style={{ marginTop: 18 }}>
          Chart your character.
        </h1>
        <p className="muted" style={{ maxWidth: 320 }}>
          Before the sky opens up, finish setting up your profile.
        </p>

        <div className="gate-steps">
          <div className={needsQuiz ? "gate-step" : "gate-step done"}>
            <span className="gate-num mono">01</span>
            <div>
              <p className="display h-md">Personality quiz</p>
              <p className="faint" style={{ fontSize: 13 }}>
                {needsQuiz ? "Not started" : "Complete"}
              </p>
            </div>
          </div>
          <div className={needsGoal ? "gate-step" : "gate-step done"}>
            <span className="gate-num mono">02</span>
            <div>
              <p className="display h-md">Set your goal</p>
              <p className="faint" style={{ fontSize: 13 }}>
                {needsGoal ? "Not started" : "Complete"}
              </p>
            </div>
          </div>
        </div>

        <button className="btn btn-primary btn-block" onClick={onEnter}>
          Enter Astrana {"\u2192"}
        </button>
        <p className="faint center" style={{ fontSize: 12 }}>
          Demo: skips the onboarding flow (out of scope for this build).
        </p>
      </div>
    </div>
  );
}

export default function App() {
  const user = useUser();
  const onboarded = user.has_completed_quiz && user.has_set_goal;
  const [entered, setEntered] = useState(onboarded);
  const location = useLocation();

  return (
    <>
      <ProfileSwitcher />
      {!entered ? (
        <OnboardingGate onEnter={() => setEntered(true)} />
      ) : (
        <AppShell>
          <Routes location={location}>
            <Route path="/" element={<Home />} />
            <Route path="/matches" element={<Matches />} />
            <Route path="/matches/:id" element={<MatchDetail />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/profile/edit" element={<EditProfile />} />
          </Routes>
        </AppShell>
      )}
    </>
  );
}
