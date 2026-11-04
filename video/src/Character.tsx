import React from "react";

/**
 * "Cloud Sage" — an original mascot for Amirullah.
 * Dark messy hair with a top-knot, round glasses, navy haori with an aurora
 * trim, a cyan/violet energy aura and small hexagon "cloud nodes" orbiting.
 *
 * Everything is drawn in a 400×400 viewBox so the same component powers the
 * waving video, the ID-badge portrait and the pointing pose.
 */

export type Pose = "wave" | "point" | "rest";

type Props = {
  pose: Pose;
  /** time in seconds — drives aura flicker, orbit and idle motion */
  t: number;
  /** arm angle offset in degrees (wave) */
  arm?: number;
  /** 0 = open, 1 = closed */
  blink?: number;
  wink?: boolean;
  aura?: number; // 0..1 intensity
  showBg?: boolean;
};

const C = {
  cyan: "#22d3ee",
  violet: "#a78bfa",
  pink: "#f472b6",
  skin: "#f1c7a3",
  skinShade: "#d9a582",
  hair: "#16182a",
  hairHi: "#2c3058",
  coat: "#1d2145",
  coatShade: "#151834",
  shirt: "#eef0fb",
  line: "#0b0c16",
};

const hexPath = (r: number) => {
  const pts = Array.from({ length: 6 }, (_, i) => {
    const a = (Math.PI / 3) * i - Math.PI / 6;
    return `${(r * Math.cos(a)).toFixed(2)} ${(r * Math.sin(a)).toFixed(2)}`;
  });
  return `M${pts.join("L")}Z`;
};

/** flame-like aura outline: radius modulated by a few sine waves */
const auraPath = (t: number, cx: number, cy: number, rx: number, ry: number, amp: number, seed: number) => {
  const n = 64;
  const pts: string[] = [];
  for (let i = 0; i <= n; i++) {
    const th = (i / n) * Math.PI * 2;
    const up = Math.max(0, -Math.sin(th)); // flames lick upward
    const wob =
      Math.sin(th * 7 + t * 6 + seed) * 0.5 +
      Math.sin(th * 11 - t * 9 + seed * 2) * 0.3 +
      Math.sin(th * 3 + t * 3) * 0.2;
    const r = 1 + amp * (0.35 + up * 1.1) * (0.6 + 0.4 * wob);
    const x = cx + rx * r * Math.cos(th);
    const y = cy + ry * r * Math.sin(th) - up * up * amp * 70 * (0.7 + 0.3 * Math.sin(t * 8 + th * 5 + seed));
    pts.push(`${x.toFixed(1)} ${y.toFixed(1)}`);
  }
  return `M${pts.join("L")}Z`;
};

const Hand: React.FC<{ point?: boolean }> = ({ point }) => (
  <g>
    {/* palm */}
    <ellipse cx={0} cy={0} rx={17} ry={19} fill={C.skin} stroke={C.line} strokeWidth={2.5} />
    {point ? (
      <>
        {/* index finger pointing along +x */}
        <rect x={8} y={-12} width={34} height={11} rx={5.5} fill={C.skin} stroke={C.line} strokeWidth={2.5} />
        {/* curled fingers */}
        <path d="M6 -1 q12 2 12 8 q0 6 -12 6" fill={C.skin} stroke={C.line} strokeWidth={2.5} />
        <path d="M4 9 q10 2 10 7 q0 5 -10 4" fill={C.skin} stroke={C.line} strokeWidth={2.5} />
        {/* thumb */}
        <path d="M-4 -16 q8 -10 16 -6" fill="none" stroke={C.line} strokeWidth={2.5} strokeLinecap="round" />
      </>
    ) : (
      <>
        {[-12, -4, 4, 12].map((x, i) => (
          <rect
            key={i}
            x={x - 4.5}
            y={-40 + Math.abs(x) * 0.5}
            width={9}
            height={26}
            rx={4.5}
            fill={C.skin}
            stroke={C.line}
            strokeWidth={2.5}
          />
        ))}
        <rect x={-30} y={-12} width={22} height={10} rx={5} fill={C.skin} stroke={C.line} strokeWidth={2.5} transform="rotate(-35 -10 -8)" />
        <ellipse cx={0} cy={0} rx={15} ry={16} fill={C.skin} />
      </>
    )}
  </g>
);

