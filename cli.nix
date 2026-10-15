{
  lib,
  stdenv,
  fetchurl,
  autoPatchelfHook,
  libsecret,
  makeWrapper,
}:

let
  sourceInfo = builtins.fromJSON (builtins.readFile ./cli-sources.json);
  source = sourceInfo.sources.${stdenv.hostPlatform.system}
    or (throw "Unsupported system: ${stdenv.hostPlatform.system}");
in
stdenv.mkDerivation {
  pname = "antigravity-cli";
  version = sourceInfo.version;

  src = fetchurl { inherit (source) url hash; };
  sourceRoot = ".";
  strictDeps = true;
  nativeBuildInputs = [ autoPatchelfHook makeWrapper ];
  # Linux credentials use Secret Service, loaded dynamically.
  runtimeDependencies = [ (lib.getLib libsecret) ];
  dontConfigure = true;
  dontBuild = true;

  installPhase = ''
    runHook preInstall
    install -Dm755 antigravity $out/bin/agy
    runHook postInstall
  '';

  postFixup = ''
    wrapProgram $out/bin/agy --set AGY_CLI_DISABLE_AUTO_UPDATE 1
  '';

  meta = {
    description = "Google Antigravity agent for the terminal";
    homepage = "https://antigravity.google/docs/cli/overview";
    changelog = "https://antigravity.google/docs/changelog?tab=cli";
    license = lib.licenses.unfree;
    sourceProvenance = with lib.sourceTypes; [ binaryNativeCode ];
    platforms = lib.attrNames sourceInfo.sources;
    mainProgram = "agy";
  };
}
