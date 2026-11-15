"""Genereert microgolf-ux-test.qsf: een Qualtrics-survey (within-subjects, 3 interfaces x 3 taken).

Gebruik:  python maak_qsf.py [stimulus_url]
De stimulus-URL staat ook als Embedded Data-veld `stimulus_url` bovenaan de Survey Flow,
dus je kan hem later in Qualtrics aanpassen zonder opnieuw te importeren.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STIM_URL = sys.argv[1] if len(sys.argv) > 1 else "https://JOUW-GEBRUIKERSNAAM.github.io/magnetron-test/"
SID = "SV_microgolfUX0001"

UIS = ["oud", "standaard", "herontwerp"]
TASKS = ["t1", "t2", "t3"]
RESULT_FIELDS = ["success", "gaveup", "time", "first", "actions", "errors", "resets", "final", "path"]
TASK_LABEL = {
    "t1": "Taak 1: hetelucht 200 °C, 10 minuten",
    "t2": "Taak 2: microgolf 600 W, 2 min 30 s",
    "t3": "Taak 3: grill 15 minuten",
}
ORDERS = [
    ("oud", "standaard", "herontwerp"), ("oud", "herontwerp", "standaard"),
    ("standaard", "oud", "herontwerp"), ("standaard", "herontwerp", "oud"),
    ("herontwerp", "oud", "standaard"), ("herontwerp", "standaard", "oud"),
]

TASK_JS = (HERE / "qualtrics-vraag.js").read_text(encoding="utf-8")

elements = []
blocks = {}
qcount = 0
_fl = [0]


def flow_id():
    _fl[0] += 1
    return f"FL_{_fl[0]}"


def add_q(payload, block):
    global qcount
    qcount += 1
    qid = f"QID{qcount}"
    payload = {
        "QuestionID": qid,
        "DataVisibility": {"Private": False, "Hidden": False},
        "Language": [],
        "Validation": {"Settings": {"Type": "None"}},
        "QuestionDescription": payload.get("QuestionDescription", strip(payload["QuestionText"])[:99]),
        "NextChoiceId": 1,
        "NextAnswerId": 1,
        **payload,
    }
    elements.append({
        "SurveyID": SID, "Element": "SQ", "PrimaryAttribute": qid,
        "SecondaryAttribute": payload["QuestionDescription"], "TertiaryAttribute": None, "Payload": payload,
    })
    blocks[block]["BlockElements"].append({"Type": "Question", "QuestionID": qid})
    return qid


def page_break(block):
    blocks[block]["BlockElements"].append({"Type": "Page Break"})


def strip(html):
    import re
    return re.sub(r"<[^>]+>", " ", html).replace("&nbsp;", " ").strip()


def new_block(bid, desc, default=False):
    blocks[bid] = {"Type": "Default" if default else "Standard", "Description": desc, "ID": bid, "BlockElements": []}


def text_q(block, tag, html, js=None):
    p = {"QuestionText": html, "DataExportTag": tag, "QuestionType": "DB", "Selector": "TB",
         "Configuration": {"QuestionDescriptionOption": "UseText"}, "ChoiceOrder": []}
    if js:
        p["QuestionJS"] = js
    return add_q(p, block)


def mc_q(block, tag, html, options, horizontal=False, force=True):
    choices = {str(i + 1): {"Display": o} for i, o in enumerate(options)}
    return add_q({
        "QuestionText": html, "DataExportTag": tag, "QuestionType": "MC",
        "Selector": "SAHR" if horizontal else "SAVR", "SubSelector": "TX",
        "Configuration": {"QuestionDescriptionOption": "UseText"},
        "Choices": choices, "ChoiceOrder": [str(i + 1) for i in range(len(options))],
        "Validation": {"Settings": {"ForceResponse": "ON" if force else "OFF", "ForceResponseType": "ON", "Type": "None"}},
        "RecodeValues": {str(i + 1): str(i + 1) for i in range(len(options))},
        "NextChoiceId": len(options) + 1,
    }, block)


def te_q(block, tag, html, numeric=False, multiline=False, force=False):
    val = {"Settings": {"ForceResponse": "ON" if force else "OFF", "ForceResponseType": "ON",
                        "Type": "ContentType" if numeric else "None"}}
    if numeric:
        val["Settings"]["ContentType"] = "ValidNumber"
        val["Settings"]["ValidNumber"] = {"Min": "16", "Max": "99", "NumDecimals": "0"}
    return add_q({
        "QuestionText": html, "DataExportTag": tag, "QuestionType": "TE",
        "Selector": "ML" if multiline else "SL",
        "Configuration": {"QuestionDescriptionOption": "UseText", "InputWidth": 120 if numeric else 680},
        "Validation": val, "SearchSource": {"AllowFreeResponse": "false"}, "DefaultChoices": False,
    }, block)


def matrix_q(block, tag, html, statements, scale):
    return add_q({
        "QuestionText": html, "DataExportTag": tag, "QuestionType": "Matrix",
        "Selector": "Likert", "SubSelector": "SingleAnswer",
        "Configuration": {"QuestionDescriptionOption": "UseText", "TextPosition": "inline",
                          "ChoiceColumnWidth": 40, "RepeatHeaders": "none", "WhiteSpace": "OFF", "MobileFirst": True},
        "Choices": {str(i + 1): {"Display": s} for i, s in enumerate(statements)},
        "ChoiceOrder": [str(i + 1) for i in range(len(statements))],
        "Answers": {str(i + 1): {"Display": a} for i, a in enumerate(scale)},
        "AnswerOrder": [str(i + 1) for i in range(len(scale))],
        "RecodeValues": {str(i + 1): str(i + 1) for i in range(len(scale))},
        "Validation": {"Settings": {"ForceResponse": "ON", "ForceResponseType": "ON", "Type": "None"}},
        "ChoiceDataExportTags": False,
        "NextChoiceId": len(statements) + 1, "NextAnswerId": len(scale) + 1,
    }, block)


# ---------------------------------------------------------------- blokken
new_block("BL_introBlok000001", "Intro en toestemming", default=True)
new_block("BL_demografie00001", "Demografie")
for r in (1, 2, 3):
    new_block(f"BL_ronde{r}000000", f"Ronde {r}")
new_block("BL_afsluiting00001", "Afsluiting")
blocks["BL_prullenbak00001"] = {"Type": "Trash", "Description": "Trash / Unused Questions", "ID": "BL_prullenbak00001", "BlockElements": []}

q_consent = None
text_q("BL_introBlok000001", "intro", (
    "<h2>Onderzoek naar bedieningspanelen van microgolfovens</h2>"
    "<p>Bedankt om deel te nemen! In dit onderzoek test je drie verschillende bedieningspanelen van een microgolfoven. "
    "Je krijgt telkens een interactief 3D-model te zien en voert een paar korte taken uit, zoals de microgolf op een "
    "bepaalde temperatuur en tijd zetten. Daarna beantwoord je enkele vragen.</p>"
    "<p>Het onderzoek duurt ongeveer <b>10 minuten</b>. Gebruik bij voorkeur een <b>computer met muis</b>. "
    "We meten hoe lang je over elke taak doet en welke knoppen je gebruikt. Je antwoorden worden anoniem verwerkt "
    "en enkel gebruikt voor een studieopdracht aan UGent. Je kan op elk moment stoppen.</p>"))
q_consent = mc_q("BL_introBlok000001", "toestemming", "Ga je akkoord om deel te nemen aan dit onderzoek?",
                 ["Ja, ik ga akkoord", "Nee, ik wil niet deelnemen"])

te_q("BL_demografie00001", "leeftijd", "Wat is je leeftijd?", numeric=True, force=True)
mc_q("BL_demografie00001", "geslacht", "Wat is je gender?", ["Man", "Vrouw", "Non-binair / anders", "Zeg ik liever niet"])
mc_q("BL_demografie00001", "gebruik_freq", "Hoe vaak gebruik je een microgolfoven?",
     ["Dagelijks", "Wekelijks", "Maandelijks", "Zelden", "Nooit"])
mc_q("BL_demografie00001", "ervaring_combi", "Heb je al eens een combi-microgolf gebruikt (met hetelucht- of grillfunctie)?",
     ["Ja, regelmatig", "Ja, een paar keer", "Nee, nooit", "Weet ik niet"])
mc_q("BL_demografie00001", "type_thuis", "Welk soort bediening heeft de microgolf die je het meest gebruikt?",
     ["Draaiknoppen", "Digitale knoppen met cijfertoetsen", "Touchscreen / aanraakpaneel", "Andere / weet ik niet",
      "Ik gebruik geen microgolf"])

SEQ_SCALE = ["1<br>Zeer moeilijk", "2", "3", "4", "5", "6", "7<br>Zeer makkelijk"]
SUS_ITEMS = [
    "Ik denk dat ik deze microgolf graag regelmatig zou gebruiken.",
    "Ik vond de bediening onnodig complex.",
    "Ik vond de microgolf makkelijk te gebruiken.",
    "Ik denk dat ik hulp van iemand met technische kennis nodig heb om deze microgolf te kunnen gebruiken.",
    "Ik vond dat de verschillende functies van deze microgolf goed op elkaar aansloten.",
    "Ik vond dat er te veel inconsistentie in de bediening zat.",
    "Ik kan me voorstellen dat de meeste mensen zeer snel leren om deze microgolf te gebruiken.",
    "Ik vond de bediening erg omslachtig.",
    "Ik voelde me erg zeker tijdens het gebruik van deze microgolf.",
    "Ik moest veel leren voordat ik met deze microgolf aan de slag kon.",
]
SUS_SCALE = ["Helemaal oneens", "Oneens", "Neutraal", "Eens", "Helemaal eens"]

for r in (1, 2, 3):
    b = f"BL_ronde{r}000000"
    text_q(b, f"r{r}_intro", (
        f"<h2>Ronde {r} van 3</h2>"
        "<p>Je krijgt zo dadelijk een microgolf met een <b>bedieningspaneel</b> te zien. Voer telkens de taak uit die "
        "bovenaan staat en druk op <b>START</b> wanneer je denkt dat alles juist is ingesteld. Je hebt <b>één poging</b> "
        "per taak. Lukt het niet, dan kan je rechtsonder op <i>Lukt niet / overslaan</i> klikken.</p>"
        "<p>Tips: klik op knoppen, draai aan draaiknoppen door te slepen, en sleep naast het toestel om het te draaien.</p>"))
    for t in TASKS:
        page_break(b)
        iframe = (f'<p style="margin:0 0 6px"><b>{TASK_LABEL[t].split(":")[0]}</b></p>'
                  f'<iframe src="${{e://Field/stimulus_url}}?ui=${{e://Field/ui_r{r}}}&amp;task={t}" '
                  'style="width:100%;height:620px;border:0;border-radius:8px" allow="autoplay"></iframe>')
        text_q(b, f"r{r}_{t}_taak", iframe, js=TASK_JS)
        page_break(b)
        mc_q(b, f"r{r}_{t}_seq", "Hoe moeilijk of makkelijk vond je deze taak?", SEQ_SCALE, horizontal=True)
    page_break(b)
    matrix_q(b, f"r{r}_sus",
             "Denk aan de microgolf die je net gebruikt hebt. In hoeverre ben je het eens met de volgende uitspraken?",
             SUS_ITEMS, SUS_SCALE)

mc_q("BL_afsluiting00001", "voorkeur", "Welk bedieningspaneel vond je het prettigst om te gebruiken?",
     ["De microgolf met draaiknoppen", "De microgolf met cijfertoetsen", "De microgolf met grote knoppen en genummerde stappen",
      "Geen voorkeur"])
te_q("BL_afsluiting00001", "waarom", "Waarom? En wat vond je het meest verwarrend aan de andere panelen?", multiline=True)
text_q("BL_afsluiting00001", "bedankt", "<p>Bedankt voor je deelname! Klik op de pijl om je antwoorden te versturen.</p>")

# ---------------------------------------------------------------- survey flow
def ed(fields):
    return {"Type": "EmbeddedData", "FlowID": flow_id(), "EmbeddedData": [
        {"Description": k, "Type": "Custom", "Field": k, "VariableType": "String",
         "DataVisibility": [], "AnalyzeText": False, "Value": v} for k, v in fields]}


declared = [("stimulus_url", STIM_URL), ("volgorde", ""), ("ui_r1", ""), ("ui_r2", ""), ("ui_r3", "")]
for ui in UIS:
    for t in TASKS:
        for f in RESULT_FIELDS:
            declared.append((f"{ui}_{t}_{f}", ""))
# Simple layout bewaart setJSEmbeddedData als __js_<naam>
for ui in UIS:
    for t in TASKS:
        for f in RESULT_FIELDS:
            declared.append((f"__js_{ui}_{t}_{f}", ""))

randomizer = {"Type": "BlockRandomizer", "FlowID": flow_id(), "SubSet": 1, "EvenPresentation": True,
              "Flow": [ed([("volgorde", str(i + 1)), ("ui_r1", o[0]), ("ui_r2", o[1]), ("ui_r3", o[2])])
                       for i, o in enumerate(ORDERS)]}

consent_branch = {
    "Type": "Branch", "FlowID": flow_id(), "Description": "Geen toestemming",
    "BranchLogic": {"0": {"0": {
        "LogicType": "Question", "QuestionID": q_consent, "QuestionIsInLoop": "no",
        "ChoiceLocator": f"q://{q_consent}/SelectableChoice/2", "Operator": "Selected",
        "QuestionIDFromLocator": q_consent, "LeftOperand": f"q://{q_consent}/SelectableChoice/2",
        "Type": "Expression",
        "Description": "<span class=\"ConjDesc\">If</span> toestemming <span class=\"OpDesc\">Is Selected</span> Nee"},
        "Type": "If"}, "Type": "BooleanExpression"},
    "Flow": [{"Type": "EndSurvey", "FlowID": flow_id()}],
}

flow = [ed(declared), randomizer,
        {"Type": "Standard", "ID": "BL_introBlok000001", "FlowID": flow_id(), "Autofill": []},
        consent_branch,
        {"Type": "Block", "ID": "BL_demografie00001", "FlowID": flow_id(), "Autofill": []}]
flow += [{"Type": "Block", "ID": f"BL_ronde{r}000000", "FlowID": flow_id(), "Autofill": []} for r in (1, 2, 3)]
flow += [{"Type": "Block", "ID": "BL_afsluiting00001", "FlowID": flow_id(), "Autofill": []}]

elements.insert(0, {"SurveyID": SID, "Element": "BL", "PrimaryAttribute": "Survey Blocks",
                    "SecondaryAttribute": None, "TertiaryAttribute": None,
                    "Payload": [blocks[k] for k in ["BL_introBlok000001", "BL_prullenbak00001", "BL_demografie00001", "BL_ronde1000000", "BL_ronde2000000", "BL_ronde3000000", "BL_afsluiting00001"]]})
elements.insert(1, {"SurveyID": SID, "Element": "FL", "PrimaryAttribute": "Survey Flow",
                    "SecondaryAttribute": None, "TertiaryAttribute": None,
                    "Payload": {"Type": "Root", "FlowID": "FL_0", "Flow": flow, "Properties": {"Count": _fl[0] + 1}}})
elements.insert(2, {"SurveyID": SID, "Element": "SO", "PrimaryAttribute": "Survey Options",
                    "SecondaryAttribute": None, "TertiaryAttribute": None, "Payload": {
                        "BackButton": "false", "SaveAndContinue": "true", "SurveyProtection": "PublicSurvey",
                        "BallotBoxStuffingPrevention": "false", "NoIndex": "Yes", "SecureResponseFiles": "true",
                        "SurveyExpiration": "None", "SurveyTermination": "DefaultMessage", "Header": "", "Footer": "",
                        "ProgressBarDisplay": "Text", "PartialData": "+1 week", "ValidationMessage": "",
                        "PreviousButton": "", "NextButton": " → ", "SurveyTitle": "Microgolf UX-test",
                        "SurveyMetaDescription": "Onderzoek naar bedieningspanelen van microgolfovens",
                        "PasswordProtection": "No", "AnonymizeResponse": "No", "RefererCheck": "No",
                        "ConfirmStart": False, "AutoConfirmStart": False, "ResponseSummary": "No",
                        "EOSMessage": "", "ShowExportTags": "false", "CollectGeoLocation": "false",
                        "SurveyLanguage": "NL", "AvailableLanguages": {"NL": []}}})
elements.append({"SurveyID": SID, "Element": "QC", "PrimaryAttribute": "Survey Question Count",
                 "SecondaryAttribute": str(qcount), "TertiaryAttribute": None, "Payload": None})
elements.append({"SurveyID": SID, "Element": "RS", "PrimaryAttribute": "RS_microgolfUX0001",
                 "SecondaryAttribute": "Default Response Set", "TertiaryAttribute": None, "Payload": None})

qsf = {
    "SurveyEntry": {
        "SurveyID": SID, "SurveyName": "Microgolf UX-test (AA2)", "SurveyDescription": None,
        "SurveyOwnerID": "UR_placeholder", "SurveyBrandID": "ugent", "DivisionID": None,
        "SurveyLanguage": "NL", "SurveyActiveResponseSet": "RS_microgolfUX0001", "SurveyStatus": "Inactive",
        "SurveyStartDate": "0000-00-00 00:00:00", "SurveyExpirationDate": "0000-00-00 00:00:00",
        "SurveyCreationDate": "2026-11-15 12:00:00", "CreatorID": "UR_placeholder",
        "LastModified": "2026-11-15 12:00:00", "LastAccessed": "0000-00-00 00:00:00",
        "LastActivated": "0000-00-00 00:00:00", "Deleted": None,
    },
    "SurveyElements": elements,
}
out = HERE / "microgolf-ux-test.qsf"
out.write_text(json.dumps(qsf, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{out.name}: {qcount} vragen, {len(declared)} embedded-data-velden, stimulus_url={STIM_URL}")
