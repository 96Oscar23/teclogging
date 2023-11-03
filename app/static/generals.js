function validanumeros(e) {
    // Allow: backspace, delete, tab, escape, enter and .
    if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110, 190]) !== -1 ||
        // Allow: Ctrl+A, Command+A
        (e.keyCode === 65 && (e.ctrlKey === true || e.metaKey === true)) ||
        // Allow: home, end, left, right, down, up
        (e.keyCode >= 35 && e.keyCode <= 40) ||
        // Allow: Ctrl+c
        (e.keyCode === 67 && (e.ctrlKey === true)) ||
        // Allow: Ctrl+v
        (e.keyCode === 86 && (e.ctrlKey === true))
    ) {
        // let it happen, don't do anything
        return;
    }
    // Ensure that it is a number and stop the keypress
    if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
        e.preventDefault();
    }

}


$(document).on("ready", function () {

    //ocultamos elementos cargando
    $(".cargando").hide();


    $('body').on('keydown', '.just_numbers', function (e) {
        validanumeros(e);
    });


    $('body').on('paste', '.just_numbers', function (e) {
        if (window.clipboardData && window.clipboardData.getData) { // IE
            pastedText = window.clipboardData.getData('Text');
        }
        else if (e.originalEvent.clipboardData && e.originalEvent.clipboardData.getData) { // other browsers
            pastedText = e.originalEvent.clipboardData.getData('text/plain');
        }
        control = this;
        setTimeout(function () {
            $(control).val(limpiaNumero(pastedText));
        }, 100);
    });
    //$("#logo_horizontal").css({'max-width':'none'});
    $('body').on('click', '.cajaEntrada', function (e) {
        $(this).select();
    });

    $('body').on('click', '.btn-borrado', function (e) {
        var objeto = $(this).attr("objeto");
        var objetoid = $(this).attr("objetoid");
        var nombre = $(this).attr("nombre");
        var tabla = $(this).closest("table")[0].id;
        var index = -1;

        for (i = 0; i <= HSCore.components.HSDatatables.collection.length - 1; i++) {
            if (HSCore.components.HSDatatables.collection[i].id == tabla) {
                index = HSCore.components.HSDatatables.collection[i].$initializedEl.row($(this).parents('tr')).index();

            }

        }

        $("#confirmarBorradoObjeto").val(objeto);
        $("#confirmarBorradoID").val(objetoid);
        $("#confirmarBorradoNombre").text(nombre);
        $("#confirmarBorradoTabla").val(tabla);
        $("#confirmarBorradoRow").val(index);


    });


    //$('#datatable').DataTable(DATATABLEOPC);
    //HSCore.components.HSDatatables.init('.js-datatable');




    //control para buscador
    /*$('.buscadorDataTable').on('keyup', function (e) {
        let tablaid  = $(this).attr("tablaid");
        e.preventDefault();
        if (tablaid ){
            $("#"+tablaid).DataTable().search( this.value ).draw();
        }else{
            alerta("Error","No se encontro tabla","danger");
        }
        return false;
    });*/

    //Botones datatable export

    $('body').on('click', '.botonExportaDataTableCopiar', function () {
        let tablaid = $(this).attr("tablaid");
        if (tablaid) {
            $("#" + tablaid).DataTable().button('.buttons-copy').trigger();
        } else {
            alerta("Error", "No se encontro tabla", "danger");
        }
    });
    $('body').on('click', '.botonExportaDataTableImprimir', function () {
        let tablaid = $(this).attr("tablaid");
        if (tablaid) {
            $("#" + tablaid).DataTable().button('.buttons-print').trigger();
        } else {
            alerta("Error", "No se encontro tabla", "danger");
        }
    });
    $('body').on('click', '.botonExportaDataTableExcel', function () {
        let tablaid = $(this).attr("tablaid");
        if (tablaid) {
            $("#" + tablaid).DataTable().button('.buttons-excel').trigger();
        } else {
            alerta("Error", "No se encontro tabla", "danger");
        }
    });
    $('body').on('click', '.botonExportaDataTableCSV', function () {
        let tablaid = $(this).attr("tablaid");
        if (tablaid) {
            $("#" + tablaid).DataTable().button('.buttons-csv').trigger();
        } else {
            alerta("Error", "No se encontro tabla", "danger");
        }
    });
    $('body').on('click', '.botonExportaDataTablePDF', function () {
        let tablaid = $(this).attr("tablaid");
        if (tablaid) {
            $("#" + tablaid).DataTable().button('.buttons-pdf').trigger();
        } else {
            alerta("Error", "No se encontro tabla", "danger");
        }
    });




});

