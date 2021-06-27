var genes_array = [];
var current_gene = "";
var current_choice_section = "lineageSection";
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
    gene_button_button.onclick = function() {
        geneDropdown(this.id)
    };
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
    var mutationDropdownButton = document.getElementById("mutationDropdownButton");
    var geneDropdownButtonText = document.getElementById("geneDropdownButtonText");
    var mutationDropdownButtonText = document.getElementById("mutationDropdownButtonText");
    var mutationNameDropdownButtonText = document.getElementById("mutationNameDropdownButtonText");
    var lineageDropdownButtonText = document.getElementById("lineageDropdownButtonText");

    var lineage_dropdown = document.getElementById("lineage");
    var gene_dropdown = document.getElementById("gene");
    var mutation_dropdown = document.getElementById("mutation");

    var mutation_array = mutation.split(':');
    mutationDropdownButton.onclick = function() {
        geneDropdown(mutation.split(':')[0])
    };

    if (mutation_array[0] == "ALL") {
    }
    else if (mutation_array[0] == "lineage") {
      lineageDropdownButtonText.textContent = mutation_array[1];
    }
    else {
      switchToLineage();
      geneDropdownButtonText.textContent = mutation_array[0];
      mutationDropdownButtonText.textContent = mutation_array[0] + ':';
      mutationNameDropdownButtonText.textContent = mutation_array[1];
    }


    mutation = mutations[0];
    mutation_array = mutation.split(':');
    var previous_gene = mutation_array[0];

    for (var i = 0; i < mutations.length; i++) {
        mutation = mutations[i];
        mutation_array = mutation.split(':');
        var gene = mutation_array[0];
        var mutation_name = mutation_array[1];
        if (gene != previous_gene) {
            genes_array.push(gene);
            var previous_gene = gene;
            gene_button_content = add_gene_dropdown(gene, mutation_dropdown, gene_dropdown);
        }
        if (gene == "lineage") {
            var mutation_button = document.createElement("a");
            mutation_button.textContent = mutation_name;
            mutation_button.className = "w3-bar-item w3-button";
            mutation_button.id = mutation;
            mutation_button.onclick = function() {
                changeUpdateLineage(this.id)
            };
            lineage_dropdown.appendChild(mutation_button);
        } else {
            var mutation_button = document.createElement("a");
            mutation_button.textContent = mutation_name;
            mutation_button.className = "w3-bar-item w3-button";
            mutation_button.id = mutation;
            mutation_button.onclick = function() {
                changeUpdate(this.id)
            };
            gene_button_content.appendChild(mutation_button);
        }
    }

    var previous_dropdown = "None";

    mutation = url.searchParams.get("mutation");

    fetch(`/map?mutation=${mutation}&lang=${language}&max_date=${max_date}&min_date=${min_date}`)
        .then(function(response) {
            return response.json();
        })
        .then(function(item) {
            return Bokeh.embed.embed_item(item, "coronamap");
        })

    fetch(`/dateRangeSlider?mutation=${mutation}&lang=${language}&max_date=${max_date}&min_date=${min_date}`)
        .then(function(response) {
            return response.json();
        })
        .then(function(item) {
            return Bokeh.embed.embed_item(item, "dateRangeSlider");
        })
    if (mutation == "ALL") {
      fetch(`/plot?mutation=${mutation}&lang=${language}&max_date=${max_date}&min_date=${min_date}`)
          .then(function(response) {
              return response.json();
          })
          .then(function(item) {
              return Bokeh.embed.embed_item(item, "coronaplot");
          })
    }
}

