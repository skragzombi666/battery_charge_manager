# Pilot-Update 0.5.0: Leistungsintegration, Vollakku-Referenz und Freigabe

Status: vom Nutzer freigegeben; Umsetzung und Abnahme für Version 0.5.0.
Datum: 9. Oktober 2026. Grundlage: Repository-Stand 0.4.2.

## Ziel und vereinbarte Rahmenbedingungen

Der nächste einzelne Pilotlauf soll mit der vorhandenen Messkette sinnvoll
auswertbar sein. Der Nutzer beurteilt jeden Lauf, bevor weitere Wiederholungen
oder die Verwendung als Ladeziel folgen. Eine Mindestanzahl von drei Läufen ist
keine Freigabevoraussetzung.

Der Nutzer bestätigt die Zuverlässigkeit seines USB-Messgeräts, die Verwendung
des ausgewählten Akkutyps, Entladung bis zur Abschaltung desselben Geräts,
mehrtägige Ruhezeit sowie gleichbleibende Verkabelung und Ports bei stabilen
Raumbedingungen. Weitere externe Tests des Smart Plugs werden nicht vorausgesetzt.
Die Software muss dessen vorhandene Reportqualität ehrlich abbilden.

Der USB-Zähler dient als separate Vergleichsmessung am Akku-Eingang. Er ersetzt
weder die netzseitige Messung noch wird sein Wert zur nachträglichen Skalierung
der Smart-Plug-Werte benutzt. Momentanwerte nach erneutem Einschalten gehören zu
einem neuen Vorgang, gespeicherte Endstände müssen dem ursprünglichen Lauf
ausdrücklich zugeordnet werden.

## Varianten und Entscheidungsvorschlag

1. Nur frische Leistung integrieren: fachlich klar als Teilintegral, aber bei der
   vorhandenen ereignisabhängigen Meldung fehlt ein großer Teil der Hauptladung.
2. Alle gehaltenen Werte integrieren und als vollständig gemessen bezeichnen:
   ergibt eine durchgehende Zahl, verdeckt jedoch die tatsächliche Unsicherheit.
3. **Empfohlen:** vollständige Integration der vorhandenen gehaltenen Zustände
   als ausdrücklich gewählte Pilotquelle, daneben getrennte Qualitätsdaten und
   das frische Teilintegral. Eine eigene Freigabe entscheidet über Ladeziele.

Dieses Update setzt Variante 3 um. Es ergänzt eine Vollakku-Referenz und liefert
in Pilotkalibrationen einen überprüfbaren Endpunktvorschlag. Die erste Version
dieses neuen Referenzverfahrens beendet Pilotkalibrationen auf Benutzeraktion;
sie erhält keine ungeprüfte automatische Volladebehauptung. Normale Ladungen
schalten weiterhin beim passenden, ausdrücklich freigegebenen Energieziel ab.

## 1. Vollständige Leistungsintegration als eigene Quelle

Eine zusätzliche Auswahl heißt „Leistungsintegration – Pilot“. Der technische
Modus heißt `power_reported`; die bisherigen Modi bleiben eindeutig adressierbar.
Die Auswahl gilt für künftig gestartete Vorgänge und wird im Vorgang eingefroren.
Das Update ändert die eingestellte Quelle nicht stillschweigend.

Für jeden vorhandenen, vorwärts laufenden Beobachtungsabschnitt wird der letzte
endliche, nichtnegative Leistungszustand zeitgewichtet fortgeschrieben:

`E_reported += P_previous * duration_seconds / 3600`

Ein unveränderter Wert darf somit zum Gesamtergebnis beitragen, auch wenn der
letzte Leistungsreport älter als 120 Sekunden ist. Daraus entsteht kein neuer
Gerätereport. Es werden weiterhin getrennt gespeichert und angezeigt:

- integrierte Energie aus allen nutzbaren Beobachtungsabschnitten;
- Teilintegral aus nach den bestehenden Regeln frischen Abschnitten;
- frische, fortgeschriebene und nicht abgedeckte Zeit;
- Dauer des längsten gehaltenen Zustands und Qualität pro Ladeabschnitt;
- Energiezähler als ergänzender Vergleichskanal, sofern verfügbar.

Die Vollintegration trägt bei gehaltenen Anteilen die Kennzeichnung „Schätzung
aus gehaltenen Leistungswerten“. „Vollständig“ beschreibt die Verarbeitung der
vorhandenen Zeitabschnitte, nicht den Nachweis lückenloser physischer Messungen.

