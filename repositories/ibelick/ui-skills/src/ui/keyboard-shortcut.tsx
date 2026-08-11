import { useEffect, useState } from "react";

const shortcutClass =
  "inline-flex h-[18px] select-none items-center gap-0.5 bg-transparent font-mono text-[10px] text-white/60";

function CommandIcon() {
  return (
    <svg
      width="10"
      height="10"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M18 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3H6a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3V6a3 3 0 0 0-3-3 3 3 0 0 0-3 3 3 3 0 0 0 3 3h12a3 3 0 0 0 3-3 3 3 0 0 0-3-3z" />
    </svg>
  );
}

export function CommandKShortcut() {
  const [isMac, setIsMac] = useState(true);

  useEffect(() => {
    setIsMac(/Mac|iPhone|iPad|iPod/i.test(navigator.userAgent));
  }, []);

  return (
    <kbd className={shortcutClass}>
      {isMac ? (
        <>
          <CommandIcon />K
        </>
      ) : (
        <>Ctrl K</>
      )}
    </kbd>
  );
}
