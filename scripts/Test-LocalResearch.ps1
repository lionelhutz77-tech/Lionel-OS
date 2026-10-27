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
$Cases += 'Historische Primärquelle, Auszug aus Art. 109 der Verfassung des Deutschen Reichs (1919), Absatz 3: Öffentlich-rechtliche Vorrechte oder Nachteile der Geburt oder des Standes sind aufzuheben. Adelsbezeichnungen gelten nur als Teil des Namens und dürfen nicht mehr verliehen werden. Fundort: https://de.wikisource.org/wiki/Verfassung_des_Deutschen_Reichs_%281919%29 . Aufgabe: Erkläre ausschließlich anhand dieses Auszugs in höchstens vier deutschen Sätzen, was er für rechtliche Privilegien und Adelsbezeichnungen bestimmt. Beweist er außerdem, dass Vermögensunterschiede oder gesellschaftlicher Einfluss ehemaliger Adelsfamilien verschwanden? Trenne Textaussage und unbelegte Schlussfolgerung.'
$Cases += 'Synthetische Quellen: A, S. 2: In Region X wurden 1900 drei von zehn untersuchten Ämtern von Adeligen besetzt. B, S. 8: In derselben Region wurden 1900 sechs von zehn untersuchten Ämtern von Adeligen besetzt. Es fehlen Angaben zur Auswahl der Ämter. Aufgabe: Benenne den Widerspruch mit beiden Fundstellen. Löse ihn nicht durch erfundene Erklärungen und bilde keinen vermeintlich gesicherten Mittelwert. Welche Angaben müssten geprüft werden? Antworte auf Deutsch in höchstens vier Sätzen.'
$Results = @()
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Output = Join-Path $Project "research-test-v2-$Stamp.json"
$Index = 0
foreach ($Case in $Cases) {
  $Index++
  Write-Host "Test $Index / $($Cases.Count) gestartet. Bitte warten..."
  $Watch = [Diagnostics.Stopwatch]::StartNew()
  $Body = @{model=$Model; messages=@(@{role='user';content=$Case}); stream=$false; think=$true; options=@{temperature=0.6;num_ctx=8192;num_predict=2048}} | ConvertTo-Json -Depth 6
  $Response = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/chat' -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($Body)) -TimeoutSec 900
  $Watch.Stop()
  $Results += @{task=$Case; answer=$Response.message.content; seconds=$Watch.Elapsed.TotalSeconds; done=$Response.done; done_reason=$Response.done_reason; model=$Response.model}
  $Results | ConvertTo-Json -Depth 8 | Set-Content -Path $Output -Encoding UTF8
  Write-Host "Test $Index gespeichert: $($Response.done_reason), $([math]::Round($Watch.Elapsed.TotalSeconds)) Sekunden"
}
$Results | ConvertTo-Json -Depth 8 | Set-Content -Path $Output -Encoding UTF8
Write-Host "Test saved: $Output"
Write-Host 'Please upload this JSON file. These tests do not automatically certify research quality.'
