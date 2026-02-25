{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.pip
    python3Packages.virtualenv
    python3Packages.setuptools
    go
    gcc
    stdenv.cc.cc.lib
    zlib
    libffi
    openssl
    pkg-config
  ];

  shellHook = ''
    # Crucial for binary python wheels on NixOS
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.libffi
      pkgs.openssl
    ]}:$LD_LIBRARY_PATH"
    
    if [ ! -d "venv" ]; then
      python3 -m venv venv
    fi
    source venv/bin/activate
    
    # Re-install with the correct library paths available
    pip install qiskit qiskit-aer numpy --quiet
  '';
}
