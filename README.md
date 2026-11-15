# Microgolf UX-test – 3D-stimulus voor Application Assignment 2

Eén interactief 3D-model van een microgolf (three.js) met **drie bedieningspanelen**.
De behuizing, deur, camera en taken zijn identiek. **Alleen het paneel verschilt**,
zodat verschillen in de resultaten aan de interface toe te schrijven zijn.

| Bestand | Wat |
|---|---|
| `index.html` | De stimulus (alles in één bestand, laadt three.js r128 van cdnjs) |
| `qualtrics-vraag.js` | JavaScript om in elke Qualtrics-taakvraag te plakken |
| `qualtrics-demo.html` | Lokale simulatie van een Qualtrics-vraag (toont de doorgestuurde data) |

## De drie interfaces

| `ui=` | Interface | Kenmerken (affordances) |
|---|---|---|
| `oud` | Mechanische draaiknoppen | 3 knoppen: functie (UIT/MICRO/GRILL/HETELUCHT), **dubbele schaal** W én °C op één knop, niet-lineaire timer (0–5 min per 30 s, daarna per minuut) + START. Geen display. |
| `standaard` | Typisch digitaal membraanpaneel | Vlakke grijze knoppen met kleine labels, numeriek klavier. Vermogen/temperatuur kies je door de functieknop **herhaaldelijk** in te drukken (900→800→600 W… / 160→180→200 °C…), tijd typ je in (`1 0 0 0` = 10:00). START zonder iets = snelstart 30 s. |
| `herontwerp` | Herontwerp | Grote reliëfknoppen met iconen + LED, genummerde stappen (1 Functie → 2 Instelling → 3 Tijd → 4 Start), display met feedforward (actieve stap gemarkeerd, “stel tijd in ↓”), aparte −/+ per instelling (vasthouden = herhalen), tijdknoppen +10 min / +1 min / +30 sec, START wordt pas groen en pulseert als alles klaar is. |

### Taken (`task=`)

| id | Taak | Minimaal aantal acties: oud / standaard / herontwerp |
|---|---|---|
| `t1` | Hetelucht 200 °C, 10 min, start | 4 / 8 / 5 |
| `t2` | Microgolf 600 W, 2 min 30 s, start | 4 / 7 / 6 |
| `t3` | Grill 15 min, start | 3 / 6 / 8 |

(Bij `oud` telt één keer een knop vastnemen en draaien als één actie.)
Met het minimale aantal kan je een **efficiëntiescore** berekenen: `acties / minimum`.

Eigen taak: `?ui=oud&task=t4&mode=oven&temp=180&time=300&text=Stel...` (`mode` = `micro|oven|grill`, `power` in W, `temp` in °C, `time` in seconden).

### Andere URL-parameters
- `debug=1`: toont een paneel met de live toestand en het resultaat
- `sound=0`: geen piepjes
- `hud=0`: verbergt de taakbalk bovenaan (als de taak al in de Qualtrics-vraagtekst staat)
- `id=...`: eigen prefix voor de Embedded Data (standaard `<ui>_<taak>`, bv. `oud_t2`)
- `tol=10`: toegestane tijdafwijking in seconden (standaard 0 = exact)
- zonder parameters: keuzemenu om alles te previewen

## Wat er gemeten wordt (per taak)

De tijd start wanneer de deelnemer op **“Begin taak”** klikt. Bij de eerste druk op START
waarbij het toestel effectief begint te werken (of bij “Lukt niet / overslaan”) wordt het
resultaat verstuurd en is de taak afgesloten. Er is dus één poging per taak.

| Veld | Betekenis |
|---|---|
| `success` | 1 = functie + temperatuur/vermogen + tijd exact juist, 0 = fout of overgeslagen |
| `gaveup` | 1 = overgeslagen |
| `time` | taakduur in ms |
| `first` | ms tot de eerste actie (oriëntatietijd) |
| `actions` | aantal acties (knopdrukken, knopdraaiingen) |
| `errors` | START gedrukt terwijl het toestel niet kon starten + ongeldige acties |
| `resets` | STOP/wissen gebruikt terwijl er iets ingesteld was |
| `final` | eindtoestand `mode|waarde|tijd(s)`, bv. `oven|200|600` |
| `path` | volledige klikvolgorde, bv. `m_oven plus plus t10m start` (handig voor foutanalyse) |

## 1. Online zetten (nodig voor Qualtrics)

Qualtrics kan alleen een **https-URL** embedden. De eenvoudigste gratis optie is GitHub Pages:
1. Maak een publieke repository op GitHub (bv. `magnetron-test`).
2. Upload `index.html` (en eventueel de andere bestanden).
3. Ga naar *Settings → Pages → Branch: main / root → Save*.
4. Na ±1 minuut staat de stimulus op `https://<gebruikersnaam>.github.io/magnetron-test/`.