Echte Aufzeichnungsunterbrechungen über der bestehenden 120-Sekunden-Grenze,
Zeitumkehr, fehlende/ungültige Leistung und unbeobachtete Neustartintervalle werden
nicht überbrückt. Das Teilergebnis bleibt erhalten, die betroffenen Abschnitte
bleiben unbekannt. Eine durch eine echte Unterbrechung unvollständige Kalibration
ist für automatische Energieziele gesperrt; eine Freigabe darf diese Sperre nicht
aufheben. Der kleine Startbereich bis zur ersten aufgezeichneten Beobachtung
wird separat ausgewiesen und nicht nachträglich als gemessen ergänzt.

Im neuen Modus ist der Leistungswert die operative Energiequelle. Ein stehender,
zurückgesetzter oder nicht verfügbarer diagnostischer Energiezähler erzeugt eine
Kennzeichnung seines Kanals; er blockiert die Leistungsmessung nicht. Verlust des
erforderlichen Leistungssensors oder Schalterzustands führt zur überprüften
Abschaltung. Zeit-, Leistungs- und konfigurierte Temperaturgrenzen gelten in
jedem Modus. Eine laufende Ladung erhält kein neues Ziel durch spätere Änderungen
an Referenzen, Freigaben oder Energiequelleneinstellungen.

Energieziele dürfen ausschließlich aus derselben versionierten Quelle und
Korrekturbasis gebildet werden. Eine alte Zählerkalibration wird nicht als Ziel
einer neuen Leistungsintegration verwendet. Eine explizite Neuauswertung darf
eine neue abgeleitete Ansicht anlegen und benötigt eine neue Freigabe.

Standard des neuen Pilotmodus ist die Bruttointegration (`energy_basis = gross`).
Damit kann ohne erneute Leerlaufmessung aufgezeichnet und später ein passendes
Brutto-Energieziel freigegeben werden. Eine Korrektur mit einer ausdrücklich
gewählten, passenden Leerlaufreferenz ist als separate Basis
`no_load_corrected` verfügbar; Referenz und Korrektur werden im Vorgang
eingefroren. Ein Ziel dieser Basis verlangt die entsprechende Referenz.
Brutto- und korrigierte Ziele dürfen nicht vermischt werden. Die Oberfläche nennt
Bruttoenergie ausdrücklich Bruttoenergie.

## 2. Vollakku-Restverbrauch als eigene Messart

„Restverbrauch mit vollem Akku“ wird getrennt vom bestehenden Leerlauf ohne Akku
geführt. Der Schlüssel besteht aus Setup-ID/Revision, Akku-ID/Revision,
Stückzahl und geordneter Portbelegung. Es handelt sich um eine Referenz des
Akkutyps in dieser Anordnung, nicht um eine automatisch auf alle Akkus und Ports
übertragbare Konstante.

Der Ablauf berücksichtigt das erneute Nachladen nach dem Einschalten:

1. „Vollakku-Referenz vorbereiten“ startet einen archivierten Vorgang und schaltet
   den Aufbau kontrolliert ein. Der Akku bleibt angeschlossen. Aufzeichnung und
   Sicherheitsüberwachung laufen bereits.
2. Ein Hinweis erklärt: Ein Einschalt-Ladeimpuls gehört zur Vorbereitung. Erst
   wenn der Nutzer den vollen Zustand beziehungsweise das Ende dieses Impulses
   am USB-Gerät oder an der Ladeanzeige bestätigt, startet er „Restphase messen“.
3. Dieser Zeitpunkt wird als unveränderliche Auswertungsgrenze gespeichert.
   Die nächsten fünf Minuten werden als Einlaufphase markiert; danach folgen
   standardmäßig 30 Minuten Referenzauswertung.
4. Der Vorgang wird gespeichert und ausgeschaltet. Der Nutzer prüft und gibt
   die Referenz frei. Abbruch erhält die Daten, erzeugt aber keine freigegebene
   Referenz.

Es werden Roh-Bruttoleistung, zeitgewichtete Mittelwerte, drei gleich lange
Zeitblockmittel, zeitgewichtete Verteilung, beobachtete Werteabstufung und die
getrennte Reportqualität gespeichert. Der Median einzelner Ereignisse wird nicht
als Energie- oder Leerlaufmittel verwendet. Die Quellenqualität bleibt auch nach
einer Benutzerfreigabe sichtbar.

Eine Referenz ist technisch auswertbar, wenn ihr Auswertungsfenster vollständig
als Beobachtungsfolge vorhanden ist und keine Unterbrechung, kein Sensorfehler
oder Neustart im Fenster liegt. Frische und gehaltene Anteile werden getrennt
bewertet; ein alter, weiterhin vorhandener Zustandswert wird nicht als fehlender
Archivpunkt behandelt. Eine geschätzte Referenz kann einzeln ausdrücklich für
den Pilotvergleich freigegeben werden, wird dadurch aber nicht zu einer
unabhängig validierten Präzisionsmessung.

