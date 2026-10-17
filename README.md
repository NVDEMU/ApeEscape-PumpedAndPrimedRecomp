# Ape Escape: Pumped & Primed Recomp

Experimental native recompilation compatibility probe using the upstream [PS2 Web Recomp](https://github.com/snuri00/ps2-web-recomp) toolchain.

## Status

This is an early feasibility test, not a confirmed playable port. The first milestone is to check whether the game image can be parsed, translated, and started in the native runner.

## Run the private probe

Add a repository Actions secret named `GAME_ASSETS_LINK` containing a public MEGA **file** link to your CHD, then open **Actions → Pumped & Primed native recomp probe → Run workflow**. A push that changes the workflow also triggers an initial run.

The workflow downloads the CHD only into temporary runner storage, converts it to ISO, and tries a short native recompilation run. It intentionally does not upload the disc image, generated game code, binaries, screenshots, or game-derived build files as artifacts.

If a run fails, inspect the diagnostic summary in the Actions log. Common early blockers include an invalid/expired MEGA share link, exhausted MEGA transfer quota, a CHD that is not a DVD image, or an unsupported PS2 system call / graphics feature.

## Legal and attribution

Use a game image you are legally entitled to use. This repository does not include the original game data. Keep generated game-specific code and binaries private and do not publish them. See the upstream toolchain's [legal notes](https://github.com/snuri00/ps2-web-recomp#legal).

Ape Escape and related names are trademarks of their respective owners. This is an independent experimental project and is not affiliated with or endorsed by Sony or the game's publisher.
