/* =====================================================================
   Qualtrics – JavaScript voor één taakvraag met het 3D-microgolf-iframe
   Plak dit via: vraag > tandwiel/"JavaScript toevoegen".
   - Verbergt de Volgende-knop tot de taak afgerond of overgeslagen is.
   - Slaat de resultaten op in Embedded Data met als prefix het id
     (standaard  <ui>_<taak>, bv. herontwerp_t1_success).
   BELANGRIJK: declareer de Embedded Data-velden bovenaan in je Survey Flow
   (zie README), anders bewaart Qualtrics ze niet.
   ===================================================================== */
Qualtrics.SurveyEngine.addOnload(function () {
  var q = this;
  q.hideNextButton();

  function save(name, value) {
    // Klassieke/flat layouts: setEmbeddedData. Nieuwe "Simple layout": setJSEmbeddedData
    // (die bewaart als "__js_" + name; declareer dan __js_<veld> in de Survey Flow).
    if (Qualtrics.SurveyEngine.setEmbeddedData) {
      Qualtrics.SurveyEngine.setEmbeddedData(name, value);
    }
    if (Qualtrics.SurveyEngine.setJSEmbeddedData) {
      Qualtrics.SurveyEngine.setJSEmbeddedData(name, value);
    }
  }

  function onMessage(e) {
    var d = e.data;
    if (!d || d.source !== 'magnetron-test') return;
    var p = d.id + '_';
    save(p + 'success', d.success);        // 1 = juist, 0 = fout/overgeslagen
    save(p + 'gaveup', d.gaveUp);          // 1 = overgeslagen
    save(p + 'time', d.timeMs);            // ms van "Begin taak" tot START/overslaan
    save(p + 'first', d.firstActionMs);    // ms tot eerste actie
    save(p + 'actions', d.actions);        // aantal knopdrukken / knopdraaiingen
    save(p + 'errors', d.errors);          // START geweigerd + ongeldige acties
    save(p + 'resets', d.resets);          // STOP/wissen gebruikt
    save(p + 'final', d.finalMode + '|' + d.finalValue + '|' + d.finalTime);
    save(p + 'path', d.path);              // volledige klikvolgorde
    q.showNextButton();
  }

  window.addEventListener('message', onMessage);
  Qualtrics.SurveyEngine.addOnUnload(function () {
    window.removeEventListener('message', onMessage);
  });
});
