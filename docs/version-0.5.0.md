# Version 0.5.0 — Pilotmessung mit nachvollziehbarer Freigabe

## Update und nächster einzelner Lauf

1. In HACS **Battery Charge Manager → Aktualisieren** auf **0.5.0**, anschließend Home Assistant neu starten. Die Oberfläche zeigt 0.5.0. Bei einer bereits geöffneten Browseransicht einmal neu laden.
2. Unter **Verwalten → Einstellungen** die Quelle **Pilot: gemeldete Leistung integrieren** und zunächst **Netzenergie brutto** wählen und speichern. Bestehende Einstellungen werden beim Update nicht automatisch umgestellt.
3. Optional zuerst mit einem vollen Akku eine Referenz aufnehmen: das genaue Akku-/Ladeanordnungsprofil und die Anzahl wählen, **Restmessung vorbereiten** starten, die Einschalt-Nachladung am USB-Gerät bzw. der Ladeanzeige abwarten und **Nachladung beendet – Messfenster starten** drücken. Die Aufzeichnung enthält auch die Vorbereitung, die Auswertung beginnt erst nach weiteren fünf Minuten und dauert 30 Minuten. Danach schaltet die App geprüft ab.
4. Die Restmessung in **Kalibrationen → Restverbrauch mit vollem Akku** öffnen, Kurve und drei Zeitblockmittel prüfen und mit Begründung **Zur Verwendung freigeben**. Eine einzelne geprüfte Referenz genügt. Instabile oder unterbrochene Referenzen sind gesperrt.
5. Den standardisiert entladenen Akku im gleichen Profil kalibrieren, den USB-Zähler am Beginn zurücksetzen. Mit passender Referenz kann **Restphase passend – Ladeende prüfen** erscheinen. Die Pilotregel schaltet nicht automatisch ab; **Beenden und prüfen** beendet die Aufzeichnung mit kontrolliertem Ausschalten.
6. In den Details USB-Endstand samt Vergleichsnotiz eintragen. Dieser Wert gehört zum gesamten Vorgang, einschließlich Nachlauf. Ein späteres Wiedereinschalten für ein Foto und dessen Momentanwerte sind kein Endpunktbeleg. Den gewünschten Ladeabschnitt in **Ladeabschnitt festlegen** mit Begründung speichern; einen vorhandenen Vorschlag kann man zuvor ins Zeitfeld übernehmen.
7. Den gesamten Lauf exportieren und einzeln auswerten. Erst nach der Prüfung **Zur Verwendung freigeben** wählen. Eine freigegebene Kalibration reicht für ein vorläufiges Energieziel. Wiederholungen zeigen Streuung, sie sind keine pauschale Drei-Läufe-Voraussetzung.

Ohne ausgewähltes Ladeende bleibt die Ladedauer unbekannt. Die Aufzeichnungsdauer ist separat sichtbar. Zehn Stunden Aufzeichnung werden dadurch nicht automatisch zu zehn Stunden Ladezeit.

## Messgrößen und Grenzen

Die neue Quelle integriert vorhandene nichtnegative Wirkleistungszustände über ihre Zeitabschnitte: `E += P_vorher × Sekunden / 3600`. Auch länger unverändert gemeldete Werte tragen bei. Das Ergebnis bleibt bei solchen Anteilen eine **Schätzung**, keine Bestätigung absoluter Messgenauigkeit. Frische, fortgeschriebene und nicht aufgezeichnete Zeiten sowie der längste Abschnitt mit fortgeschriebenen Werten bleiben unterscheidbar.

Aufzeichnungslücken über 120 Sekunden, Zeitumkehr, ungültige Leistung und Neustartintervalle werden nicht ergänzt. Eine unterbrochene Normalladung schaltet ab; ein unterbrochener Kalibrationsversuch bleibt gespeichert und kann für den unvollständigen Abschnitt nicht freigegeben werden. Die Zeit zwischen Einschaltauftrag und erstem Messpunkt wird separat ausgewiesen. Der ausgewertete Energieabschnitt beginnt mit dem ersten tatsächlich aufgezeichneten Punkt.

Ein zurückgesetzter oder ausgefallener Wh-Zähler ist im Pilotmodus nur ein Problem seines Vergleichskanals. Benötigte Leistungs-, Schalter- und konfigurierte Temperatursensoren, Leistungs-/Temperaturgrenzen und der Sicherheitstimer bleiben wirksam. Quelle, Korrektur und Ziel werden bei Beginn eingefroren.

