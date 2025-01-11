var colorMap = {
  'LOW': '#fff7b3',  // Light yellow
  'MEDIUM': '#ffcc99',  // Light orange
  'HIGH': '#ffb3b3',  // Light red
  'CRITICAL': '#ff6666'  // Light dark red
};
function {{table_name}}loadTable() {
  var table = $('#{{table_name}}_customtable').DataTable({
    {% for k, data in config.items() %}
    "{{k}}":{{json.dumps(data, indent=2).strip()}},{% endfor %}
    "createdRow": {{ row_function }},
    "initComplete": {{ init_function or "{}" }}
  });
    new $.fn.dataTable.FixedHeader(table);
};
(function() {
  function {{table_name}}checkJQuery() {
      if (
          window.jQuery 
          && typeof $.fn.dataTable !== 'undefined'
          && typeof $.fn.dataTable.FixedHeader !== 'undefined'
      ) {
        {{table_name}}loadTable();
      } else {
        setTimeout({{table_name}}checkJQuery, 50);
      }
  }
  {{table_name}}checkJQuery();
})();