This is for the Czech keyboard Macbook Neo I bought in Prague in June 2026

I needed to be funtional quick! So I told AI to use Karabiner-Elements to do sort-of-minimal 
changes with respect to the actual keycaps, plus ad-hoc my-personal-muscle memory (learned on a US keyboard)

## Depends on:
- Set your Input Source (in System Settings) to Czech QWERTY
- No other input sources installed
- Install Karabiner-Elements v16.0.0 

## The config does the following:
- Swap `Y` and `Z`
- Numbers are unshifted
- ⇧-_\<number keys\>_ output what would otherwise require ⌥ (obeying the keycaps)
- Map umlaut-combiner (dead key) to ↩ because the ↩ key is too skinny for my phat phingers
- Map `ů` → `;` and `§` (section sign) → `'` (don't require ⌥)

## Scripts

- Backup the current Karabiner rules JUST IN CASE:
  ```
  ./backup-karabiner-settings.sh
  ```

- Copy the backup over the active config (That's my dev cycle)
  
  __BEWARE! This is nice 'n destructive!__
  ```
  ./copy-local-backup-back-to-config.sh
  ```

- Compare local-dir backup to active config
  ```
  ./diff-backup-with-active-config.sh
  ```
  Prints a recursive diff of `~/.config/karabiner` vs `karabiner-config-backup-v16.0.0`.
  If there are no differences, diff prints nothing and exits successfully.
