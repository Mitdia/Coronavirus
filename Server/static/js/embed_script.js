var genes_array = [];
var current_gene = "";
var url_string = window.location.href;
var url = new URL(url_string);
var max_date = url.searchParams.get("max_date");
var min_date = url.searchParams.get("min_date");
var language = url.searchParams.get("lang");
var mutation = url.searchParams.get("mutation");

function add_gene_dropdown(gene, mutation_dropdown, gene_dropdown) {
  var gene_button = document.createElement("div");
  gene_button.className = "w3-bar-item w3-dropdown-click";
  var gene_button_button = document.createElement("button");
  gene_button_button.id = gene;
  gene_button_button.textContent = gene;
  gene_button_button.className = "w3-button";
  gene_button_button.onclick = function() {geneDropdown(this.id)};
  var gene_button_content = document.createElement("div");
  gene_button_content.id = gene + ":";
  gene_button_content.className = "w3-dropdown-content w3-bar-block w3-border";
  gene_button_content.style = "max-height:250px; overflow:auto;"
  gene_button.appendChild(gene_button_button);
  mutation_dropdown.appendChild(gene_button_content);
  gene_dropdown.appendChild(gene_button);
  return gene_button_content
}


function init(mutations) {
  var mutationDropdownButton =  document.getElementById("mutationDropdownButton");
  var geneDropdownButtonText = document.getElementById("geneDropdownButtonText");
  var mutationDropdownButtonText =  document.getElementById("mutationDropdownButtonText");
  var mutationNameDropdownButtonText =  document.getElementById("mutationNameDropdownButtonText");
  var gene_dropdown = document.getElementById("gene");
  var mutation_dropdown = document.getElementById("mutation");


  var mutation_array = mutation.split(':');
  mutationDropdownButton.onclick = function () {geneDropdown(mutation.split(':')[0])};
  geneDropdownButtonText.textContent = mutation_array[0];
  mutationDropdownButtonText.textContent = mutation_array[0] + ':';
  mutationNameDropdownButtonText.textContent = mutation_array[1];

  mutation = mutations[0];
  mutation_array = mutation.split(':');
  var previous_gene = mutation_array[0];
  gene_button_content = add_gene_dropdown(previous_gene, mutation_dropdown, gene_dropdown);

  genes_array.push(previous_gene);

  for (var i = 0; i < mutations.length; i++) {
    mutation = mutations[i];
    mutation_array = mutation.split(':');
    var gene = mutation_array[0];
    var mutation_name = mutation_array[1];
    if (gene != previous_gene)
    {
        genes_array.push(gene);
        var previous_gene = gene;
        gene_button_content = add_gene_dropdown(gene, mutation_dropdown, gene_dropdown);
    }
    var mutation_button = document.createElement("a");
    mutation_button.textContent = mutation_name;
    mutation_button.className = "w3-bar-item w3-button";
    mutation_button.id = mutation;
    mutation_button.onclick = function () {changeupdate(this.id)};
    gene_button_content.appendChild(mutation_button);
  }

  var previous_dropdown = "None";

  mutation = url.searchParams.get("mutation");

  fetch(`/plot?mutation=${mutation}&lang=${language}&max_date=${max_date}&min_date=${min_date}`)
      .then(function(response) { return response.json(); })
      .then(function(item) { return Bokeh.embed.embed_item(item, "coronaplot"); })

  fetch(`/dateRangeSlider?mutation=${mutation}&lang=${language}&max_date=${max_date}&min_date=${min_date}`)
      .then(function(response) { return response.json(); })
      .then(function(item) { return Bokeh.embed.embed_item(item, "dateRangeSlider"); })

}


function switch_lang() {
  if (language == "EN")
  {
    language = "RU";
  }
  else
  {
    language = "EN";
  }
  window.location.href=(`/embed?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
}


function home() {
  window.location.href=(`/embed?mutation=ALL&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
}


function geneDropdown(id) {
  var x = document.getElementById(id + ":");
  current_gene = id;

  var mutationDropdownButton =  document.getElementById("mutationDropdownButton");
  var mutationDropdownButtonText =  document.getElementById("mutationDropdownButtonText");
  var geneDropdownButtonText = document.getElementById("geneDropdownButtonText");
  var mutationNameDropdownButtonText =  document.getElementById("mutationNameDropdownButtonText");

  mutationDropdownButton.onclick = function () {geneDropdown(current_gene)};
  mutationDropdownButtonText.textContent = current_gene + ':';
  geneDropdownButtonText.textContent = current_gene;
  mutationNameDropdownButtonText.textContent = '';

  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
  } else {
    x.className = x.className.replace(" w3-show", "");
  }
  var x = document.getElementById("gene");
  if (x.className.indexOf("w3-show") != -1) {
    x.className = x.className.replace(" w3-show", "");
  }
  for (var i = 0; i < genes_array.length; i++)
  {
    var x = document.getElementById(genes_array[i] + ":");
    if ((x.className.indexOf("w3-show") != -1) && (genes_array[i] != id)) {
      x.className = x.className.replace(" w3-show", "");
    }
  }
}


function mainDropdown() {
  var x = document.getElementById("gene");
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
  } else {
    x.className = x.className.replace(" w3-show", "");
  }
  for (var i = 0; i < genes_array.length; i++)
  {
    var x = document.getElementById(genes_array[i] + ":");
    if (x.className.indexOf("w3-show") != -1) {
      x.className = x.className.replace(" w3-show", "");
    }
  }
}


function changeupdate(new_mutation) {
  var x = document.getElementById("gene");
  if (x.className.indexOf("w3-show") != -1) {
    x.className = x.className.replace(" w3-show", "");
  }
  for (var i = 0; i < genes_array.length; i++)
  {
    var x = document.getElementById(genes_array[i] + ":");
    if (x.className.indexOf("w3-show") != -1) {
      x.className = x.className.replace(" w3-show", "");
    }
  }
  mutation = new_mutation;
  var updateButton = document.getElementById("update");
  var mutationNameDropdownButtonText =  document.getElementById("mutationNameDropdownButtonText");
  updateButton.onclick = function () {window.location.href=(`/embed?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);}
  mutationNameDropdownButtonText.textContent = mutation.split(':')[1];
}


function dateRangeSlider(min_timestamp, max_timestamp) {
  var update = document.getElementById("update");
  min_date = new Date(min_timestamp);
  min_date = min_date.getFullYear() + "-" + (min_date.getMonth() + 1) + "-" + min_date.getDate();
  max_date = new Date(max_timestamp);
  max_date = max_date.getFullYear() + "-" + (max_date.getMonth() + 1) + "-" + max_date.getDate();
  update.onclick = function() {window.location.href=(`/embed?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);};
}


function outbreakInfoLink(outbreak_link) {
  console.log(outbreakInfoLink);
  window.location.href=(outbreak_link);
}