export const Character: React.FC<Props> = ({ pose, t, arm = 0, blink = 0, wink = false, aura = 1, showBg = false }) => {
  const bob = Math.sin(t * 2.4) * 2.5;
  const eyeOpen = 1 - blink;

  // arm geometry (character's left hand = screen right)
  const shoulder = { x: 262, y: 318 };
  const armAngle = pose === "wave" ? -62 + arm : pose === "point" ? -8 + arm : 60;
  const armLen = pose === "point" ? 92 : 88;
  const rad = (armAngle * Math.PI) / 180;
  const hand = { x: shoulder.x + Math.cos(rad) * armLen, y: shoulder.y + Math.sin(rad) * armLen };

  return (
    <svg viewBox="0 0 400 400" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="cs-aura" cx="0.5" cy="0.55" r="0.5">
          <stop offset="0" stopColor={C.violet} stopOpacity={0.55 * aura} />
          <stop offset="0.6" stopColor={C.cyan} stopOpacity={0.25 * aura} />
          <stop offset="1" stopColor={C.cyan} stopOpacity={0} />
        </radialGradient>
        <linearGradient id="cs-flame" x1="0" y1="1" x2="0" y2="0">
          <stop offset="0" stopColor={C.violet} stopOpacity={0.0} />
          <stop offset="0.4" stopColor={C.violet} stopOpacity={0.35 * aura} />
          <stop offset="1" stopColor={C.cyan} stopOpacity={0.55 * aura} />
        </linearGradient>
        <linearGradient id="cs-trim" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor={C.cyan} />
          <stop offset="0.5" stopColor={C.violet} />
          <stop offset="1" stopColor={C.pink} />
        </linearGradient>
        <radialGradient id="cs-iris" cx="0.5" cy="0.4" r="0.6">
          <stop offset="0" stopColor="#e0f7ff" />
          <stop offset="0.35" stopColor={C.cyan} />
          <stop offset="1" stopColor="#5b3fd1" />
        </radialGradient>
        <filter id="cs-blur" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="6" />
        </filter>
        <filter id="cs-glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="2.5" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {showBg ? <rect width={400} height={400} fill="#0d0e16" /> : null}

      {/* ---------- aura ---------- */}
      <ellipse cx={200} cy={250} rx={170} ry={175} fill="url(#cs-aura)" />
      <path d={auraPath(t, 200, 270, 118, 120, 0.42 * aura, 0)} fill="url(#cs-flame)" filter="url(#cs-blur)" />
      <path d={auraPath(t * 1.3, 200, 275, 104, 108, 0.32 * aura, 2)} fill="none" stroke={C.cyan} strokeOpacity={0.55 * aura} strokeWidth={2} filter="url(#cs-glow)" />

      <g transform={`translate(0 ${bob})`}>
        {/* ---------- back hair ---------- */}
        <path
          d="M128 196 C120 140 150 104 200 102 C252 104 282 140 274 198 C262 176 250 170 240 168 L160 168 C150 170 138 178 128 196Z"
          fill={C.hair}
        />

        {/* ---------- torso ---------- */}
        <path d="M100 400 C102 340 140 308 200 306 C260 308 298 340 300 400Z" fill={C.coat} stroke={C.line} strokeWidth={3} />
        {/* shirt V */}
        <path d="M172 310 L200 362 L228 310 C218 306 182 306 172 310Z" fill={C.shirt} stroke={C.line} strokeWidth={2.5} />
        {/* collar trim */}
        <path d="M160 314 L200 392 M240 314 L200 392" stroke="url(#cs-trim)" strokeWidth={9} strokeLinecap="round" />
        <path d="M160 314 L200 392 M240 314 L200 392" stroke={C.line} strokeWidth={1.5} strokeOpacity={0.5} fill="none" />
        {/* chest emblem: small cloud */}
        <g transform="translate(140 352)" filter="url(#cs-glow)">
          <path d="M-12 4 a7 7 0 0 1 3-13 a9 9 0 0 1 17 2 a6 6 0 0 1 4 11z" fill="none" stroke={C.cyan} strokeWidth={2.2} />
        </g>
        {/* shading */}
        <path d="M100 400 C102 352 124 326 156 314 C136 340 128 370 130 400Z" fill={C.coatShade} />

        {/* ---------- neck ---------- */}
        <path d="M184 270 L184 312 C192 318 208 318 216 312 L216 270Z" fill={C.skinShade} stroke={C.line} strokeWidth={2.5} />

        {/* ---------- head ---------- */}
        <path
          d="M142 196 C140 252 168 292 200 292 C232 292 260 252 258 196 C256 150 232 130 200 130 C168 130 144 150 142 196Z"
          fill={C.skin}
          stroke={C.line}
          strokeWidth={3}
        />
        {/* ears */}
        <path d="M144 214 c-14 -6 -16 18 -2 24" fill={C.skin} stroke={C.line} strokeWidth={2.5} />
        <path d="M256 214 c14 -6 16 18 2 24" fill={C.skin} stroke={C.line} strokeWidth={2.5} />

        {/* ---------- eyes ---------- */}
        {[
          { x: 176, w: false },
          { x: 224, w: wink },
        ].map(({ x, w }, i) => {
          const open = w ? 0 : eyeOpen;
          return open < 0.15 ? (
            <path key={i} d={`M${x - 13} 220 q13 ${w ? -9 : 6} 26 0`} fill="none" stroke={C.line} strokeWidth={3.5} strokeLinecap="round" />
          ) : (
            <g key={i} transform={`translate(${x} 220) scale(1 ${open})`}>
              <ellipse cx={0} cy={0} rx={12} ry={14} fill="#fff" stroke={C.line} strokeWidth={2.5} />
              <ellipse cx={0} cy={2} rx={9} ry={11} fill="url(#cs-iris)" />
              <ellipse cx={0} cy={3} rx={3.5} ry={5} fill="#1b1145" />
              <circle cx={-4} cy={-4} r={3.2} fill="#fff" />
              <circle cx={4} cy={6} r={1.4} fill="#fff" opacity={0.8} />
              <path d="M-13 -11 q13 -9 26 0" fill="none" stroke={C.line} strokeWidth={4} strokeLinecap="round" />
            </g>
          );
        })}
        {/* brows */}
        <path d="M160 196 q16 -9 30 -2" fill="none" stroke={C.hair} strokeWidth={4.5} strokeLinecap="round" />
        <path d="M210 194 q14 -7 30 2" fill="none" stroke={C.hair} strokeWidth={4.5} strokeLinecap="round" />

        {/* glasses */}
        <g fill="none" stroke="#2b2f52" strokeWidth={3}>
          <circle cx={176} cy={222} r={20} />
          <circle cx={224} cy={222} r={20} />
          <path d="M196 220 q4 -4 8 0" />
          <path d="M156 216 L144 212 M244 216 L256 212" />
        </g>
        <path d="M164 210 l8 -6" stroke="#fff" strokeOpacity={0.6} strokeWidth={2.5} strokeLinecap="round" />
        <path d="M212 210 l8 -6" stroke="#fff" strokeOpacity={0.6} strokeWidth={2.5} strokeLinecap="round" />

        {/* nose + blush + mouth */}
        <path d="M200 236 q3 6 -1 9" fill="none" stroke={C.skinShade} strokeWidth={2.5} strokeLinecap="round" />
        <ellipse cx={162} cy={250} rx={9} ry={4.5} fill={C.pink} opacity={0.35} />
        <ellipse cx={238} cy={250} rx={9} ry={4.5} fill={C.pink} opacity={0.35} />
        <path d="M184 258 q16 16 32 0 q-16 6 -32 0Z" fill="#7a2944" stroke={C.line} strokeWidth={2.5} strokeLinejoin="round" />
        <path d="M190 262 q10 5 20 0" fill="none" stroke="#fff" strokeWidth={2.5} strokeLinecap="round" />

        {/* forehead mark: tiny glowing hexagon */}
        <g transform="translate(200 168)" filter="url(#cs-glow)">
          <path d={hexPath(5.5)} fill="none" stroke={C.cyan} strokeWidth={2} opacity={0.6 + 0.4 * aura} />
        </g>

        {/* ---------- front hair ---------- */}
        <path
          d="M138 200 C130 150 158 112 200 110 C246 110 274 146 264 202
             L252 172 L244 192 L232 160 L220 182 L206 150 L194 178 L180 152 L170 184 L160 162 L152 196 Z"
          fill={C.hair}
          stroke={C.line}
          strokeWidth={3}
          strokeLinejoin="round"
        />
        <path d="M168 128 C184 116 214 114 232 124" fill="none" stroke={C.hairHi} strokeWidth={5} strokeLinecap="round" />
        {/* top-knot with aurora tie */}
        <path d="M184 112 C176 86 196 70 210 78 C226 86 220 108 214 112Z" fill={C.hair} stroke={C.line} strokeWidth={3} />
        <rect x={186} y={104} width={30} height={10} rx={5} fill="url(#cs-trim)" stroke={C.line} strokeWidth={2} />

        {/* ---------- arm ---------- */}
        <g>
          <line
            x1={shoulder.x}
            y1={shoulder.y}
            x2={hand.x}
            y2={hand.y}
            stroke={C.line}
            strokeWidth={33}
            strokeLinecap="round"
          />
          <line x1={shoulder.x} y1={shoulder.y} x2={hand.x} y2={hand.y} stroke={C.coat} strokeWidth={27} strokeLinecap="round" />
          {/* sleeve cuff */}
          <line
            x1={shoulder.x + (hand.x - shoulder.x) * 0.78}
            y1={shoulder.y + (hand.y - shoulder.y) * 0.78}
            x2={shoulder.x + (hand.x - shoulder.x) * 0.86}
            y2={shoulder.y + (hand.y - shoulder.y) * 0.86}
            stroke="url(#cs-trim)"
            strokeWidth={29}
          />
          <g transform={`translate(${hand.x} ${hand.y}) rotate(${pose === "point" ? armAngle : armAngle + 90})`}>
            <Hand point={pose === "point"} />
          </g>
        </g>
      </g>

      {/* ---------- orbiting hex nodes ---------- */}
      {[0, 1, 2, 3].map((i) => {
        const a = t * 1.6 + (i * Math.PI) / 2;
        const x = 200 + Math.cos(a) * 165;
        const y = 318 + Math.sin(a) * 34;
        const front = Math.sin(a) > 0;
        const col = [C.cyan, C.violet, C.pink, C.cyan][i];
        return (
          <g key={i} transform={`translate(${x} ${y})`} opacity={(front ? 1 : 0.45) * aura} filter="url(#cs-glow)">
            <path d={hexPath(front ? 9 : 6.5)} fill={col} fillOpacity={0.25} stroke={col} strokeWidth={2} />
          </g>
        );
      })}
    </svg>
  );
};