// se puede mejorar esta logica.
function alerta(titulo, mensaje, tipo) {

    $("#alerta_titulo").text(titulo);
    $("#alerta_body").text(mensaje);

    let clases = $("#liveToast").attr('class');

    //eliminamos las clases para evitar problemas. 

    clases = clases.split(" ");

    for (var i = 0; i < clases.length; i++) {
        if (clases[i].includes("alert-") == true) {
            $("#liveToast").removeClass(clases[i]);
        }
    }

    //agregamos la clase
    $("#liveToast").addClass("alert-" + tipo);

    //$("#liveToast").show();

    //$(#liveToast").show();
    const liveToast = new bootstrap.Toast(document.querySelector('#liveToast'));

    liveToast.show();

}

function borrarRegistro() {


    var tabla = $("#confirmarBorradoTabla").val();
    var objid = $("#confirmarBorradoID").val();
    var objeto = $("#confirmarBorradoObjeto").val();
    var row = $("#confirmarBorradoRow").val();
    dat = JSON.stringify({ objid: objid, objeto: objeto });
    $(".cargando").show();
    $('.btn').attr('disabled', 'disabled');

    $.ajax({
        url: "/" + objeto + "/delete",
        type: "POST",
        data: dat,
        contentType: 'application/json',
        dataType: "json",
        success: function (data) {


            //cargamos la tabla sucursales
            if (data.estatus == "ok") {

                //quitamos el elemento de la tabla
                for (i = 0; i <= HSCore.components.HSDatatables.collection.length - 1; i++) {
                    if (HSCore.components.HSDatatables.collection[i].id == tabla) {
                        HSCore.components.HSDatatables.collection[i].$initializedEl.row(row).remove().draw();
                    }
                }

                alerta("Aviso", data.msn, "success");

            } else {
                alerta("Error", data.msn, "danger");

            }




        },
        error: function () {

            alerta("Error", "Error al Grabar", "danger");

        },
        complete: function () {

            //ocultamos los modales, los loadings y habilitamos botones

            $('#confirmarBorrado').appendTo("body").modal('hide');
            $(".cargando").hide();
            $('.btn').removeAttr('disabled');
        }

    });

}

