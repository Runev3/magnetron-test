/* =====================================================================
   Qualtrics – JavaScript voor één taakvraag met het 3D-microgolf-iframe
   Plak dit via: vraag > tandwiel/"JavaScript toevoegen".
   - Verbergt de Volgende-knop tot de taak afgerond of overgeslagen is.
   - Slaat de resultaten op in Embedded Data, per model en per taak:
       model1_taak1_juist, model1_taak1_seconden, model1_taak1_kliks, ...
     (model1 = draaiknoppen, model2 = cijfertoetsen, model3 = herontwerp)
   De deelnemer ziet of vult hier niets van in.
   BELANGRIJK: declareer de Embedded Data-velden bovenaan in je Survey Flow
   (zie README), anders bewaart Qualtrics ze niet.
   ===================================================================== */
Qualtrics.SurveyEngine.addOnload(function () {
  var q = this;
  q.hideNextButton();

  function save(name, value) {
    // Klassieke/flat layouts: setEmbeddedData. Nieuwe "Simple layout": enkel setJSEmbeddedData
    // (die bewaart als "__js_" + naam; declareer dan __js_<veld> in de Survey Flow).
    if (Qualtrics.SurveyEngine.setEmbeddedData) {
      Qualtrics.SurveyEngine.setEmbeddedData(name, value);
    } else if (Qualtrics.SurveyEngine.setJSEmbeddedData) {
      Qualtrics.SurveyEngine.setJSEmbeddedData(name, value);
    }
  }

  function onMessage(e) {
    var d = e.data;
    if (!d || d.source !== 'magnetron-test') return;
    var p = d.id + '_';                                  // bv. "model1_taak1_"
    save(p + 'juist', d.success);                        // 1 = juist uitgevoerd, 0 = fout of overgeslagen
    save(p + 'seconden', Math.round(d.timeMs / 100) / 10); // tijd van "Begin taak" tot START/overslaan
    save(p + 'kliks', d.actions);                        // aantal knopdrukken / knopdraaiingen
    save(p + 'fouten', d.errors);                        // START geweigerd + ongeldige acties
    save(p + 'opgegeven', d.gaveUp);                     // 1 = "Lukt niet / overslaan"
    save(p + 'klikvolgorde', d.path);                    // welke knoppen, in volgorde (voor foutanalyse)
    q.showNextButton();
  }

  window.addEventListener('message', onMessage);
  Qualtrics.SurveyEngine.addOnUnload(function () {
    window.removeEventListener('message', onMessage);
  });
});