Der bestehende Leerlauf ohne Akku bleibt die optionale Korrektur für den
lastunabhängigen Aufbauverbrauch. Bei nahezu null liegendem Ergebnis gibt es
keine Pflicht, wegen kleiner Pulse wiederholt neue Nullmessungen durchzuführen.
Die Auswertung muss Mittelwert, Auflösung und Qualität zeigen. Die neue
Vollakku-Referenz wird **nicht** über die gesamte Ladung hinweg als zusätzlicher
Leerlauf abgezogen; sie dient zur Beschreibung und Erkennung der Restphase.

## 3. Endpunktvorschlag für den nächsten Pilotlauf

Ohne passende freigegebene Vollakku-Referenz kann eine Pilotkalibration messen
und manuell beendet werden. Die Oberfläche zeigt „Ladeende noch nicht
festgelegt“. Mit einer passenden Referenz beobachtet sie den Übergang in einen
ähnlichen Restverbrauchsbereich; dafür ist keine zuvor zu 99 % frisch gemeldete
Hauptlast zwingend erforderlich.

Die erste versionierte Vergleichsregel ist bewusst eine dokumentierte
Pilotregel, kein naturgesetzlicher Volladenachweis:

- Referenzobergrenze: größter Mittelwert der drei Referenzblöcke plus Toleranz.
- Toleranz: größerer Wert aus 0,03 W und der halben kleinsten beobachteten
  positiven Leistungswerteabstufung; bei unbekannter Abstufung werden 0,03 W
  benutzt und der unbekannte Anteil ausgewiesen. Die beobachtete Abstufung ist
  keine behauptete Hersteller-Genauigkeit.
- Eine Referenz mit einer Spanne ihrer Blockmittel über dem Zweifachen dieser
  Toleranz ist als instabil markiert und liefert keinen automatischen Vorschlag.
- Vor einem Kandidaten muss ein fünfminütiges Beobachtungsfenster oberhalb der
  Referenzobergrenze plus Toleranz vorliegen. Nach reinem Start im bereits
  niedrigen Bereich wird keine vorausgegangene Hauptladung erfunden.
- Der Kandidat beginnt mit dem ersten vollständigen Fünf-Minuten-Fenster, dessen
  zeitgewichteter Mittelwert im Referenzbereich liegt. Sobald einschließlich
  dieses ersten Fensters vier aufeinanderfolgende solche Fenster vorliegen,
  ergeben die insgesamt 20 Minuten einen Vorschlag.
- Jeder Block muss als Beobachtungsfolge vollständig vorliegen. Gehaltene Werte
  dürfen zur Pilotregel beitragen; ihr Anteil wird an der Entscheidung gespeichert.
  Eine echte Aufzeichnungslücke verwirft den Kandidaten. Ein neuer Block oberhalb
  der Grenze verwirft ihn ebenfalls. Einzelne Pulse werden über ihre Energie und
  Dauer im Block berücksichtigt und setzen die Prüfung nicht allein durch ihre
  Höhe zurück.
- Das vorgeschlagene Ende wird auf einen tatsächlichen gespeicherten Punkt am
  Anfang des ersten passenden Fensters gelegt. Bestätigungszeit und gewählter
  Messpunkt bleiben getrennt. Die Grenze ist eine Auswertungsentscheidung mit
  begrenzter Zeitauflösung, kein neuer Rohmesswert.

In der Pilotoberfläche lautet das Ergebnis „Restphase passend – Ladeende
prüfen“. Die Aufzeichnung läuft bis „Beenden und prüfen“ weiter. Dabei wird
zuerst überprüft ausgeschaltet. Ein Vorschlag kann übernommen oder ein anderer
gespeicherter Zeitpunkt mit Begründung gewählt werden. Ohne festgelegten
Endpunkt bleibt die Ladedauer unbekannt; sichtbar bleibt die Vorgangsdauer.

Ein erneuter deutlicher Verbrauch vor dem Ende kann einen noch nicht übernommenen
Vorschlag zurücknehmen. Eine bereits gespeicherte Analyse wird bei späterer
Neubewertung versioniert. Eine Referenz aus demselben Lauf darf ihn nicht
rückwirkend als unabhängig automatisch bestätigt ausgeben.

## 4. Eigene Freigabe für Ladeziele

