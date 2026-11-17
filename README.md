# Microgolf UX-test – 3D-stimulus voor Application Assignment 2

**Live:** https://runev3.github.io/magnetron-test/ (zonder parameters = keuzemenu,
bv. `?ui=herontwerp&task=t1&debug=1`). Wijzigingen die naar `main` gepusht worden, staan binnen een minuut online.

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
- `id=...`: eigen prefix voor de Embedded Data (standaard `<model>_<taak>`, bv. `model1_taak2`)
- `tol=10`: toegestane tijdafwijking in seconden (standaard 0 = exact)
- zonder parameters: keuzemenu om alles te previewen

## Wat er gemeten wordt (per taak)

De tijd start wanneer de deelnemer op **“Begin taak”** klikt. Bij de eerste druk op START
waarbij het toestel effectief begint te werken (of bij “Lukt niet / overslaan”) wordt het
resultaat verstuurd en is de taak afgesloten. Er is dus één poging per taak.

| Veld | Betekenis |
|---|---|
| `juist` | 1 = functie + temperatuur/vermogen + tijd exact juist, 0 = fout of overgeslagen |
| `seconden` | taakduur in seconden (1 decimaal) |
| `kliks` | aantal acties (knopdrukken, knopdraaiingen) |
| `fouten` | START gedrukt terwijl het toestel niet kon starten + ongeldige acties |
| `opgegeven` | 1 = "Lukt niet / overslaan" gebruikt |
| `klikvolgorde` | volledige klikvolgorde, bv. `m_oven plus plus t10m start` (handig voor foutanalyse) |

De deelnemer vult hier niets van in: het wordt op de achtergrond gemeten en als Embedded Data
opgeslagen. In de export heten de kolommen **`<model>_<taak>_<veld>`**, met een vaste naam per interface:

| Model | Interface |
|---|---|
| `model1` | `oud` (draaiknoppen) |
| `model2` | `standaard` (cijfertoetsen) |
| `model3` | `herontwerp` |

Bv. `model1_taak1_kliks`, `model2_taak3_seconden`, `model3_taak2_juist`. Ook de vragen heten zo
(`model1_taak1_seq`, `model1_sus_1` … `model1_sus_10`), en `model1_ronde` zegt in welke ronde (1–3)
die persoon model 1 zag.

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
   <iframe src="https://<gebruikersnaam>.github.io/magnetron-test/?ui=oud&task=t1&id=model1_taak1"
           style="width:100%;height:620px;border:0;border-radius:8px" allow="autoplay"></iframe>
   ```
3. Vraag → **JavaScript toevoegen** → plak de inhoud van `qualtrics-vraag.js`.
   De Volgende-knop verschijnt pas wanneer de taak afgerond of overgeslagen is.
4. Kies onder *Look & Feel* een layout met voldoende breedte (Flat/Modern/Classic) en zet
   *Survey options → Allow mobile* bij voorkeur uit: de 3D-test is bedoeld voor desktop.

## 3. Survey Flow (within-subjects, gecounterbalanced)

`microgolf-ux-test.qsf` (gemaakt met `python maak_qsf.py <stimulus_url>`) bevat dit al:

```
Embedded Data   ← alle velden declareren (zie lijst hieronder)
Randomizer (1 van 6, "Evenly Present Elements" aan)
   ├─ Embedded Data: volgorde=1 ui_r1=oud        ui_r2=standaard  ui_r3=herontwerp  (+ model1_ronde=1 …)
   ├─ Embedded Data: volgorde=2 ui_r1=oud        ui_r2=herontwerp ui_r3=standaard
   ├─ Embedded Data: volgorde=3 ui_r1=standaard  ui_r2=oud        ui_r3=herontwerp
   ├─ Embedded Data: volgorde=4 ui_r1=standaard  ui_r2=herontwerp ui_r3=oud
   ├─ Embedded Data: volgorde=5 ui_r1=herontwerp ui_r2=oud        ui_r3=standaard
   └─ Embedded Data: volgorde=6 ui_r1=herontwerp ui_r2=standaard  ui_r3=oud
Block: Intro + toestemming, Block: demografie
Ronde 1: Branch ui_r1 = oud → Block Model1 | = standaard → Block Model2 | = herontwerp → Block Model3
Ronde 2: idem met ui_r2
Ronde 3: idem met ui_r3
Block: Voorkeur + open vraag
```

Elk modelblok bevat t1, t2, t3 (telkens gevolgd door SEQ) en daarna de SUS. Elke deelnemer ziet
de drie modellen dus in een **willekeurige volgorde** (6 volgordes, evenwichtig verdeeld), maar
de resultaten landen altijd in dezelfde kolommen (`model1_…`, `model2_…`, `model3_…`). `volgorde`
en `model1_ronde` … `model3_ronde` gebruik je als controlevariabelen.

### Te declareren Embedded Data-velden

```
stimulus_url volgorde model1_ronde model2_ronde model3_ronde
model1_taak1_juist model1_taak1_seconden model1_taak1_kliks model1_taak1_fouten model1_taak1_opgegeven
… idem voor model1–3 × taak1–3 …
model1_taak1_klikvolgorde … model3_taak3_klikvolgorde
ui_r1 ui_r2 ui_r3
```
De volgorde waarin je ze declareert, is de volgorde van de kolommen in de export.

> Gebruik je de nieuwe **Simple layout**? Dan werkt alleen `setJSEmbeddedData`, en heten de
> velden `__js_model1_taak1_juist` enz. Declareer die namen dan in de Survey Flow.

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
