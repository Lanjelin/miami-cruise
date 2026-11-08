<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Miami Cruise">
  <defs>
    <linearGradient id="mc-l-sun" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{{warning}}"/>
      <stop offset=".24" stop-color="{{orange}}"/>
      <stop offset=".5" stop-color="{{accent}}"/>
      <stop offset="1" stop-color="{{accent}}"/>
    </linearGradient>
    <clipPath id="mc-l-sky"><rect width="64" height="35"/></clipPath>
    <clipPath id="mc-l-sun-c"><circle cx="32" cy="35" r="17"/></clipPath>
    <clipPath id="mc-l-tile"><rect width="64" height="64" rx="14"/></clipPath>
    <filter id="mc-car-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="1.1"/></filter>
    <filter id="mc-l-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="1.6"/></filter>
  </defs>
  <g clip-path="url(#mc-l-tile)">
    <rect width="64" height="64" fill="{{bg}}"/>
    <g clip-path="url(#mc-l-sky)">
      <circle cx="32" cy="35" r="22" fill="{{accent}}" opacity=".16" filter="url(#mc-l-glow)"/>
      <circle cx="32" cy="35" r="17" fill="url(#mc-l-sun)"/>
      <g fill="{{bg}}" clip-path="url(#mc-l-sun-c)">
        <rect x="14" y="26" width="36" height="1.3"/>
        <rect x="14" y="29.4" width="36" height="2"/>
        <rect x="14" y="33" width="36" height="2.8"/>
      </g>
    </g>
    <rect y="35" width="64" height="29" fill="{{panel}}"/>
    <path d="M28.5,35 H35.5 L62,64 H2 Z" fill="{{bg}}"/>
    <path d="M28.5,35 L2,64 M35.5,35 L62,64" stroke="{{orchid}}" stroke-width="1" opacity=".6"/>
    <line x1="0" y1="35" x2="64" y2="35" stroke="{{accent}}" stroke-width=".8" opacity=".9"/>
    <path d="M32,39 V42 M32,45.5 V50" stroke="{{text}}" stroke-width="1" stroke-linecap="round" opacity=".55"/>
    {{car}}
  </g>
</svg>
