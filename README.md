# Antigravity Hub for Nix

This flake packages Google's proprietary Antigravity Hub binary for NixOS. The
recipe and pinned binary hashes are kept here; no Antigravity source code is
included.

## Build

```sh
nix build .#antigravity-hub
```

## Automatic updates

The GitHub Actions workflow checks Google's official download page daily and can
also be started with **Actions → Update Antigravity Hub → Run workflow**. When
the published version or build ID changes, it calculates hashes for both Linux
architectures, builds the package, and commits the new pin.

The updater has a non-mutating check mode for local use:

```sh
python3 update.py --check
```

## Use as a flake input

After publishing this directory as a GitHub repository, add it to a system flake:

```nix
inputs.antigravity-hub-nix = {
  url = "github:jh0nz/antigravity-hub-nix";
  inputs.nixpkgs.follows = "nixpkgs";
};
```

Then install `inputs.antigravity-hub-nix.packages.${pkgs.system}.antigravity-hub`.

## Distribution

This repository contains only the packaging recipe and update script. The
Antigravity binary remains proprietary and is distributed by Google under its
own terms.
