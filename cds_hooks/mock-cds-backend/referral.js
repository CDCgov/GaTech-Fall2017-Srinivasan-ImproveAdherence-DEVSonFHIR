// This file has been modified from the original
// file, patient.js

var isArray = require('util').isArray
var getIn = require('./utils').getIn
var paramsToJson = require('./utils').paramsToJson
var context = require('./context')
var fs = require('fs')
var metadata = require('./utils').metadata
var request = require('sync-request');

module.exports = {
  service: function(indata, cb) {
    cb(null, recommend(indata));
  },
  view: null,
  description: {
    id: "patient-referral",
    name: "Patient referral", // Remove on complete transition to CDS Hooks 1.0 Spec
    title: "Patient referral",
    description: "Refer patient to program",
    hook: "patient-view",
    prefetch: {
      patientToRefer: "Patient/{{Patient.id}}"

    }
  }
}

function recommend(data) {
  var patient = data.prefetch.patientToRefer.resource;
  var name = patient.name[0].given[0];
  var patient_id = patient.id;
  var service_response = "Patient does not meets criteria for referral";
  var res = request('GET', process.env.LPHD_URL + '/referrals/user/user_id=' + patient_id);
  var user_data = JSON.parse(res.getBody('utf8'));
  return cds_cards(name, user_data, patient_id);
}

function cds_cards(name, res, patient_id) {
  console.log("res.results is " + res);
  cards = []
  if (res != null && 'results' in res) {
    Object.keys(res.results).forEach(function(key) {
      var has_referral = res.results[key]
      if (has_referral) {
          var diagnosis = key.replace(/\s+/g, '-').toLowerCase();
          var referral_url = process.env.LPHD_URL + '/patient?user_id=' + patient_id + '&conditions=' + diagnosis
          cards.push({
                    summary: "Patient meets criteria for " + key.replace(/_+/g, ' ') + " referral" ,
                    links: [{
                        "label": "Click here to Launch e-referral app",
                         "type": "absolute",
                         "url": referral_url
                    }],
                    source: {label: "Patient referral service"},
                    indicator: "info"
        })
      }
    });
  }
  return {'cards' : cards}
}
