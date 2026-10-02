{
  description = "Nix package for Google Antigravity Hub";

  inputs.nixpkgs.url = "https://channels.nixos.org/nixos-unstable/nixexprs.tar.xz";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
      antigravity-hub = pkgs.callPackage ./package.nix { };
    in
    {
      packages.${system} = {
        default = antigravity-hub;
        inherit antigravity-hub;
      };
    };
}
