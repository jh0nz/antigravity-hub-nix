# Antigravity Hub and CLI for Nix

This flake packages Google's proprietary Antigravity Hub and CLI binaries for NixOS. The
recipe and pinned binary hashes are kept here; no Antigravity source code is
included.

## Build

```sh
nix build .#antigravity-hub
nix build .#antigravity-cli
nix run .#agy -- --version
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

The separate **Update Antigravity CLI** workflow checks the official installer’s
Linux manifests daily, pins the version, URLs and SHA-512 checksums in
`cli-sources.json`, then builds and checks `agy --version` before committing.
To update or check the CLI locally:

```sh
python3 update-cli.py --check
python3 update-cli.py
```

Both packages support Linux x86_64 and aarch64 binaries; this flake currently
exports packages for x86_64-linux.

## Use as a flake input

After publishing this directory as a GitHub repository, add it to a system flake:

```nix
inputs.antigravity-hub-nix = {
  url = "github:jh0nz/antigravity-hub-nix";
  inputs.nixpkgs.follows = "nixpkgs";
};
```

Install either or both packages:

```nix
home.packages = [
  inputs.antigravity-hub-nix.packages.${pkgs.system}.antigravity-hub
  inputs.antigravity-hub-nix.packages.${pkgs.system}.antigravity-cli
];
```

The CLI command is `agy` (`agy` is also a flake package alias). Run `agy` to
sign in using the official authentication flow. Update the CLI through the flake
pin and your system rebuild; the Nix store is read-only, so `agy update` cannot
replace this installation.

## Distribution

This repository contains only the packaging recipe and update script. The
Antigravity binary remains proprietary and is distributed by Google under its
own terms.
