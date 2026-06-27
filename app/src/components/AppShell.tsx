import type { ReactNode } from "react";
import Starfield from "./Starfield";
import BottomNav from "./BottomNav";

interface Props {
  children: ReactNode;
  showNav?: boolean;
}

export default function AppShell({ children, showNav = true }: Props) {
  return (
    <div className="app-frame">
      <Starfield />
      <div className="app-scroll">{children}</div>
      {showNav ? <BottomNav /> : null}
    </div>
  );
}
