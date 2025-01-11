function toggleZoom(event) {
  let currentZoomLevel = parseFloat(localStorage.getItem('zoomLevel')) || 100;
  currentZoomLevel += 10;
  if (currentZoomLevel > 200) {
    currentZoomLevel = 100;
  }
  localStorage.setItem('zoomLevel', currentZoomLevel);
  document.body.style.zoom = currentZoomLevel + '%';
  updateZoomTooltip(currentZoomLevel);
}

function getComputedBackgroundColor(element) {
  var tempElement = document.createElement('div');
  tempElement.classList.add(element);
  document.body.appendChild(tempElement);
  var computedColor = window.getComputedStyle(tempElement).getPropertyValue('background-color');
  document.body.removeChild(tempElement);
  return computedColor;
}

function getComputedColor(element) {
  var tempElement = document.createElement('div');
  tempElement.classList.add(element);
  document.body.appendChild(tempElement);
  var computedColor = window.getComputedStyle(tempElement).getPropertyValue('color');
  document.body.removeChild(tempElement);
  return computedColor;
}

function parseRGBA(color) {
  var rgba = color.substring(color.indexOf('(') + 1, color.lastIndexOf(')')).split(',');
  return {
    r: parseInt(rgba[0].trim()),
    g: parseInt(rgba[1].trim()),
    b: parseInt(rgba[2].trim()),
  };
}

function rgbaWithAlpha(color) {
  var components = color.split(",");
  components[3] = "1)";
  return components.join(",");
}

function interpolateColor(color1, color2, factor) {
  var c1 = parseRGBA(color1);
  var c2 = parseRGBA(color2);
  var r = Math.round(c1.r + (c2.r - c1.r) * factor);
  var g = Math.round(c1.g + (c2.g - c1.g) * factor);
  var b = Math.round(c1.b + (c2.b - c1.b) * factor);
  var a = 0.25 + (0.65 - 0.25) * factor;
  return 'rgba(' + r + ',' + g + ',' + b + ',' + a + ')';
}

function deleteMessage(button) {
  // Traverse up the DOM to find the parent alert div and remove it
  var alertDiv = button.closest('.alert');
  if (alertDiv) {
    alertDiv.remove();
  }
};
function toggleChevronIcon(button) {
  const chevronIcon = button.querySelector('.bi-chevron-down');
  chevronIcon.classList.toggle('flip');
  button.setAttribute('aria-expanded', chevronIcon.classList.contains('flip'));
}
function loadTab(tabId, endpoint) {
  var tabContent = document.getElementById(tabId);
  if (!tabContent.hasAttribute('data-loaded')) {
    var container = document.createElement('div');
    container.classList.add("iframeContainer");
    var iframe = document.createElement('iframe');
    iframe.classList.add("iframeFill");
    iframe.src = endpoint;
    iframe.frameBorder = 0;
    tabContent.appendChild(container);
    container.appendChild(iframe);
    tabContent.setAttribute('data-loaded', 'true');
    iframe.addEventListener('load', function () {
      var links = iframe.contentDocument.querySelectorAll('a');
      links.forEach(function (link) {
        link.setAttribute('target', '_top');
      });
    });
  }
}

function updateZoomTooltip(level) {
  const zoomButton = document.getElementById('zoomButton');
  try {
    zoomButton.textContent = ` ${level}%`;
  } catch (error) {
    
  }
}

$(document).ready(function () {
  $('[id$="_table"]').each(function () {
      var table = $(this).DataTable({
          scrollX: true,
          "pageLength": 25,
          aaSorting: [],
          columnDefs: [{
              targets: "_all",
              className: 'dt-body-left'
          }],
          "oLanguage": {
              "sSearch": "",
              "sSearchPlaceholder": "Filter Results",
              "sLengthMenu": "_MENU_ &nbsp;per page",
          },
          "createdRow": function (row, data, dataIndex) {
              var table = $(this).DataTable();
              var tableId = table.settings()[0].sTableId;
              var rawTable = document.getElementById(tableId);
              var headersRow = rawTable.rows[0];
              var headerCells = headersRow.cells;
              $(row).css('background-opacity', 0.5); 
          },
          "columnDefs": [
              { "targets": '_all', "className": 'display dt-no-padding' },
              { "type": "string", "targets": 0 },
              { "className": "dt-left", "targets": 0 },
          ],
          layout: {
              top1Start: {
                  search: {
                  },
                  pageLength: {
                      menu: [10, 25, 50, 100, 200, 1000]
                  },
                  buttons: [
                      'copyHtml5',
                      'excelHtml5',
                      'csvHtml5',
                      'pdfHtml5',
                  ],
              },
              top1End: null,
              topStart: 'info',
              topEnd: 'paging',
              bottomStart: 'info',
              bottomEnd: 'paging'
          },
          "initComplete": function () {
              var api = this.api();
              var table = api.table(); // Current table

              // Add export buttons
              var btns = $(table.table().container()).find('.dt-button');
              btns.addClass('bi');
              var icon_map = {
                  "PDF": "bi-filetype-pdf",
                  "CSV": "bi-filetype-csv",
                  "Excel":"bi-file-earmark-spreadsheet",
                  "Copy": "bi-copy",
              }
              btns.each(function () {
                  var buttonText = $(this).text().trim();
                  $(this).addClass(icon_map[buttonText]);
              });
              btns.addClass('datatables-export text-muted');
              btns.each(function() {
                  $(this).find('span').prepend('&nbsp;');
              });
              var mutedColor = getComputedColor('text-primary');
              var filterInput = $(api.table().container()).find('.dt-input input');
              filterInput.css('color', mutedColor);

              // Apply custom css classes to certain table rows
              $(table.table().container()).find('.dt-info').addClass("text-normal");
              $(table.table().container()).find('.dt-length').find("label").addClass("text-normal");
              $(api.table().header()).find('th').addClass('bg-dark text-light');
              // Grab primary text css color
              var primarycolor = getComputedColor('text-light');
              // Dynamically inject CSS to set placeholder color
              var style = document.createElement('style');
              style.innerHTML = '.column-search-input::placeholder { color: ' + primarycolor + '; }';
              document.getElementsByTagName('head')[0].appendChild(style);

              $(api.table().header()).find('th').each(function (index) {
                  var column = table.column(index);
                  var title = $(this).text();
                  $(this).html(
                      '<input type="text" class="column-search-input bg-transparent mx-0 my-0 text-light" placeholder="'
                      + title + '" /><span class="dt-column-title" role="button" style="display:none;">' + title
                      + '</span><span class="dt-column-order" style="right:0px;top:-4px;"></span>'
                  );
                  $('input', this).on('click', function (e) {
                      e.stopPropagation(); // Prevent propagation to avoid sorting
                  });
                  $('input', this).on('keyup change', function () {
                      if (column.search() !== this.value) {
                          column.search(this.value).draw();
                      }
                  });
              });
              $(api.table().header()).find('th').on('click', function (e) {
                  e.preventDefault(); 
              });

          }
      });
      new $.fn.dataTable.FixedHeader(table);
  });
});