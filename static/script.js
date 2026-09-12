// =====================================================
// SMART LOST & FOUND
// MAIN JAVASCRIPT
// =====================================================

const menuToggle = document.querySelector(".menu-toggle");
const navbar = document.querySelector(".navbar");

if (menuToggle && navbar) {
  menuToggle.addEventListener("click", function () {
    const isOpen = navbar.classList.toggle("menu-open");

    menuToggle.setAttribute("aria-expanded", String(isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
  });
}


// =====================================================
// CATEGORY - OTHER
// =====================================================

const categorySelect = document.getElementById("category");

const otherCategoryBox =
  document.getElementById("other-category-box");

const otherCategoryInput =
  document.getElementById("other_category");


if (categorySelect) {
  categorySelect.addEventListener("change", function () {

    if (this.value === "other") {

      if (otherCategoryBox) {
        otherCategoryBox.style.display = "block";
      }

      if (otherCategoryInput) {
        otherCategoryInput.required = true;
      }

    } else {

      if (otherCategoryBox) {
        otherCategoryBox.style.display = "none";
      }

      if (otherCategoryInput) {
        otherCategoryInput.required = false;
        otherCategoryInput.value = "";
      }

    }

  });
}


// =====================================================
// SOCKET.IO
// LIVE NOTIFICATION COUNT
// =====================================================

document.addEventListener("DOMContentLoaded", function () {

  // ---------------------------------------------------
  // CHECK SOCKET.IO
  // ---------------------------------------------------

  if (typeof io === "undefined") {

    console.error(
      "Socket.IO library not loaded."
    );

    return;
  }


  // ---------------------------------------------------
  // NOTIFICATION ELEMENT
  // ---------------------------------------------------

  const notificationCount =
    document.getElementById("notificationCount");


  // ---------------------------------------------------
  // CREATE SOCKET CONNECTION
  // ---------------------------------------------------

  const socket = io();


  // ---------------------------------------------------
  // SOCKET CONNECTED
  // ---------------------------------------------------

  socket.on("connect", function () {

    console.log(
      "Socket.IO connected"
    );

  });


  // ---------------------------------------------------
  // SOCKET DISCONNECTED
  // ---------------------------------------------------

  socket.on("disconnect", function () {

    console.log(
      "Socket.IO disconnected"
    );

  });


  // ---------------------------------------------------
  // LIVE NOTIFICATION COUNT
  // ---------------------------------------------------
  //
  // app.py sends:
  //
  // notification_count_update
  //
  // {
  //     unread_count: 3
  // }
  //
  // ---------------------------------------------------

  socket.on(
    "notification_count_update",
    function (data) {

      console.log(
        "Notification count updated:",
        data
      );


      // -------------------------------------------------
      // CHECK ELEMENT
      // -------------------------------------------------

      if (!notificationCount) {
        return;
      }


      // -------------------------------------------------
      // GET COUNT
      // -------------------------------------------------

      const count =
        Number(data?.unread_count) || 0;


      // -------------------------------------------------
      // UPDATE COUNT
      // -------------------------------------------------

      if (count > 0) {

        notificationCount.textContent =
          ` (${count})`;

        notificationCount.style.display =
          "inline";

      } else {

        notificationCount.textContent =
          "";

        notificationCount.style.display =
          "none";
      }

    }
  );


  // ---------------------------------------------------
  // SOCKET ERROR
  // ---------------------------------------------------

  socket.on(
    "connect_error",
    function (error) {

      console.error(
        "Socket.IO connection error:",
        error
      );

    }
  );

});