Jede neue Pilotkalibration beginnt mit `usage_approval = pending`. Speicherung,
erfolgreiches Ausschalten, Auswertbarkeit, Endpunktstatus und Freigabe sind
getrennte Felder. Ein „gültig“-Schalter ersetzt die Freigabe nicht.

In der Detailansicht stehen „Für Ladeziele freigeben“ und „Freigabe zurückziehen“.
Die Freigabe enthält Nutzer, Zeitpunkt, Begründung, Analyseversion, Quelle,
Endpunkt und Referenz-IDs. Änderungen an diesen Grundlagen machen eine erneute
Prüfung erforderlich; die alte Entscheidung bleibt historisch erhalten.

Eine Freigabe ist möglich, wenn ein Endpunkt ausgewählt und begründet ist, die
Quelle über den gewählten Abschnitt auswertbar ist, die erforderlichen Referenzen
vorliegen und die Hardwarezuordnung passt. Der Nutzer kann eine auf gehaltenen
Werten beruhende, ansonsten auswertbare Kalibration ausdrücklich als Pilotziel
freigeben. Die Oberfläche nennt dabei den geschätzten Anteil. Echte unbekannte
Energieintervalle, nichtpositive Zielenergie, fehlender Endpunkt oder ein nicht
bestätigtes Ausschalten bleiben technische Sperren.

Ein einzelner freigegebener Lauf reicht für ein als vorläufig gekennzeichnetes
Ziel. Weitere Läufe ergänzen die Auswertung; es gibt keine Drei-Läufe-Sperre.
Historische Datensätze ohne diese neue Entscheidung bekommen den Status
„Prüfung erforderlich“ für zukünftige Ladeziele. Die Migration erfindet keine
Benutzerfreigabe aus früheren Gültigkeits- oder Vertrauensmarkierungen. Bestehende
historische Messwerte und Analysen werden nicht überschrieben. Bereits laufende
Vorgänge behalten ihre eingefrorene Entscheidung.

## 5. Grafik und Referenzvergleich

Die Grafikaufbereitung bestimmt zuerst die gültigen und geschätzten Segmente je
Messkanal. Danach reduziert sie nur innerhalb dieser Segmente. Segmentgrenzen,
Extrema und relevante Zeitmarker bleiben erhalten. Bei zu vielen Segmenten wird
eine zeitbasierte Hüllkurve mit Qualitätsband und nachladbaren Detaildaten
verwendet; ein festes Punktlimit darf keine echten Grenzen löschen.

Leistung und Energie erhalten getrennte, synchronisierte Achsen. Gehaltene Werte
werden als durchgehende, markierte Fortschreibung gezeigt. Wirklich fehlende
Abschnitte bleiben sichtbar begrenzte Lücken. Die Energiezählerdarstellung hat
ihre eigene Qualität und wird nicht von Leistungsreportlücken abgeschnitten.

Die Kalibrationsansicht zeigt Vorgang, gewählten Ladeabschnitt und Restphase
getrennt. Ein optional eingetragener USB-Endstand hat einen zugeordneten Zeitraum
und einen Kommentar; er bleibt eine unabhängige Referenzangabe. Die App nennt
einen Quotienten zwischen Netz- und USB-Anzeige einen Vergleich, keinen bewiesenen
Wirkungsgrad oder Zellladezustand. Es erfolgt keine Skalierung an Nenn-Wh.

## 6. Datenmodell, Schnittstellen und Migration

- `RestMeasurement` als separate Sammlung `rest_measurements`, mit Setup- und
  Akkusnapshot, Stückzahl/Ports, Vorbereitungs-/Bestätigungs-/Auswertungszeiten,
  Trace-ID, Referenzstatistik, Quellenqualität und eigener Freigabehistorie.
- `ChargeSession` erhält einen Modus für die Vollakku-Referenz und die
  eingefrorenen Auswertungs-/Referenzentscheidungen.
- Kalibrationen erhalten die getrennten Endpunkt-/Freigabefelder und den
  optionalen USB-Vergleich; alte Felder werden für kompatible Leser erhalten.
- Der Schema-Stand steigt von 5 auf 6, Integration und Algorithmus auf 0.5.0.
  Rohdatenspeicherung, Trace-IDs und Hash-Ketten bleiben unabhängig von dieser
  Metadatenmigration. Das vollständige Exportformat bleibt additiv lesbar.
- Neue administrativ geschützte Befehle bereiten die Referenz vor, markieren
  ihren Auswertungsbeginn und bearbeiten Freigabe beziehungsweise USB-Vergleich.
  Bestehende Historiendetails, Rohdatenpaginierung und Export werden um die neue
  Messart erweitert. Veraltete Dialoge werden über erwartete Analyse-/Profil-
  Revisionen abgewiesen.

