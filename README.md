# Ape Escape: Pumped & Primed Recomp

Experimental **native desktop recompilation** for Ape Escape: Pumped & Primed, using the upstream [PS2 Web Recomp](https://github.com/snuri00/ps2-web-recomp) toolchain.

## Status

The game image has been parsed and the pinned toolchain completed the Linux native recompilation/exploration pipeline. The desktop workflow now attempts native Windows and macOS builds with SDL windows and platform GPU surfaces (Win32/D3D and Cocoa/Metal). A successful compile is not yet proof of full playability; boot, menus, graphics, audio, controller input, and longer gameplay still need testing.

This project targets **native Windows and macOS applications, not a browser build**.

## Build

1. Add a repository Actions secret named `GAME_ASSETS_LINK` containing the MEGA file link to your own CHD dump.
2. Open **Actions → Ape Escape: Pumped & Primed — Native Desktop Builds → Run workflow**, or push a change to the workflow file.
3. Check the run’s individual platform jobs. A completed green job means that platform’s app bundle compiled and was packaged; it does not guarantee the game is fully playable.

The app asks you to select a compatible ISO at launch. The workflow also attempts to provide an optional encrypted ISO converted from the configured CHD, so you don’t have to convert it yourself.

## Downloading encrypted artifacts

This repository is public, so game-specific build outputs are uploaded **encrypted with AES-256**, not as public unencrypted executables. The passphrase is the exact MEGA file-link string stored in `GAME_ASSETS_LINK`.

Download the artifact from the completed workflow run, extract the artifact’s ZIP wrapper, and decrypt the enclosed file with GnuPG, entering that same MEGA link when prompted. For example:

```sh
gpg --output ApeEscape-PumpedAndPrimed-macOS.dmg --decrypt ApeEscape-PumpedAndPrimed-macOS.dmg.gpg
gpg --output ApeEscape-PumpedAndPrimed-Windows.zip --decrypt ApeEscape-PumpedAndPrimed-Windows.zip.gpg
```

If you use the optional disc artifact, decrypt `pumped-primed-disc.iso.gz.gpg` to `pumped-primed.iso.gz`, then run `gunzip pumped-primed.iso.gz`. Choose the resulting ISO in the app’s file picker. Artifacts have a short retention period, so download them soon after a successful run.

## Legal and attribution

Use a game image you are legally entitled to use. The repository does not commit the original disc image or generated game-specific code. Keep generated game-specific code and binaries private and do not publish decrypted build outputs. See the upstream toolchain’s [legal notes](https://github.com/snuri00/ps2-web-recomp#legal).

Ape Escape and related names are trademarks of their respective owners. This is an independent experimental project and is not affiliated with or endorsed by Sony or the game's publisher.
