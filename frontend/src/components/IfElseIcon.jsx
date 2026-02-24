import React from 'react';

/**
 * If Else branding icon: "01" above "10" with padding so it never clips.
 * Use className for size (e.g. w-5 h-5 text-white) and gradient box around it.
 */
export default function IfElseIcon({ className = 'w-5 h-5', ...props }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 28 28"
      fill="none"
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-hidden="true"
      className={className}
      {...props}
    >
      <text x="14" y="13" textAnchor="middle" fontSize="15" fontWeight="800" fontFamily="ui-monospace, monospace" fill="currentColor">01</text>
      <text x="14" y="26" textAnchor="middle" fontSize="15" fontWeight="800" fontFamily="ui-monospace, monospace" fill="currentColor">10</text>
    </svg>
  );
}
