<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Miami Cruise">
  <defs>
    <linearGradient id="mc-m-sun" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{{warning}}"/>
      <stop offset=".3" stop-color="{{orange}}"/>
      <stop offset=".62" stop-color="{{accent}}"/>
      <stop offset="1" stop-color="{{accent}}"/>
    </linearGradient>
    <clipPath id="mc-m-sky"><rect width="64" height="40"/></clipPath>
    <clipPath id="mc-m-sunc"><circle cx="32" cy="40" r="21"/></clipPath>
    <clipPath id="mc-m-tile"><rect width="64" height="64" rx="14"/></clipPath>
  </defs>
  <g clip-path="url(#mc-m-tile)">
    <rect width="64" height="64" fill="{{bg}}"/>
    <g clip-path="url(#mc-m-sky)">
      <circle cx="32" cy="40" r="21" fill="url(#mc-m-sun)"/>
      <g fill="{{bg}}" clip-path="url(#mc-m-sunc)">
        <rect x="8" y="28" width="48" height="1.6"/>
        <rect x="8" y="32.2" width="48" height="2.4"/>
        <rect x="8" y="36.6" width="48" height="3.4"/>
      </g>
    </g>
    <rect y="40" width="64" height="24" fill="{{panel}}"/>
    <path d="M29,40 H35 L58,64 H6 Z" fill="{{bg}}"/>
    <path d="M29,40 L6,64 M35,40 L58,64" stroke="{{orchid}}" stroke-width="1.6" opacity=".75"/>
    <line x1="0" y1="40" x2="64" y2="40" stroke="{{accent}}" stroke-width="1.4"/>
    <path d="M32,44 V47 M32,51 V56" stroke="{{text}}" stroke-width="1.6" stroke-linecap="round" opacity=".7"/>
  </g>
</svg>
