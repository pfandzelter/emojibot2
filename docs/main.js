"use strict";

let inputTextArea = $("#in");
let edb = null;

fetch("edb.prebuilt.json")
  .then((resp) => resp.json())
  .then((data) => {
    edb = data;
  });

function stripWord(word) {
  let validChars =
    "abcdefghijklmnopqrstuvwxyzäöüß1234567890_-ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  return word
    .split("")
    .filter((c) => validChars.includes(c))
    .join("")
    .toLowerCase();
}

function emojify(text, len_probabilities = [1, 1, 1, 1, 2, 2, 3]) {
  return text
    .split(/\n/g)
    .map((line) => emojifyLine(line))
    .join("\n");
}

// 1 to 1 translation of emojifier.EDB.emojify
function emojifyLine(text, len_probabilities = [1, 1, 1, 1, 2, 2, 3]) {
  let emojified = "";
  for (let word of text.split(/ /g)) {
    if (edb[stripWord(word)]) {
      let emoji_string = "";
      for (let i of _.range(_.sample(len_probabilities))) {
        emoji_string += _.sample(edb[stripWord(word)]);
      }
      emojified += word + emoji_string + " ";
    } else {
      emojified += word + " ";
    }
  }

  return emojified;
}

inputTextArea.on("input", (event) => {
  $("#out").val(emojify(event.target.value));
});