Zuständigkeiten: `metering.py` für Integrale und Quellenqualität;
`energy_policy.py` für Auswahl/operative Quelle; eine separate
`rest_reference.py` für Referenzstatistik und Vergleich; `models.py` und
`persistence.py` für additive Speicherung; `manager.py` für den Vorgangsablauf;
`history.py` für Segmentierung; WebSocket-API, Frontend und Übersetzungen für die
genannten Benutzeraktionen. Der bestehende Manager bekommt keine zweite Kopie
der Integrations- oder Statistiklogik.

## 7. Abnahme und Veröffentlichung

Die Umsetzung muss Folgendes nachweisen:

1. Ein lange gehaltener, endlicher Leistungszustand trägt im neuen Modus zum
   Integral bei und bleibt qualitativ als gehalten markiert. Alte strikte Modi
   behalten ihre definierte Bedeutung. Fehlende Archivintervalle werden nicht
   durch dieselbe Regel ergänzt.
2. Zählerstillstand, Zählerreset und Zählerausfall beeinflussen im neuen Modus
   ausschließlich den Vergleichskanal; erforderliche Sensor-/Schalterfehler
   lösen weiterhin die passende überprüfte Abschaltung aus.
3. Vorbereitungs-Ladeimpulse gelangen nicht in die Vollakku-Referenz.
   Referenzen passen nur zur genauen Profilkombination. Pulslasten werden
   zeitgewichtet; ein Nullmedian ersetzt keinen Mittelwert.
4. Stabile/pulsierende Restphasen, erneute hohe Last, echte Report-/Aufzeichnungslücken,
   fehlende Referenz und unklare Endpunkte haben getrennte Ergebnisse. Die
   Pilotregel beendet eine Messung nicht eigenmächtig.
5. Manuelles Beenden oder Wiederherstellen der Gültigkeit erteilt keine Freigabe.
   Änderungen an freigegebenen Grundlagen erfordern eine neue Entscheidung.
   Normalladungen verwenden die gleiche eingefrorene Rechenbasis wie ihr Ziel.
6. Die bekannten Grafikprobleme werden mit synthetischen Fällen und dem lokal
   vorhandenen Export geprüft. Private Originaldaten gelangen nicht ins Git-Repo.
   Rohdatenanzahl und Hash-Ketten bleiben beim Migrieren und Wiederöffnen gleich.
7. Python-/Frontend-Tests, Python-Kompilierung, JSON- und JavaScript-Syntaxprüfungen
   sowie die vorgesehenen HACS-/hassfest-Prüfungen werden ausgeführt. Falls ein
   externer Prüfer nicht zugänglich ist, wird das konkrete Ergebnis als offen
   dokumentiert, nicht als bestanden ausgegeben.

Der Remote-Stand wurde gelesen: `main` und das letzte Release sind 0.4.2.
Das bestehende Release-Workflow veröffentlicht beim Push einer neuen Version auf
`main` automatisch. Deshalb erfolgen Implementierung und Prüfung zunächst auf
einem Arbeitsbranch im vorhandenen isolierten Checkout; kein zusätzliches
Worktree ist erforderlich. Ein Push auf `main` erfolgt erst mit dem geprüften
Release-Stand. Ein erfolgreicher Git-Lesezugriff ist noch kein Nachweis für
Push- oder GitHub-API-Berechtigungen; diese werden bei Bedarf über die vorhandene
Plattformauthentifizierung geprüft.

## Ablauf für den nächsten einzelnen Pilotlauf

Nach dem Update wählt der Nutzer „Leistungsintegration – Pilot“. Falls ein voller
Akku verfügbar ist, bereitet er zuerst die Vollakku-Referenz vor, wartet einen
eventuellen Einschaltimpuls ab und markiert den Beginn der Restphase. Nach deren
Auswertung kann er die Referenz einzeln freigeben.

Der nächste standardisiert entladene Akku wird wie gewohnt kalibriert. Die App
zeigt das vollständige Integral und seine Qualität; mit Referenz ergänzt sie
einen Restphasen-/Endpunktvorschlag. Der Nutzer beendet und exportiert diesen
einzelnen Lauf. Gemeinsam werden Kurve, USB-Endstand, Endpunkt und Referenz
geprüft; erst anschließend wird die Kalibration als Ladeziel freigegeben.

Nicht Teil dieses Pilot-Updates sind eine behauptete absolute Kalibrierung des
Smart Plugs, Änderungen seiner Firmware, eine genaue Zell-SoC-Messung oder eine
automatisch an Nennenergie angepasste Ladung.
