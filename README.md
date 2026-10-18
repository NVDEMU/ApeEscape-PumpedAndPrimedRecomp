# Ape Escape: Pumped & Primed Recomp

Experimental **native desktop recompilation** for Ape Escape: Pumped & Primed, using the upstream [PS2 Web Recomp](https://github.com/snuri00/ps2-web-recomp) toolchain.

## Status

The game image has been parsed and the pinned toolchain completed the Linux native recompilation/exploration pipeline. The desktop workflow builds native Windows and macOS apps with SDL windows and platform GPU surfaces (Win32/D3D and Cocoa/Metal). A successful compile is not proof of full playability; boot, menus, graphics, audio, controller input, and longer gameplay still need testing.

This project targets **native Windows and macOS applications, not a browser build**.

## Build

1. Add a repository Actions secret named `GAME_ASSETS_LINK` containing the MEGA link to your own CHD dump. This secret is used only by the build runner to fetch the source disc image.
2. Open **Actions → Ape Escape: Pumped & Primed — Native Desktop Builds → Run workflow**, or push a change to the workflow, portability patch, or packaging scripts.
3. Open the successful run and download the platform artifact you need.

## Downloads (no encryption)

**Build artifacts are uploaded as normal, unencrypted files.** No GPG passphrase or decryption step is required.

- **macOS:** download the `pumped-primed-macos-app` artifact and extract GitHub's artifact ZIP wrapper. Open `ApeEscape-PumpedAndPrimed-macOS.dmg`, then drag or copy the app as usual.
- **Windows:** download the `pumped-primed-windows-app` artifact and extract GitHub's artifact ZIP wrapper. Open the resulting `ApeEscape-PumpedAndPrimed-Windows.zip` and run the launcher inside the extracted folder.

The app asks you to select a compatible ISO at launch. **The source CHD and converted ISO are not uploaded as artifacts.** Use an ISO made from a disc image you are legally entitled to use.

Artifacts are kept for a short period, so download them soon after a successful run.

## Legal and attribution

Use a game image you are legally entitled to use. The project does not publish the original disc image as an ISO artifact. See the upstream toolchain's [legal notes](https://github.com/snuri00/ps2-web-recomp#legal).

Ape Escape and related names are trademarks of their respective owners. This is an independent experimental project and is not affiliated with or endorsed by Sony or the game's publisher.
