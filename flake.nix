{
  description = "Nix packages for Google Antigravity Hub and CLI";

  inputs.nixpkgs.url = "https://channels.nixos.org/nixos-unstable/nixexprs.tar.xz";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
      antigravity-hub = pkgs.callPackage ./package.nix { };
      antigravity-cli = pkgs.callPackage ./cli.nix { };
    in
    {
      packages.${system} = {
        default = antigravity-hub;
        inherit antigravity-hub antigravity-cli;
        agy = antigravity-cli;
      };
    };
}