function switch_lang() {
    if (language == "EN") {
        language = "RU";
    } else {
        language = "EN";
    }
    window.location.href = (window.location.pathname + `?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
}

function home() {
    window.location.href = (`/home?mutation=ALL&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
}

function closeAllDropdowns(except) {
    if (except != "gene") {
      var x = document.getElementById("gene");
      if (x.className.indexOf("w3-show") != -1) {
          x.className = x.className.replace(" w3-show", "");
      }
    }
    if (except != "lineage") {
      var x = document.getElementById("lineage");
      if (x.className.indexOf("w3-show") != -1) {
          x.className = x.className.replace(" w3-show", "");
      }
    }
    for (var i = 0; i < genes_array.length; i++) {
        var local_gene = genes_array[i];
        var x = document.getElementById(local_gene + ":");
        if ((x.className.indexOf("w3-show") != -1) || (except != local_gene)) {
            x.className = x.className.replace(" w3-show", "");
        }
    }
}

function geneDropdown(id) {
    closeAllDropdowns(id);
    var x = document.getElementById(id + ":");
    current_gene = id;

    var mutationDropdownButton = document.getElementById("mutationDropdownButton");
    var mutationDropdownButtonText = document.getElementById("mutationDropdownButtonText");
    var geneDropdownButtonText = document.getElementById("geneDropdownButtonText");
    var mutationNameDropdownButtonText = document.getElementById("mutationNameDropdownButtonText");

    var mutation_array = id.split(':');
    if (mutation_array[0] == "ALL") {
    }
    else if (mutation_array[0] == "lineage") {
    }
    else {
      geneDropdownButtonText.textContent = mutation_array[0];
      mutationDropdownButtonText.textContent = mutation_array[0] + ':';
      mutationNameDropdownButtonText.textContent = mutation_array[1];
    }

    mutationDropdownButton.onclick = function() {
        geneDropdown(current_gene)
    };
    mutationDropdownButtonText.textContent = current_gene + ':';
    geneDropdownButtonText.textContent = current_gene;
    mutationNameDropdownButtonText.textContent = '';

    if (x.className.indexOf("w3-show") == -1) {
        x.className += " w3-show";
    } else {
        x.className = x.className.replace(" w3-show", "");
    }
}

function mainDropdown() {
    closeAllDropdowns("gene");
    var x = document.getElementById("gene");
    if (x.className.indexOf("w3-show") == -1) {
        x.className += " w3-show";
    } else {
        x.className = x.className.replace(" w3-show", "");
    }
}

function lineageDropdown() {
    closeAllDropdowns("lineage");
    var x = document.getElementById("lineage");
    if (x.className.indexOf("w3-show") == -1) {
        x.className += " w3-show";
    } else {
        x.className = x.className.replace(" w3-show", "");
    }
}

function changeUpdate(new_mutation) {
    closeAllDropdowns();
    mutation = new_mutation;
    var updateButton = document.getElementById("update");
    var mutationNameDropdownButtonText = document.getElementById("mutationNameDropdownButtonText");
    updateButton.onclick = function() {
        window.location.href = (`/?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
    }
    mutationNameDropdownButtonText.textContent = mutation.split(':')[1];
}

function changeUpdateLineage(new_lineage) {
    closeAllDropdowns();
    mutation = new_lineage;
    var updateButton = document.getElementById("update");
    var lineageDropdownButtonText = document.getElementById("lineageDropdownButtonText");
    updateButton.onclick = function() {
        window.location.href = (`/?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
    }
    lineageDropdownButtonText.textContent = mutation.split(':')[1];
}

function dateRangeSlider(min_timestamp, max_timestamp) {
    var update = document.getElementById("update");
    min_date = new Date(min_timestamp);
    min_date = min_date.getFullYear() + "-" + (min_date.getMonth() + 1) + "-" + min_date.getDate();
    max_date = new Date(max_timestamp);
    max_date = max_date.getFullYear() + "-" + (max_date.getMonth() + 1) + "-" + max_date.getDate();
    update.onclick = function() {
        window.location.href = (window.location.pathname + `?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
    };
}

function minDatePicker(new_min_date) {
    var update = document.getElementById("update");
    min_date = new_min_date.replace("-0", "");
    update.onclick = function() {
        window.location.href = (window.location.pathname + `?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
    };
}

function maxDatePicker(new_max_date) {
    var update = document.getElementById("update");
    max_date = new_max_date.replace("-0", "");
    update.onclick = function() {
        window.location.href = (window.location.pathname + `?mutation=${mutation}&lang=${language}&min_date=${min_date}&max_date=${max_date}`);
    };
}

function outbreakInfoLink(outbreak_link) {
    console.log(outbreakInfoLink);
    window.location.href = (outbreak_link);
}

function switchToLineage() {
  closeAllDropdowns();
  if (current_choice_section == "lineageSection") {
    var oldSection = document.getElementById("lineageSection");
    var newSection = document.getElementById("geneMutationSection");
    current_choice_section = "geneMutationSection";
  }
  else {
    var oldSection = document.getElementById("geneMutationSection");
    var newSection = document.getElementById("lineageSection");
    current_choice_section = "lineageSection";
  }
  oldSection.style.display = "none";
  newSection.style.display = "block";
}