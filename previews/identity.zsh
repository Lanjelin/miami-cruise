# Preview-only display identity. Source after the Miami Cruise prompt theme.
# %n uses the OS login name, not $USER; replace prompt escapes before rendering
# without changing the user account, host configuration or captured image pixels.
_miami_cruise_user_host=${_miami_cruise_user_host//\%n/miami}
_miami_cruise_user_host=${_miami_cruise_user_host//\%m/cruise}
_miami_cruise_user_host=${_miami_cruise_user_host//\%M/cruise}
