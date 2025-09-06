$(function () {
  let modalRol = $("#modalRol");

  function abrirModal(url) {
    $.get(url, function (data) {
      modalRol.html(data.html_form);
      modalRol.modal("show");
    });
  }

  function guardarForm(form) {
    $.post(form.attr("action"), form.serialize(), function (data) {
      if (data.form_is_valid) {
        $("#tabla_roles_disponibles").html(data.html_roles_disponibles);
        $("#tabla_roles_eliminados").html(data.html_roles_eliminados);
        modalRol.modal("hide");
      } else {
        modalRol.html(data.html_form);
      }
    });
    return false;
  }

  // Crear
  $("#btnAgregarRol").click(function () {
    abrirModal("/roles/ingresar/");
  });

  modalRol.on("submit", ".js-rol-create-form", function () {
    return guardarForm($(this));
  });

  // Editar
  $("#tabla_roles_disponibles").on("click", ".js-modificar-rol", function () {
    abrirModal($(this).data("url"));
  });

  modalRol.on("submit", ".js-rol-update-form", function () {
    return guardarForm($(this));
  });

  // Eliminar
  $("#tabla_roles_disponibles").on("click", ".js-eliminar-rol", function () {
    abrirModal($(this).data("url"));
  });

  modalRol.on("submit", ".js-rol-delete-form", function () {
    return guardarForm($(this));
  });

  // Recuperar
  $("#tabla_roles_eliminados").on("click", ".js-recuperar-rol", function () {
    abrirModal($(this).data("url"));
  });

  modalRol.on("submit", ".js-rol-recover-form", function () {
    return guardarForm($(this));
  });
});
