# Version 0.1.7 — Startseite, Messhistorie und Revisionsfreigaben

## Startseite und Verwaltung

Die Startseite zeigt laufendes Laden, Kalibrieren oder Leerlaufmessen mit Kurve
und Bedienelementen. Ohne laufenden Vorgang stehen Akkuanzahl als Auswahlknöpfe
und Akkutyp als Dropdown direkt bereit. Ladeanordnung und relative Ladeenergie
werden kompakt angezeigt; „Ändern“ klappt ihre Eingaben auf. Nach einer Auswahl
werden Kalibrationswert und Ladebereitschaft sofort aktualisiert. Die Auswahl
bleibt wie bisher in der Integration gespeichert.

„Kalibrieren“ ist auf der Startseite aufklappbar. Der Zustand bleibt pro
Browser/App-Gerät und HA-Benutzer gespeichert; auf einem neuen Gerät ist der
Bereich geschlossen. Bei gesperrtem Browserspeicher bleibt er für die aktuelle
Ansicht bedienbar. Eine laufende Kalibration bleibt auch bei eingeklapptem
Startbereich sichtbar. Das Auf- oder Zuklappen löst keine Messaktion aus.

„Verwaltung“ bündelt Akkutypen, Ladeanordnungen, Leerlaufmessungen, Kalibrationen
mit Historie und Einstellungen. Unterseiten bieten den Rückweg zu Verwaltung
und Startseite. Ein laufender Vorgang bleibt dort als direkter Rücksprung
sichtbar. Erfolgreich gestartete Messungen öffnen die Startseite; bei Fehlern
bleibt das Formular mit Fehlermeldung erhalten. Links oben öffnet der native
HA-Menüknopf die Home-Assistant-Seitenleiste.

## Status und Verwendung

Leerlaufmessungen und Kalibrationen zeigen getrennt:

- **Gültigkeit:** gültig ist grün, ungültig ist rot. Geringes Vertrauen macht eine gültige Messung nicht ungültig.
- **Ursprung:** die tatsächlich gemessene Setup- und gegebenenfalls Batterie-Revision.
- **Verwendung:** ob die Messung aktuell in die Berechnung eingeht, samt Ausschlussgrund. Beispielsweise historische Revision, ausstehende Leerlaufkorrektur, ungültige Referenz oder vorhandene Messungen mit höherem Vertrauen.

Die Historie gehört zum gewählten Setup beziehungsweise Setup/Batterie/Anzahl-Profil. Filter und „Weitere anzeigen“ ermöglichen auch den Zugriff auf ältere Einträge; Kurven werden erst beim Öffnen der Details geladen.

## Aktionen und ihre Folgen

| Aktion | Wirkung |
| --- | --- |
| Als ungültig markieren | Schließt die Messung aus Berechnungen aus. Bei Leerlaufmessungen werden auch darauf beruhende Kalibrationen ausgeschlossen. Die Messdaten bleiben erhalten. |
| Gültigkeit wiederherstellen | Hebt die Ungültigkeit auf. Revisions- und Qualitätsregeln gelten weiterhin; eine alte Messung wird dadurch nicht automatisch für die aktuelle Revision freigegeben. |
| Für aktuelle Revision freigeben | Erlaubt eine alte Messung ausdrücklich für die geprüfte aktuelle Setup-Revision beziehungsweise das Setup/Batterie-Revisionspaar. Grund und Bestätigung gleichwertiger Bedingungen sind erforderlich. |
| Freigabe widerrufen | Entfernt diese Revisionsfreigabe. Andere Freigaben und die globale Gültigkeit bleiben bestehen. Bereits berechnete Kalibrationen werden dadurch nicht nachträglich verändert. |
| Leerlaufkorrektur neu berechnen | Berechnet eine geeignete Kalibration anhand ihrer gespeicherten Kurve mit der aktuellen brauchbaren Leerlaufbasis neu. Frühere Ergebnisse bleiben in der Analysehistorie erhalten. |

