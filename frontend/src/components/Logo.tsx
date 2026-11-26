import "./Logo.css";

type LogoProps = {
  /** Liggende i menylinjen, stablet på innloggingssiden (UX-DR2). */
  variant: "horizontal" | "stacked";
  className?: string;
};

/**
 * Logo 3c («rund bane») som innebygd SVG, så ordmerket får Manrope.
 * Liggende: mockups/logo-3c.svg. Stablet: innloggingskortet i mockups/key-screens.html.
 */
export function Logo({ variant, className }: LogoProps) {
  const classes = `logo logo--${variant}${className ? ` ${className}` : ""}`;

  if (variant === "horizontal") {
    return (
      <svg
        className={classes}
        width="170"
        height="30"
        viewBox="0 0 340 60"
        role="img"
        aria-label="Red Ball Express"
      >
        <rect
          className="logo__loop"
          x="10"
          y="10"
          width="44"
          height="40"
          rx="20"
          strokeWidth="5"
        />
        <circle
          className="logo__ball"
          cx="47"
          cy="17"
          r="9"
          strokeWidth="2.5"
        />
        <text className="logo__wordmark" x="68" y="38" fontSize="24">
          Red Ball Express
        </text>
      </svg>
    );
  }

  return (
    <svg
      className={classes}
      width="200"
      height="110"
      viewBox="0 0 200 110"
      role="img"
      aria-label="Red Ball Express"
    >
      <g transform="translate(68 0)">
        <rect
          className="logo__loop"
          x="10"
          y="10"
          width="44"
          height="40"
          rx="20"
          strokeWidth="5"
        />
        <circle
          className="logo__ball"
          cx="47"
          cy="17"
          r="9"
          strokeWidth="2.5"
        />
      </g>
      <text
        className="logo__wordmark"
        x="100"
        y="84"
        textAnchor="middle"
        fontSize="22"
      >
        Red Ball Express
      </text>
    </svg>
  );
}
