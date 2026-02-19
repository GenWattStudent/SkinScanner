/**
 * BodySilhouette – inline SVG silhouettes (front & back).
 *
 * Each path is normalised to a 200×500 viewBox so marker coordinates
 * stay in the 0–1 range regardless of the rendered size.
 *
 * Front and back views are clearly differentiated:
 * - Front: face features, navel, chest lines
 * - Back: spine, shoulder blades, hair from behind, "BACK" label
 */

export const BODY_VIEWBOX = { width: 200, height: 500 }

/** Front-facing human silhouette with anatomical cues. */
export const FrontSilhouette = () => (
  <g>
    {/* Main body fill */}
    <g fill="currentColor" opacity={0.10}>
      {/* Head */}
      <ellipse cx="100" cy="38" rx="22" ry="28" />
      {/* Neck */}
      <rect x="92" y="62" width="16" height="16" rx="4" />
      {/* Torso */}
      <path d="M62 78 Q60 130 62 190 Q70 210 100 215 Q130 210 138 190 Q140 130 138 78 Q120 72 100 72 Q80 72 62 78Z" />
      {/* Left arm */}
      <path d="M62 82 Q40 90 28 140 Q24 170 26 200 Q28 210 34 210 Q40 208 42 200 Q48 160 52 140 Q56 120 60 100Z" />
      {/* Right arm */}
      <path d="M138 82 Q160 90 172 140 Q176 170 174 200 Q172 210 166 210 Q160 208 158 200 Q152 160 148 140 Q144 120 140 100Z" />
      {/* Left leg */}
      <path d="M72 210 Q66 280 64 350 Q62 410 60 440 Q58 460 64 470 Q72 475 78 470 Q82 460 82 440 Q84 380 86 320 Q90 260 95 215Z" />
      {/* Right leg */}
      <path d="M128 210 Q134 280 136 350 Q138 410 140 440 Q142 460 136 470 Q128 475 122 470 Q118 460 118 440 Q116 380 114 320 Q110 260 105 215Z" />
    </g>

    {/* Front-specific details */}
    <g stroke="currentColor" fill="none" opacity={0.18} strokeWidth="1">
      {/* Eyes */}
      <ellipse cx="91" cy="34" rx="4" ry="2.5" />
      <ellipse cx="109" cy="34" rx="4" ry="2.5" />
      {/* Nose */}
      <path d="M98 39 Q100 44 102 39" />
      {/* Mouth */}
      <path d="M94 49 Q100 53 106 49" />
      {/* Collarbones */}
      <path d="M72 80 Q86 76 100 78 Q114 76 128 80" strokeWidth="0.8" />
      {/* Chest/pectoral lines */}
      <path d="M76 95 Q82 106 96 104" strokeWidth="0.7" />
      <path d="M124 95 Q118 106 104 104" strokeWidth="0.7" />
      {/* Navel */}
      <circle cx="100" cy="175" r="2.5" />
    </g>

    {/* "FRONT" label */}
    <text
      x="100"
      y="490"
      textAnchor="middle"
      fill="currentColor"
      opacity="0.22"
      fontSize="11"
      fontWeight="600"
      letterSpacing="2"
    >
      FRONT
    </text>
  </g>
)

/** Back-facing human silhouette with anatomical cues. */
export const BackSilhouette = () => (
  <g>
    {/* Main body fill */}
    <g fill="currentColor" opacity={0.10}>
      {/* Head */}
      <ellipse cx="100" cy="38" rx="22" ry="28" />
      {/* Neck */}
      <rect x="92" y="62" width="16" height="16" rx="4" />
      {/* Torso */}
      <path d="M64 78 Q60 130 62 190 Q70 212 100 216 Q130 212 138 190 Q140 130 136 78 Q120 72 100 72 Q80 72 64 78Z" />
      {/* Left arm */}
      <path d="M64 82 Q42 90 30 140 Q26 170 28 200 Q30 210 36 210 Q42 208 44 200 Q50 160 54 140 Q58 120 62 100Z" />
      {/* Right arm */}
      <path d="M136 82 Q158 90 170 140 Q174 170 172 200 Q170 210 164 210 Q158 208 156 200 Q150 160 146 140 Q142 120 138 100Z" />
      {/* Left leg */}
      <path d="M72 212 Q66 280 64 350 Q62 410 60 440 Q58 460 64 470 Q72 475 78 470 Q82 460 82 440 Q84 380 86 320 Q90 260 95 216Z" />
      {/* Right leg */}
      <path d="M128 212 Q134 280 136 350 Q138 410 140 440 Q142 460 136 470 Q128 475 122 470 Q118 460 118 440 Q116 380 114 320 Q110 260 105 216Z" />
    </g>

    {/* Back-specific details */}
    <g stroke="currentColor" fill="none" opacity={0.18} strokeWidth="1">
      {/* Hair (back of head) */}
      <path d="M80 22 Q78 14 82 10 Q92 4 100 3 Q108 4 118 10 Q122 14 120 22" strokeWidth="1.2" />
      <path d="M82 20 Q90 16 100 15 Q110 16 118 20" strokeWidth="0.7" />
      {/* Ears (seen from back) */}
      <path d="M78 32 Q74 36 78 42" strokeWidth="0.8" />
      <path d="M122 32 Q126 36 122 42" strokeWidth="0.8" />
      {/* Spine */}
      <path d="M100 68 L100 200" strokeWidth="1.2" strokeDasharray="3 3" />
      {/* Vertebrae bumps */}
      <circle cx="100" cy="80" r="1.5" fill="currentColor" opacity="0.12" />
      <circle cx="100" cy="95" r="1.5" fill="currentColor" opacity="0.12" />
      <circle cx="100" cy="110" r="1.5" fill="currentColor" opacity="0.12" />
      <circle cx="100" cy="125" r="1.5" fill="currentColor" opacity="0.12" />
      <circle cx="100" cy="140" r="1.5" fill="currentColor" opacity="0.12" />
      <circle cx="100" cy="155" r="1.5" fill="currentColor" opacity="0.12" />
      <circle cx="100" cy="170" r="1.5" fill="currentColor" opacity="0.12" />
      <circle cx="100" cy="185" r="1.5" fill="currentColor" opacity="0.12" />
      {/* Shoulder blades */}
      <path d="M74 92 Q72 105 78 118 Q86 120 90 112 Q88 100 82 90Z" strokeWidth="0.7" />
      <path d="M126 92 Q128 105 122 118 Q114 120 110 112 Q112 100 118 90Z" strokeWidth="0.7" />
      {/* Lower back dimples */}
      <circle cx="92" cy="195" r="2" />
      <circle cx="108" cy="195" r="2" />
      {/* Gluteal fold lines */}
      <path d="M78 218 Q100 225 122 218" strokeWidth="0.6" />
    </g>

    {/* "BACK" label */}
    <text
      x="100"
      y="490"
      textAnchor="middle"
      fill="currentColor"
      opacity="0.22"
      fontSize="11"
      fontWeight="600"
      letterSpacing="2"
    >
      BACK
    </text>
  </g>
)
