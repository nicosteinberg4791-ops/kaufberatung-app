<#
.SYNOPSIS
  Testlauf des Projekts; läuft auch als Git-pre-commit-Hook (.githooks/pre-commit).

.BESCHREIBUNG
  Fehler (zählen, Exitcode = Zahl der Fehler, Commit wird abgebrochen):
    unittest tests/test_*.py (falls vorhanden) · Pester tests/*.Tests.ps1 (falls vorhanden).
  Ohne eine einzige Testdatei bleibt der Lauf grün (Gerüst); sobald das Projekt Tests schreibt, laufen sie hier.
  Hook einrichten (einmal je Klon): git config core.hooksPath .githooks
  Ausgabe am Ende: „Fehler: N · Warnungen: M“.

  Laufprotokoll (lokale CI, Kennzahlen ci_gruen/ci_laufzeit): je Lauf eine Zeile in
    %LOCALAPPDATA%\AI-Work-Playbook\projekte\<Projektordner>\sammellauf.csv (daneben besitzer.txt mit dem vollen Pfad des
    Hauptordners, beim ersten Lauf geschrieben; gehört der Ordner einem anderen gleichnamigen Projekt, gibt es eine Warnung
    statt einer Zeile)
    (Projektordner = Ordnername des Hauptordners, auch wenn der Commit in einem Worktree läuft).
    Kopf: zeit;quelle;baum;sauber;fehler;warnungen;sekunden;werkzeuge;werkzeuge_getestet;abdeckung
    Die ersten sieben Spalten wie das Playbook-Protokoll: zeit ISO mit Zone, quelle hook/hand, baum = git write-tree des
    Index (hand: HEAD^{tree} bei sauberem Arbeitsbaum), sauber 1/0 (Tests liefen auf genau diesem Baum), Zahlen.
  Werkzeugkennzahlen (nur Projekte mit eigenen Werkzeugen unter werkzeuge/): die letzten drei Spalten bleiben leer, solange
    das Projekt sie nicht liefert. Liefern: ein eigener Test schreibt während des Laufs tests/kennzahlen.json
    {"werkzeuge": 4, "werkzeuge_getestet": 3, "abdeckung": 0.85}  (abdeckung 0..1; Datei steht in .gitignore, der Runner
    löscht sie vor dem Lauf und liest sie danach).
#>
[CmdletBinding()]
param([switch] $Hook)   # -Hook: Aufruf aus .githooks/pre-commit (Laufprotokoll mit git write-tree)

$uhr = [System.Diagnostics.Stopwatch]::StartNew()
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$env:PYTHONIOENCODING = 'utf-8'
$wurzel = Split-Path -Parent $PSScriptRoot
$tests = $PSScriptRoot
$fehler = 0; $warnungen = 0

function Melde([string] $name, [bool] $ok, [string] $detail = '') {
  if ($ok) { "OK      $name" } else { "FEHLER  $name"; if ($detail) { "        $detail" }; $script:fehler++ }
}
function Warne([string] $text) { "WARNUNG $text"; $script:warnungen++ }
function Lauf([scriptblock] $befehl) {
  # Externes Programm: Exitcode und letzte Ausgabezeilen; Startfehler und fehlender Exitcode zählen als Fehler (Code -1)
  $alt = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  $global:LASTEXITCODE = $null; $aus = @(); $code = -1
  try {
    $aus = & $befehl 2>&1 | ForEach-Object { if ($_ -is [System.Management.Automation.ErrorRecord] -and
        $_.Exception -is [System.Management.Automation.CommandNotFoundException]) { throw $_.Exception }; "$_" }
    if ($null -ne $LASTEXITCODE) { $code = $LASTEXITCODE }
  } catch { $aus += "Startfehler: $($_.Exception.Message)" } finally { $ErrorActionPreference = $alt }
  [pscustomobject]@{ Code = $code; Text = (($aus | Select-Object -Last 3) -join ' | ') }
}
function Get-Laufstand {
  # Protokollzeile: im Hook der Baum des Index (git write-tree = Stand des Commits); sauber heißt, Index und Arbeitsbaum
  # stimmen überein und es gibt keine unversionierten Dateien. Ohne Hook zählt HEAD^{tree}, aber nur bei sauberem Stand.
  $alt = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  try {
    $baum = ''; $sauber = 0; $env:GIT_OPTIONAL_LOCKS = '0'; $env:GIT_NO_LAZY_FETCH = '1'   # nur lesen: Index nicht auffrischen, nichts nachladen
    $offen = @(& git -C $wurzel status --porcelain --untracked-files=all 2>$null)
    $unversioniert = @(& git -C $wurzel ls-files --others --exclude-standard 2>$null)
    $null = & git -C $wurzel diff --quiet 2>$null; $gleich = ($LASTEXITCODE -eq 0)
    if ($Hook) { $baum = [string](& git -C $wurzel write-tree 2>$null); $sauber = [int]($gleich -and -not $unversioniert.Count) }
    elseif (-not $offen.Count) { $baum = [string](& git -C $wurzel rev-parse 'HEAD^{tree}' 2>$null); $sauber = 1 }
  } finally { $ErrorActionPreference = $alt }
  [pscustomobject]@{ Baum = $baum.Trim(); Sauber = $sauber; Offen = ($offen -join "`n") }
}
function Test-StandGleich($a, $b) { ($a.Baum -ceq $b.Baum) -and ($a.Sauber -eq $b.Sauber) -and ($a.Offen -ceq $b.Offen) }
function Get-Haupt {
  # Voller Pfad des Hauptordners über das gemeinsame Git-Verzeichnis (gilt auch im Worktree); GIT_DIR/GIT_INDEX_FILE des
  # Hooks würden die Abfrage umlenken und werden dafür kurz entfernt.
  $alt = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  $gd = $env:GIT_DIR; $gi = $env:GIT_INDEX_FILE; $env:GIT_DIR = $null; $env:GIT_INDEX_FILE = $null
  try {
    $cd = [string](& git -C $wurzel rev-parse --git-common-dir 2>$null)
    if ($cd.Trim()) {
      $cd = $cd.Trim(); $voll = [IO.Path]::GetFullPath($(if ([IO.Path]::IsPathRooted($cd)) { $cd } else { Join-Path $wurzel $cd }))
      $haupt = if ((Split-Path -Leaf $voll) -eq '.git') { Split-Path -Parent $voll } else { $voll }
      return $haupt
    }
  } finally { $env:GIT_DIR = $gd; $env:GIT_INDEX_FILE = $gi; $ErrorActionPreference = $alt }
  return $wurzel
}

$vorher = Get-Laufstand
$kennzahlenDatei = Join-Path $tests 'kennzahlen.json'
if (Test-Path -LiteralPath $kennzahlenDatei) { Remove-Item -LiteralPath $kennzahlenDatei -Force }

# 1. unittest (nur wenn Testdateien vorhanden; -B: kein __pycache__)
$pyTests = @(Get-ChildItem -LiteralPath $tests -Filter 'test_*.py' -File)
if ($pyTests.Count) {
  $r = Lauf { python -I -B -m unittest discover -s $tests -t $tests -p 'test_*.py' }
  Melde 'unittest tests/test_*.py' ($r.Code -eq 0) $r.Text
}
# 2. Pester (Pester 3.4 ist in Windows enthalten; je Testdatei ein eigener Lauf, Code = Zahl fehlgeschlagener Tests)
$pesterDateien = @(Get-ChildItem -LiteralPath $tests -Filter '*.Tests.ps1' -File | Sort-Object Name)
if ($pesterDateien.Count) {
  $o = $tests.Replace("'", "''")
  $r = Lauf { & powershell.exe -NoProfile -Command "try { Import-Module Pester -MaximumVersion '3.99' -ErrorAction Stop } catch { 'Pester nicht ladbar: ' + `$_.Exception.Message; exit 91 }; `$rot = 0; foreach (`$d in @(Get-ChildItem -LiteralPath '$o' -Filter '*.Tests.ps1' -File | Sort-Object Name)) { `$e = Invoke-Pester -Script `$d.FullName -PassThru -Quiet; if (`$null -eq `$e -or `$e.TotalCount -lt 1) { 'ohne Testergebnis: ' + `$d.Name; `$rot++; continue }; `$rot += `$e.FailedCount }; exit `$rot" }
  Melde 'Pester tests/*.Tests.ps1' ($r.Code -eq 0) $r.Text
}
if (-not $pyTests.Count -and -not $pesterDateien.Count) {
  Warne 'noch keine Tests im Projekt (tests/test_*.py oder tests/*.Tests.ps1)'
}

# Laufprotokoll; ein Schreibfehler macht den Lauf nicht rot, erscheint aber als Warnung
try {
  $nachher = Get-Laufstand
  $baum = $nachher.Baum; $sauber = $nachher.Sauber
  if (-not (Test-StandGleich $vorher $nachher)) {
    $baum = ''; $sauber = 0
    Warne 'Stand während des Laufs verändert: Lauf gilt für keinen Git-Baum'
  }
  $wk = @('', '', '')   # werkzeuge, werkzeuge_getestet, abdeckung: leer, solange das Projekt sie nicht liefert
  if (Test-Path -LiteralPath $kennzahlenDatei) {
    try {
      $k = Get-Content -LiteralPath $kennzahlenDatei -Raw -Encoding UTF8 | ConvertFrom-Json
      $inv = [Globalization.CultureInfo]::InvariantCulture
      # Pflichtfelder, Ganzzahligkeit und Wertebereich vor der Umwandlung prüfen: Ungültiges bleibt leer (offen) und warnt
      $w = $k.werkzeuge; $g = $k.werkzeuge_getestet; $a = $k.abdeckung
      $ganz = { param($x) ($x -is [int] -or $x -is [long]) -and $x -ge 0 }
      $zahl = { param($x) $x -is [double] -or $x -is [decimal] -or $x -is [single] -or $x -is [int] -or $x -is [long] }
      if (-not ((& $ganz $w) -and (& $ganz $g) -and ($g -le $w) -and (& $zahl $a) -and ($a -ge 0) -and ($a -le 1))) {
        throw 'werkzeuge und werkzeuge_getestet müssen ganze Zahlen sein (getestet höchstens werkzeuge), abdeckung eine Zahl von 0 bis 1'
      }
      $wk = @(([int]$w).ToString($inv), ([int]$g).ToString($inv), ([double]$a).ToString($inv))
    } catch { Warne "tests/kennzahlen.json ungültig, Felder bleiben leer: $($_.Exception.Message)" }
  }
  $haupt = Get-Haupt
  $ordner = Join-Path (Join-Path (Join-Path $env:LOCALAPPDATA 'AI-Work-Playbook') 'projekte') (Split-Path -Leaf $haupt)
  $null = New-Item -ItemType Directory -Force -Path $ordner
  # besitzer.txt: voller Pfad des Hauptordners, beim ersten Lauf geschrieben. Gleichnamige Projekte in anderen Elternordnern
  # teilen sonst den Ordner; passt der Besitzer nicht, entsteht keine Protokollzeile.
  $besitzer = Join-Path $ordner 'besitzer.txt'
  if (-not (Test-Path -LiteralPath $besitzer)) {
    # Ein Protokoll ohne nachgewiesenen Besitzer wird nicht übernommen (Herkunft unbekannt, evtl. gleichnamiges Projekt): beiseite legen
    $altCsv = Join-Path $ordner 'sammellauf.csv'
    if (Test-Path -LiteralPath $altCsv) {
      Move-Item -LiteralPath $altCsv -Destination (Join-Path $ordner ('sammellauf-ohne-besitzer-' + (Get-Date -Format 'yyyyMMddTHHmmss') + '.csv'))
      Warne 'Laufprotokoll ohne besitzer.txt beiseite gelegt (sammellauf-ohne-besitzer-<zeit>.csv), neues Protokoll beginnt'
    }
    Set-Content -LiteralPath $besitzer -Value $haupt -Encoding UTF8
  }
  $eigner = (Get-Content -LiteralPath $besitzer -Raw -Encoding UTF8).Trim()
  if ($eigner.TrimEnd('\', '/') -ine $haupt.TrimEnd('\', '/')) {
    Warne "Laufprotokoll gehört zu '$eigner', nicht zu '$haupt': keine Protokollzeile geschrieben"
  } else {
    $csv = Join-Path $ordner 'sammellauf.csv'
    if (-not (Test-Path -LiteralPath $csv)) {
      Set-Content -LiteralPath $csv -Value 'zeit;quelle;baum;sauber;fehler;warnungen;sekunden;werkzeuge;werkzeuge_getestet;abdeckung' -Encoding UTF8
    }
    $sek = [math]::Round($uhr.Elapsed.TotalSeconds, 1).ToString([Globalization.CultureInfo]::InvariantCulture)
    $zeile = (@((Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz'), $(if ($Hook) { 'hook' } else { 'hand' }), $baum, $sauber, $fehler, $warnungen, $sek) + $wk) -join ';'
    Add-Content -LiteralPath $csv -Value $zeile -Encoding UTF8
  }
} catch { Warne "Laufprotokoll nicht geschrieben: $($_.Exception.Message)" }

"Fehler: $fehler · Warnungen: $warnungen"
exit $fehler