**Netzenergie brutto** braucht keine zusätzliche Leerlaufmessung. **Netzenergie ohne gemessenen Leerlauf** verwendet eine passende, zuverlässige Leerlaufreferenz ohne Akku und speichert diese mit dem Vorgang. Eine Normalladung verwendet dieselbe Basis und Referenz wie ihr freigegebenes Ziel. Die Restreferenz mit vollem Akku dient ausschließlich dem Endpunktvergleich; sie wird nicht als konstanter Verlust von der ganzen Ladung abgezogen. Netz-Wh, USB-Eingangs-Wh und Akku-Nennenergie sind verschiedene Größen. Es erfolgt keine Anpassung der Messwerte an die Nennenergie oder den USB-Wert.

Die bisherigen Modi `auto`, `meter` und `power` behalten ihre Integrations-/Auswahlregeln. Die neue Freigabe gilt für die Verwendung aller historischen und neuen Kalibrationen in zukünftigen Ladezielen.

## Versionierte Restphasenregel

Das Referenzfenster enthält drei gleich lange Zehn-Minuten-Blöcke. Ihre zeitgewichteten Mittelwerte werden aus der Rohleistung gebildet. Die Toleranz ist `max(0,03 W, halbe kleinste beobachtete positive Werteabstufung)`. Fehlt eine Abstufung, gelten 0,03 W mit dem Hinweis unbekannter Auflösung; dies ist keine Hersteller-Genauigkeitsangabe. Liegen die Blockmittel mehr als zweimal diese Toleranz auseinander, ist die Referenz instabil.

Die Vergleichsobergrenze ist der größte Blockmittelwert plus Toleranz. Ein vorausgegangenes mindestens fünfminütiges Fenster muss oberhalb von Obergrenze plus Toleranz liegen. Anschließend ergeben vier aufeinanderfolgende mindestens fünfminütige Fenster unterhalb der Obergrenze einen Vorschlag. Grenzen liegen auf Originalmesspunkten; die zeitliche Genauigkeit ist durch die Fenster und den Beobachtungsabstand begrenzt. Echte Lücken verwerfen einen Kandidaten, ein neuer höherer Block ebenfalls. Pulse werden zeitgewichtet bewertet. Der Vorschlag ist eine prüfbare Pilotregel, kein Nachweis des Zellladezustands.

Referenzen passen ausschließlich zu Setup-ID/Revision, Akku-ID/Revision, Stückzahl und geordneten Ports. Verwendung und Widerruf sind mit Nutzer, Zeitpunkt und Begründung protokolliert. Änderungen an einer freigegebenen Auswertung bzw. Zuordnung erfordern eine neue Entscheidung; veraltete Dialoge werden abgewiesen.

## Darstellung, Speicherung und Migration

Leistung und Energie besitzen getrennte Diagramme mit gemeinsamer Zeitachse. Frische und fortgeschriebene Leistungsabschnitte werden getrennt markiert. Der Zählerkanal hat eigene Lücken. Qualitätsgrenzen werden vor der Reduktion der dargestellten Punkte erhalten; bei sehr vielen Wechseln zeigen Zeitfenster Min/Max und ein Qualitätsband. Das ist eine Übersicht, alle verfügbaren Originalwerte bleiben über die Rohdatenanzeige und den Export zugänglich.

Metadatenschema 6 ergänzt Restmessungen, Pilotentscheidungen, USB-Vergleiche und Freigabehistorien. Rohdaten, Trace-IDs und Hashketten bleiben unverändert. Historische gültige Kalibrationen erhalten **Prüfung und Freigabe ausstehend**: Das Update erfindet keine menschliche Freigabe. Historische Zählerwerte werden nicht automatisch zu Pilotzielen. Eine ausdrücklich gestartete Neuauswertung kann die vorhandene Leistungsspur mit der eingestellten Pilotbasis auswerten; sie benötigt anschließend eine neue Freigabe.

Vor einem Downgrade ein vollständiges Home-Assistant-Backup einschließlich `.storage` und einen vollständigen Messdatenexport sichern. Ältere Versionen verstehen die neuen Metadaten/Freigaben nicht und können ihre eigenen früheren Auswahlregeln anwenden. Ein vollständiges Backup stellt einen zusammengehörigen Software- und Datenstand wieder her.

## Entwicklungsprüfung

Die CI führt Python- und JavaScript-Regressionstests, JavaScript-Syntax sowie die vorhandenen HACS-/hassfest-Workflows aus. Testdaten sind synthetisch; private Originalexporte werden nicht mitgeliefert. Die Änderungen fügen keine Home-Assistant-Laufzeitabhängigkeiten hinzu.
