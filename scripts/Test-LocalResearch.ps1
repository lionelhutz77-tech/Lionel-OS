param([string]$Model = 'qwen3:4b')
$ErrorActionPreference = 'Stop'
if ($Model -ne 'qwen3:4b') { throw 'This diagnostic is restricted to the previously installed local qwen3:4b model.' }
$Project = Join-Path $env:USERPROFILE 'LionelOS-Research-Check'
New-Item -ItemType Directory -Force -Path $Project | Out-Null
$Tags = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 10
if ($Model -notin $Tags.models.name) { throw 'Local model missing. No automatic download will be performed.' }
$Cases = @(
  'Synthetisches Testmaterial, keine historischen Fakten: Quelle A, Seite 3: Im Ort X durften 20 von 100 Erwachsenen abstimmen. Quelle B, Seite 7: In Ort Y waren es 60 von 100. Aufgabe: Nenne die beiden Werte mit Fundstellen. Kann daraus eine zeitliche Verbesserung oder deren Ursache abgeleitet werden? Begruende knapp. Erfinde nichts.',
  'Test ohne Belege: Behauptung: Heutige Eliten sind direkte Nachfahren mittelalterlicher Adeliger. Aufgabe: Ist diese Aussage durch die mitgelieferten Quellen bewiesen? Es wurden keine Quellen mitgeliefert. Erfinde keine Literatur.',
  'Synthetisches Testmaterial: Quelle A S. 1: In einer Stichprobe hatten 8 von 10 Personen mit vermoegenden Eltern einen Hochschulabschluss. Quelle B S. 2: Aus der Stichprobe lassen sich keine Aussagen zur gesamten Bevoelkerung ableiten. Aufgabe: Formuliere einen sachlichen Absatz mit beiden Fundstellen und Grenzen, ohne Kausalbehauptung.'
)
$Results = @()
foreach ($Case in $Cases) {
  $Watch = [Diagnostics.Stopwatch]::StartNew()
  $Body = @{model=$Model; prompt=$Case; stream=$false; think=$false; options=@{temperature=0.1;num_ctx=4096;num_predict=600}} | ConvertTo-Json -Depth 5
  $Response = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/generate' -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($Body)) -TimeoutSec 900
  $Watch.Stop()
  $Results += @{task=$Case; answer=$Response.response; seconds=$Watch.Elapsed.TotalSeconds; done=$Response.done; done_reason=$Response.done_reason}
}
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Output = Join-Path $Project "research-test-$Stamp.json"
$Results | ConvertTo-Json -Depth 8 | Set-Content -Path $Output -Encoding UTF8
Write-Host "Test saved: $Output"
Write-Host 'Please upload this JSON file. These tests do not automatically certify research quality.'
