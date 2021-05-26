var genes_array = [];
var current_gene = "";

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
  var gene_dropdown = document.getElementById("gene");
  var mutation_dropdown = document.getElementById("mutation");
  var url_string = window.location.href;
  var url = new URL(url_string);
  var language = url.searchParams.get("lang");
  var max_date = url.searchParams.get("max_date");
  var min_date = url.searchParams.get("min_date");
  var mutation = url.searchParams.get("mutation");
  mutationDropdownButton.onclick = function () {geneDropdown(mutation.split(':')[0])};
  var mutation = mutations[0];
  var mutation_array = mutation.split(':');
  var previous_gene = mutation_array[0];
  gene_button_content = add_gene_dropdown(previous_gene, mutation_dropdown, gene_dropdown);
  genes_array.push(previous_gene);
  for (var i = 0; i < mutations.length; i++) {
    var mutation = mutations[i];
    var mutation_array = mutation.split(':');
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
    mutation_button.onclick = function () {changeUpdateMutation(this.id)};
    gene_button_content.appendChild(mutation_button);
  }

  var previous_dropdown = "None";

  var mutation = url.searchParams.get("mutation");

  fetch(`/plot?mutation=${mutation}&lang=${language}&max_date=${max_date}&min_date=${min_date}`)
      .then(function(response) { return response.json(); })
      .then(function(item) { return Bokeh.embed.embed_item(item, "coronaplot"); })

  fetch(`/dateRangeSlider?mutation=${mutation}&lang=${language}&max_date=${max_date}&min_date=${min_date}`)
      .then(function(response) { return response.json(); })
      .then(function(item) { return Bokeh.embed.embed_item(item, "dateRangeSlider"); })

}


function switch_lang() {
  var url_string = window.location.href;
  var url = new URL(url_string);
  var mutation = url.searchParams.get("mutation");
  var language = url.searchParams.get("lang");
  var max_date = url.searchParams.get("max_date");
  var min_date = url.searchParams.get("min_date");
  if (language == "EN")
  {
    language = "RU";
  }
  else
  {
    language = "EN";
  }
  window.location.href=(`/?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
}


function home() {
  var url_string = window.location.href;
  var url = new URL(url_string);
  var language = url.searchParams.get("lang");
  var max_date = url.searchParams.get("max_date");
  var min_date = url.searchParams.get("min_date");
  window.location.href=(`/?mutation=ALL&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
}


function geneDropdown(id) {
  var x = document.getElementById(id + ":");
  current_gene = id;
  var mutationDropdownButton =  document.getElementById("mutationDropdownButton");
  mutationDropdownButton.onclick = function () {geneDropdown(current_gene)};
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
  } else {
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


function changeUpdateMutation(mutation) {
  var url_string = window.location.href;
  var url = new URL(url_string);
  var max_date = url.searchParams.get("max_date");
  var min_date = url.searchParams.get("min_date");
  var language = url.searchParams.get("lang");
  var updateMutationButton = document.getElementById("updateMutation");
  var updateMutationText = document.getElementById("updateMutationText");
  updateMutationButton.onclick = function () {window.location.href=(`/?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);}
  updateMutationText.textContent = mutation;
}


function updateMutation(mutation) {
  var url_string = window.location.href;
  var url = new URL(url_string);
  var max_date = url.searchParams.get("max_date");
  var min_date = url.searchParams.get("min_date");
  var language = url.searchParams.get("lang");
  window.location.href=(`/?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
}

function updateDate(min_date, max_date) {
  var url_string = window.location.href;
  var url = new URL(url_string);
  var mutation = url.searchParams.get("mutation");
  var language = url.searchParams.get("lang");
  window.location.href=(`/?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
}
