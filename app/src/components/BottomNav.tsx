import { NavLink } from "react-router-dom";

const TABS = [
  { to: "/", label: "Home", icon: "\u2727", end: true },
  { to: "/matches", label: "Matches", icon: "\u269D", end: false },
  { to: "/profile", label: "Character", icon: "\u263D", end: false },
];

export default function BottomNav() {
  return (
    <nav className="bottom-nav" aria-label="Primary">
      {TABS.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          end={tab.end}
          className={({ isActive }) =>
            isActive ? "nav-item active" : "nav-item"
          }
        >
          <span className="ico" aria-hidden="true">
            {tab.icon}
          </span>
          <span>{tab.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