Test de link eerst in je browser, bv. `.../?ui=oud&task=t1&debug=1`.

## 2. Taakvraag in Qualtrics

1. Maak een vraag van het type **Text / Graphic**.
2. Klik in de vraagtekst op **HTML View** en plak:
   ```html
   <iframe src="https://<gebruikersnaam>.github.io/magnetron-test/?ui=${e://Field/ui_r1}&task=t1&hud=1"
           style="width:100%;height:620px;border:0;border-radius:8px" allow="autoplay"></iframe>
   ```
3. Vraag → **JavaScript toevoegen** → plak de inhoud van `qualtrics-vraag.js`.
   De Volgende-knop verschijnt pas wanneer de taak afgerond of overgeslagen is.
4. Kies onder *Look & Feel* een layout met voldoende breedte (Flat/Modern/Classic) en zet
   *Survey options → Allow mobile* bij voorkeur uit: de 3D-test is bedoeld voor desktop.

## 3. Survey Flow (within-subjects, gecounterbalanced)

```
Embedded Data   ← alle velden declareren (zie lijst hieronder) + ui_r1, ui_r2, ui_r3, volgorde
Randomizer (1 element, "Evenly Present Elements" aan)
   ├─ Embedded Data: volgorde=1 ui_r1=oud        ui_r2=standaard  ui_r3=herontwerp
   ├─ Embedded Data: volgorde=2 ui_r1=oud        ui_r2=herontwerp ui_r3=standaard
   ├─ Embedded Data: volgorde=3 ui_r1=standaard  ui_r2=oud        ui_r3=herontwerp
   ├─ Embedded Data: volgorde=4 ui_r1=standaard  ui_r2=herontwerp ui_r3=oud
   ├─ Embedded Data: volgorde=5 ui_r1=herontwerp ui_r2=oud        ui_r3=standaard
   └─ Embedded Data: volgorde=6 ui_r1=herontwerp ui_r2=standaard  ui_r3=oud
Block: Intro + toestemming + demografie (+ ervaring met microgolven)
Block: Ronde 1  → t1, t2, t3 met ${e://Field/ui_r1}, telkens gevolgd door SEQ; daarna SUS of UMUX-Lite
Block: Ronde 2  → idem met ${e://Field/ui_r2}
Block: Ronde 3  → idem met ${e://Field/ui_r3}
Block: Voorkeur + open vraag
```

Omdat het `id` automatisch `<ui>_<taak>` is, landen de resultaten altijd in dezelfde kolommen
(`oud_t1_time`, `herontwerp_t2_success`, ...), ongeacht de volgorde. Het veld `volgorde` gebruik
je als controlevariabele.

### Te declareren Embedded Data-velden

Minimum (4 per combinatie):
```
oud_t1_success oud_t1_time oud_t1_actions oud_t1_errors
oud_t2_success oud_t2_time oud_t2_actions oud_t2_errors
oud_t3_success oud_t3_time oud_t3_actions oud_t3_errors
standaard_t1_success standaard_t1_time standaard_t1_actions standaard_t1_errors
standaard_t2_success standaard_t2_time standaard_t2_actions standaard_t2_errors
standaard_t3_success standaard_t3_time standaard_t3_actions standaard_t3_errors
herontwerp_t1_success herontwerp_t1_time herontwerp_t1_actions herontwerp_t1_errors
herontwerp_t2_success herontwerp_t2_time herontwerp_t2_actions herontwerp_t2_errors
herontwerp_t3_success herontwerp_t3_time herontwerp_t3_actions herontwerp_t3_errors
```
Optioneel per combinatie: `_gaveup _first _resets _final _path`.

> Gebruik je de nieuwe **Simple layout**? Dan werkt alleen `setJSEmbeddedData`, en heten de
> velden `__js_oud_t1_success` enz. Declareer die namen dan in de Survey Flow.

## Methodologische aandachtspunten (voor je verslag/reflectie)

- **Within-design**: meer power met weinig deelnemers, maar met **leereffecten**, want dezelfde
  taken komen 3× terug. Dat vang je op met de 6 volgordes hierboven (volledig gecounterbalanced).
  Alternatief: equivalente maar verschillende taken per ronde, of een between-design (1 interface per persoon).
- Bij een gepaarde vergelijking (bv. herontwerp vs. standaard) moet het **verschil** normaal
  verdeeld zijn. Taaktijden zijn meestal scheef verdeeld: log-transformeer of gebruik Wilcoxon/Friedman.
- Met 3 condities: repeated-measures ANOVA / Friedman + post-hoc met correctie;
  voor `success` (0/1): Cochran’s Q of McNemar per paar.
- Het herontwerp gebruikt standaardwaarden (180 °C, 800 W). Benoem dat als ontwerpkeuze, want
  het beïnvloedt het minimale aantal acties.
- Zet in Qualtrics de **previewantwoorden** uit je data voor je analyseert.