Die Freigabe passt zu rein formellen Änderungen, wenn der physische Aufbau und die Messbedingungen tatsächlich gleich geblieben sind. Der Dialog stellt die alten und aktuellen Angaben gegenüber. Er ändert weder Ursprungsrevisionen noch Batterieanzahl oder ursprüngliche Portbelegung. Eine weitere Revision erfordert eine neue Freigabe.

Alle Änderungen an Messungen erfordern Administratorrechte und sind während eines laufenden Vorgangs gesperrt. Geprüfte Revisionsnummern verhindern eine Freigabe für einen inzwischen geänderten Stand. Entscheidungen werden mit Zeitpunkt, Benutzer-ID und Grund gespeichert; der Grund ist bei Gültigkeitsänderungen optional.

## Details und Kurven

Details stehen allen angemeldeten Benutzern offen. Sie zeigen Messwerte, ursprüngliche und aktuelle Revisionen, Unterschiede, Zeitpunkte, Vertrauen, Messverfahren, Quellmessungen und Entscheidungsverlauf. Historische Leistungs- und Energiekurven lassen sich über einen Messpunktregler untersuchen. Die Anzeige reduziert lange Kurven auf höchstens 600 Punkte und erhält Anfang, Ende und Extremwerte je Abschnitt; gespeicherte Messdaten bleiben vollständig erhalten.

Bei noch ausstehender Leerlaufkorrektur wird Bruttoenergie angezeigt und Nettoenergie ausdrücklich als ausstehend gekennzeichnet. Ohne gespeicherte Kurve erscheint ein entsprechender Hinweis. Eine nachträglich neu berechnete Kalibration übernimmt hohes Vertrauen nur, wenn die neue Auswertung den Endpunkt bestätigt.

## Messqualität und Betrieb

Zuverlässige Messwerte unterhalb der Nachweisgrenze werden nicht als gemessene Nullwerte mit präziseren Leerlaufmessungen vermischt. Sind nur solche Grenzwertmessungen vorhanden, verwendet die Korrektur Null als ausdrücklich ausgewiesene Untergrenze. Widersprüchliche Leerlaufmessungen liefern keine brauchbare Korrektur. Normales Laden verlangt deshalb sowohl eine verwendbare Kalibration als auch eine brauchbare Leerlaufbasis. Eine neue Kalibration kann weiterhin ohne Leerlaufbasis aufgenommen und später automatisch korrigiert werden.

Fehlende Einschaltbestätigung und ein unklarer Schalterzustand nach Neustart lösen einen bestätigten Ausschaltversuch aus. Rückwärts laufende Energiezähler führen zum Abbruch. Sensorereignisse werden weiterhin einzeln ausgewertet; laufende Messdaten werden höchstens einmal pro 30 Sekunden gespeichert, außerdem unmittelbar bei Start, Abschluss, Abbruch, Änderungen und geordnetem Herunterfahren.

## Kompatibilität und Prüfung

Vorhandene Daten bleiben lesbar. Neue Freigabe- und Gültigkeitsverläufe beginnen bei alten Datensätzen leer. Historische Revisionen werden beim Update nicht automatisch freigegeben. Diese Version benötigt keine zusätzlichen Laufzeitabhängigkeiten.

Die automatisierten Tests decken Revisionszuordnung, Freigabe/Widerruf, Gültigkeit und abhängige Kalibrationen, Kurvenbegrenzung, erneute Auswertung, API-Argumente und Fehler, Dialogzustände, Schaltfehler, Neustart, Energiezählerrücklauf und Speicherung ab. Die UI-Tests prüfen außerdem Navigation, sichtbare und aufklappbare Eingaben, lokale Zustandsspeicherung samt Speicherfehlern, laufende Vorgänge auf der Startseite, Auswahlaktualisierung und erfolgreiche/fehlgeschlagene Starts.

Die Tests verwenden ein simuliertes Home-Assistant-Umfeld und DOM-Stubs; WebSocket-Transport, Schema-Validierung, das tatsächliche Öffnen der HA-Seitenleiste und responsive Darstellung benötigen die echte HA-Laufzeit beziehungsweise einen Browser. Eine Prüfung an echter Hardware und eine visuelle Browserprüfung konnten in dieser Arbeitsumgebung nicht durchgeführt werden.