function iniciarTabla(controlesHeader, idtabla, controlesFooter) {

    //Agregmos los botones de exportar
    $(controlesHeader).append(`<div class="row align-items-center">
            <div class="col">
                <form>
                    <!-- Buscador -->
                    <div class="input-group input-group-merge input-group-flush">
                        <div class="input-group-prepend input-group-text">
                            <i class="bi-search"></i>
                        </div>
                        <input id="`+ idtabla + `Buscador" type="search" class="form-control buscadorDataTable"
                            placeholder="Buscar" tablaid=`+ idtabla + ` aria-label="Buscar">
                    </div>
                    <!-- End Search -->
                </form>
            </div>
            <div class="col-auto">
                <!--Exportar-->
                <div class="dropdown me-2">
                    <button type="button" class="btn btn-white btn-sm dropdown-toggle" id="usersExportDropdown"
                        data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="bi-download me-2"></i> Exportar
                    </button>
                    <div class="dropdown-menu dropdown-menu-sm-end" aria-labelledby="usersExportDropdown">
                        <a id="export-copy" class="botonExportaDataTableCopiar dropdown-item" href="javascript:;"  tablaid="`+ idtabla + `">
                            <img class="avatar avatar-xss avatar-4x3 me-2"
                                src="/static/assets/svg/illustrations/copy-icon.svg"
                                alt="Image Description">
                            Copiar
                        </a>
                    
                        
                        
                        <a id="export-excel" class="botonExportaDataTableExcel dropdown-item" href="javascript:;"  tablaid="`+ idtabla + `">
                            <img class="avatar avatar-xss avatar-4x3 me-2"
                                src="/static/assets/svg/brands/excel-icon.svg"
                                alt="Image Description">
                            Excel
                        </a>
                        <a id="export-csv" class="botonExportaDataTableCSV dropdown-item" href="javascript:;"  tablaid="`+ idtabla + `">
                            <img class="avatar avatar-xss avatar-4x3 me-2"
                                src="/static/assets/svg/components/placeholder-csv-format.svg"
                                alt="Image Description">
                            .CSV
                        </a>
                        
                    </div>
                </div>
            </div>
            
        </div> `);
    //agregmos controles de paginacion en footer
    $(controlesFooter).append(`<div class="row justify-content-center justify-content-sm-between align-items-sm-center">
            <div class="col-sm mb-2 mb-sm-0">
              <div class="d-flex justify-content-center justify-content-sm-start align-items-center">
                <span class="me-2">Mostrando:</span>
                <div class="tom-select-custom" style="width: 85px;">
                  <select id="`+ idtabla + `comboRegistros" class="js-select-tabla form-select form-select-borderless" autocomplete="off" data-hs-tom-select-options='{
                            "searchInDropdown": false,
                            "hideSearch": true
                          }'>
                    <option value="10" selected>10</option>
                    <option value="50">50</option>
                    <option value="100" >100</option>
                    <option value="200">200</option>
                  </select>
                </div>
                <span class="text-secondary me-2">de</span>
                <!-- Pagination Quantity -->
                <span id="`+ idtabla + `total"></span>
              </div>
            </div>
            <!-- Pagination -->
            <div class="col-sm-auto">
              <div class="d-flex justify-content-center justify-content-sm-end">
                <nav id="`+ idtabla + `paginacion" aria-label="Activity pagination"></nav>
              </div>
            </div>
          </div>`);
    //inicializamos combo de reigstros tabla
    HSCore.components.HSTomSelect.init('.js-select-tabla');


    //template incializar datatable
    HSCore.components.HSDatatables.init("#" + idtabla, {
        order: [],
        info: {
            "totalQty": "#" + idtabla + 'total'
        },
        search: "#" + idtabla + "Buscador",
        pageLength: 10,
        pagination: idtabla + 'paginacion',
        paginationNextLinkMarkup: '<span aria-hidden="true">Sig</span>',
        columnDefs: [{
            "targets": 'no-sort',
            "orderable": false,
        },
        {
            "targets": "no-show",
            "visible": false
        },
        ],
        entries: "#" + idtabla + "comboRegistros",
        language: {
            zeroRecords: `<div class="text-center p-4">
            <img class="mb-3" src="/static/assets/svg/illustrations/oc-browse.svg" alt="Image Description" style="width: 10rem;" data-hs-theme-appearance="default">
            <img class="mb-3" src="/static/assets/svg/illustrations-light/oc-browse.svg" alt="Image Description" style="width: 10rem;" data-hs-theme-appearance="dark">
            <p class="mb-0">No existen Registros</p>
            </div>`
        },
        "buttons": [
            {
                "extend": "copy",
                "className": "d-none"
            },
            {
                "extend": "excel",
                "className": "d-none"
            },
            {
                "extend": "csv",
                "className": "d-none"
            },
            {
                "extend": "pdf",
                "className": "d-none"
            },
            {
                "extend": "print",
                "className": "d-none"
            }
        ]
    });






}

function inicializaDatetimepicker(inputID, start_date, end_date) {


    $(`input[id="${inputID}"]`).daterangepicker({
        opens: 'down',
        startDate: moment().startOf('month'),
        endDate: moment().endOf('month'),
        ranges: {
            'Hoy': [moment(), moment()],
            'Ayer': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Últimos 7 días': [moment().subtract(6, 'days'), moment()],
            'Últimos 30 días': [moment().subtract(29, 'days'), moment()],
            'Este mes': [moment().startOf('month'), moment().endOf('month')],
            'Mes pasado': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        },
        "locale": {
            "applyLabel": "Aplicar",
            "cancelLabel": "Cancelar",
            "fromLabel": "Desde",
            "toLabel": "Hasta",
            "customRangeLabel": "Personalizado",
            "daysOfWeek": ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"],
            "monthNames": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
            "firstDay": 1,
            "format": "DD/MM/YYYY"
        }
    }, function (start, end) {
        //fill_table(start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD'));
        $("#" + start_date + "").val(start.format('DD/MM/YYYY'));
        $("#" + end_date + "").val(end.format('DD/MM/YYYY'));

    });

    //inicializamos los valores de los input
    $("#" + start_date + "").val(moment().startOf('month').format('DD/MM/YYYY'));
    $("#" + end_date + "").val(moment().endOf('month').format('DD/MM/YYYY'));

}
