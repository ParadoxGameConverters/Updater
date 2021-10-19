# Updater
Updater for PGCG (Paradox Game Converters Group) converters written in Python.

Needs to be put inside an "Updater" directory in the root converter directory.

Takes two parameters:
1) URL of converter release .zip to download, for example `"https://github.com/ParadoxGameConverters/ImperatorToCK3/releases/download/1.2.3/ImperatorToCK3.zip"`
2) Name of converter backend folder, for example `"ImperatorToCK3"`

Usage:
`./Updater/updater.exe "https://github.com/ParadoxGameConverters/ImperatorToCK3/releases/download/1.2.3/ImperatorToCK3.zip" "ImperatorToCK3"
`