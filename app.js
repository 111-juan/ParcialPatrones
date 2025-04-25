const App = {
    users: [],
    admin: {
      username: "admin",
      password: "admin123"
    },
    user: null,
    reservationMade: false,
  
    showRegister() {
      this.hideAll();
      document.getElementById("register").classList.remove("hidden");
    },
  
    showLogin() {
      this.hideAll();
      document.getElementById("auth").classList.remove("hidden");
    },
  
    showReservation() {
      this.hideAll();
      document.getElementById("main").classList.remove("hidden");
      document.getElementById("user-name").textContent = this.user;
      this.assignRandomTable();
    },
  
    hideAll() {
      document.querySelectorAll(".container").forEach(el => el.classList.add("hidden"));
    },
  
    backToSelect() {
      this.hideAll();
      document.getElementById("auth").classList.remove("hidden");
    },
  
    login(event) {
      event.preventDefault();
      const input = document.getElementById("login-user").value;
      const pass = document.getElementById("login-pass").value;
  
      // Check admin login
      if (input === this.admin.username && pass === this.admin.password) {
        alert("Inicio de sesión como administrador no implementado aún.");
        return;
      }
  
      const user = this.users.find(u => (u.email === input || u.name === input) && u.pass === pass);
      if (user) {
        this.user = user.name;
        this.showReservation();
      } else {
        alert("Usuario o contraseña incorrectos");
      }
    },
  
    register(event) {
      event.preventDefault();
      const user = {
        name: document.getElementById("reg-name").value,
        lastname: document.getElementById("reg-lastname").value,
        id: document.getElementById("reg-id").value,
        email: document.getElementById("reg-email").value,
        birth: document.getElementById("reg-birth").value,
        pass: document.getElementById("reg-pass").value,
      };
      this.users.push(user);
      alert("Registro exitoso, ahora inicia sesión");
      this.showLogin();
    },
  
    validateID(input) {
      input.value = input.value.replace(/[^0-9]/g, '');
    },
  
    assignRandomTable() {
      const tableInput = document.getElementById("table");
      const tables = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2", "E1", "E2"];
      const random = tables[Math.floor(Math.random() * tables.length)];
      tableInput.value = random;
    },
  
    generateTicket() {
      if (this.reservationMade) {
        alert("Ya has generado una reserva. Si deseas hacer otra, confirma en el mensaje posterior.");
        return;
      }
  
      const date = document.getElementById("date").value;
      const time = document.getElementById("time").value;
      const people = document.getElementById("people").value;
      const table = document.getElementById("table").value;
      const ticketId = Math.floor(100000 + Math.random() * 900000);
  
      const ticket = document.getElementById("ticket");
      ticket.classList.remove("hidden");
      ticket.innerHTML = `
        <h3>Reserva Confirmada</h3>
        <p><strong>ID Reserva:</strong> ${ticketId}</p>
        <p><strong>Cliente:</strong> ${this.user}</p>
        <p><strong>Restaurante:</strong> La Casa Criolla</p>
        <p><strong>Fecha:</strong> ${date}</p>
        <p><strong>Hora:</strong> ${time}</p>
        <p><strong>Número de personas:</strong> ${people}</p>
        <p><strong>Mesa asignada:</strong> ${table}</p>
      `;
  
      this.reservationMade = true;
  
      setTimeout(() => {
        if (confirm("¿Deseas realizar una nueva reserva?")) {
          document.getElementById("reservation-form").reset();
          this.assignRandomTable();
          ticket.classList.add("hidden");
          this.reservationMade = false;
        }
      }, 300);
    }
  };
  