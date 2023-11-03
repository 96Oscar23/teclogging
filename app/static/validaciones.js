$(document).on("ready",function () {

    

    
    RFCAMBOS = /^(([A-Z]|[a-z]){3,4})([0-9]{6})((([A-Z]|[a-z]|[0-9]){3}))/
    AMBOSL = /^.{12,13}$/
    RFCMORAL = /^(([A-Z]|[a-z]){3})([0-9]{6})((([A-Z]|[a-z]|[0-9]){3}))/
    RFCFISICA = /^(([A-Z]|[a-z]|\s){1})(([A-Z]|[a-z]){3})([0-9]{6})((([A-Z]|[a-z]|[0-9]){3}))/
    MORALL = /^.{12,12}$/
    FISICAL = /^.{13,13}$/
    RFCDINAMICA = RFCFISICA
    CLABE = /^(\d{10}|\d{18})$/
    RFCL = FISICAL
    PESOVOLUMEN = /^(0*[1-9][0-9]*(\.[0-9]+)?|0+\.[0-9]*[1-9][0-9]*)$/
    EMAILPDX= /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/

    jQuery.validator.addMethod("menos1", function (value, element) {
        return this.optional(element) || value!='-1';
    }, "Requerido"); 
    jQuery.validator.addMethod("passcomplex", function (value, element) {
        return this.optional(element) || /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*\s).{8,20}$/.test(value);
    }, "La contrasena debe de contener al menos una minúscula, una mayúscula y un número.");
    jQuery.validator.addMethod("epdx", function (value, element) {
        return this.optional(element) || EMAILPDX.test(value);
    }, "Correo incorrecto.");

    REQUERIDO = 'Requerido';
    optionsvalidate = {
        errorClass: "is-invalid",
        validClass: "is-valid",
        errorElement: "span",
        rules: {
            nombre: { required: true},
            idinterno: { required: true},
            rolid:{menos1: true},
            useremail: {
                required: true,
                epdx: true},
            loginpassword: {
                required: true
            },
            contrasena: {
                required: true,
                minlength: 8,
                maxlength: 16,
                passcomplex: true
            },
            confirmar: {
                required: true,
                minlength: 8,
                maxlength: 16,
                equalTo: '#contrasena'
            },
        },
        messages: {
            nombre: {required: REQUERIDO},
            idinterno: {required: REQUERIDO},
            rolid: {menos1: REQUERIDO},
            useremail: {
                required: REQUERIDO,
                epdx: 'Ingrese un correo válido'
            },
            loginpassword: {
                required: REQUERIDO

            },
            contrasena: {
                required: REQUERIDO,
                minlength: 'Ingrese al menos 8 caracteres',
                maxlength: 'Ingrese máximo 16 caracteres'

            },
            confirmar: {
                required: REQUERIDO,
                minlength: 'Ingrese al menos 8 caracteres',
                equalTo: 'Las contraseñas no coinciden',
                maxlength: 'Ingrese máximo 16 caracteres'
            },
        },        
        highlight: function (element, errorClass, validClass) {
            
            if($(element).hasClass('js-toggle-password')){
                $(element).closest('div').addClass(errorClass).removeClass(validClass);
            }else{
                $(element).addClass(errorClass).removeClass(validClass);

            }
        },
        unhighlight: function (element, errorClass, validClass) {
            if($(element).hasClass('js-toggle-password')){
                $(element).closest('div').removeClass(errorClass).addClass(validClass);
            }else{
                $(element).removeClass(errorClass).addClass(validClass);

            }
            
        },
        errorPlacement: function (error, element) {
            if (element.is(":radio") || element.is(":checkbox")) {
                element.closest('.option-group').after(error);
            } else {
                if(!element.hasClass('noerror')){
                    if(element.hasClass('js-toggle-password')){
                        element.closest('div').after(error);
                    }else{
                        error.insertAfter(element);
                    }

                }
                    
            }
        },
        submitHandler: function (form) {
            $(':submit').prop('disabled', true);
            if(form.id!='formaModalBusqueda'){
                form.submit();
            }
                
            else {                
                buscadorGeneral();//funcion en dashboard.html
            }
        }        
    };
    $(".js-validate").validate(optionsvalidate);

});