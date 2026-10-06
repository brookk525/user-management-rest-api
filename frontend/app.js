/* Autor: Brooklyn Muñoz */

const apiUrl = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const profileForm = document.getElementById("profileForm");
    const changeAvatarButton = document.getElementById("changeAvatarButton");
    const deleteUserButton = document.getElementById("deleteUserButton");
    const logoutButton = document.getElementById("logoutButton");
    const loadInfoButton = document.getElementById("loadInfoButton");
    const accountButton = document.getElementById("accountButton");

    if (loginForm !== null) {
        loginForm.addEventListener("submit", login);
    }

    if (registerForm !== null) {
        registerForm.addEventListener("submit", register);
    }

    if (profileForm !== null) {
        loadProfile();
        profileForm.addEventListener("submit", updateUser);
    }

    if (changeAvatarButton !== null) {
        changeAvatarButton.addEventListener("click", changeAvatar);
    }

    if (deleteUserButton !== null) {
        deleteUserButton.addEventListener("click", deleteUser);
    }

    if (logoutButton !== null) {
        logoutButton.addEventListener("click", logout);
    }

    if (loadInfoButton !== null) {
        loadInfoButton.addEventListener("click", loadInfoFile);
    }

    if (accountButton !== null) {
        accountButton.addEventListener("click", showAccountView);
    }
});

async function login(event) {
    event.preventDefault();

    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;
    const error = document.getElementById("loginError");
    const loginRequest = {
        email: email,
        password: password,
    };

    const response = await fetch(apiUrl + "/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(loginRequest),
    });

    if (!response.ok) {
        error.textContent = "Error, usuario no encontrado. Vuelve a introducir los datos o registrate si aún no lo estás.";
        return;
    }

    const data = await response.json();
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("email", email);

    const user = await findUserByEmail(email);
    if (user === null) {
        error.textContent = "Login correcto, pero no se ha encontrado el usuario en la base de datos local.";
        return;
    }

    localStorage.setItem("userId", user.id);
    window.location.href = "users.html";
}

async function register(event) {
    event.preventDefault();

    const name = document.getElementById("registerName").value;
    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;
    const message = document.getElementById("registerMessage");
    const registerRequest = {
        name: name,
        email: email,
        password: password,
    };

    const response = await fetch(apiUrl + "/auth/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(registerRequest),
    });

    if (!response.ok) {
        message.className = "message error";
        message.textContent = "No se ha podido registrar el usuario.";
        return;
    }

    const data = await response.json();
    localStorage.setItem("userId", data.user_id);
    localStorage.setItem("email", email);
    message.className = "message ok";
    message.textContent = "Usuario registrado. Ahora inicia sesión.";

    setTimeout(function () {
        window.location.href = "index.html";
    }, 1200);
}

async function findUserByEmail(email) {
    const response = await fetch(apiUrl + "/list_users");

    if (!response.ok) {
        return null;
    }

    const ids = await response.json();

    for (const id of ids) {
        const userResponse = await fetch(apiUrl + "/users/" + id);
        if (userResponse.ok) {
            const user = await userResponse.json();
            if (user.email === email) {
                return user;
            }
        }
    }

    return null;
}

async function loadProfile() {
    const userId = localStorage.getItem("userId");
    const token = localStorage.getItem("token");

    if (userId === null || token === null) {
        window.location.href = "index.html";
        return;
    }

    const response = await fetch(apiUrl + "/users/" + userId);

    if (!response.ok) {
        showProfileMessage("No se ha podido cargar el usuario.", true);
        return;
    }

    const user = await response.json();
    document.getElementById("profileId").value = user.id;
    document.getElementById("profileEmail").value = user.email;
    document.getElementById("profileName").value = user.name;
    document.getElementById("profileCreatedAt").value = user.created_at || "";
    showAvatar(user.avatar_url);
}

async function updateUser(event) {
    event.preventDefault();

    const token = localStorage.getItem("token");
    const id = Number(document.getElementById("profileId").value);
    const name = document.getElementById("profileName").value;
    const email = document.getElementById("profileEmail").value;
    const updateUserRequest = {
        id: id,
        name: name,
        email: email,
    };

    const response = await fetch(apiUrl + "/update_user", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        },
        body: JSON.stringify(updateUserRequest),
    });

    if (!response.ok) {
        showProfileMessage("No se ha podido actualizar el usuario.", true);
        return;
    }

    localStorage.setItem("email", email);
    showProfileMessage("Usuario actualizado.", false);
}

async function changeAvatar() {
    const token = localStorage.getItem("token");
    const fileInput = document.getElementById("avatarFile");

    if (fileInput.files.length === 0) {
        showProfileMessage("Selecciona un archivo primero.", true);
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch(apiUrl + "/storage/avatar", {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token,
        },
        body: formData,
    });

    if (!response.ok) {
        showProfileMessage("No se ha podido cambiar el avatar.", true);
        return;
    }

    const data = await response.json();
    showAvatar(data.avatar_url);
    showProfileMessage("Avatar actualizado.", false);
}

async function deleteUser() {
    const token = localStorage.getItem("token");
    const userId = localStorage.getItem("userId");

    const response = await fetch(apiUrl + "/delete_user?id=" + userId, {
        method: "DELETE",
        headers: {
            "Authorization": "Bearer " + token,
        },
    });

    if (!response.ok) {
        showProfileMessage("No se ha podido eliminar el usuario.", true);
        return;
    }

    localStorage.clear();
    window.location.href = "index.html";
}

async function loadInfoFile() {
    const response = await fetch(apiUrl + "/files/info");
    const fileInfo = document.getElementById("fileInfo");
    showInfoView();

    if (!response.ok) {
        fileInfo.textContent = "No se ha podido leer el fichero.";
        return;
    }

    const data = await response.json();
    fileInfo.textContent = data.content;
}

function showInfoView() {
    document.getElementById("accountView").style.display = "none";
    document.getElementById("infoView").style.display = "block";
    document.getElementById("loadInfoButton").className = "menu-button active";
    document.getElementById("accountButton").className = "menu-button";
}

function showAccountView() {
    document.getElementById("accountView").style.display = "block";
    document.getElementById("infoView").style.display = "none";
    document.getElementById("loadInfoButton").className = "menu-button";
    document.getElementById("accountButton").className = "menu-button active";
}

function showAvatar(avatarUrl) {
    const avatarImage = document.getElementById("avatarImage");
    const emptyAvatar = document.getElementById("emptyAvatar");

    if (avatarUrl === null || avatarUrl === undefined || avatarUrl === "") {
        avatarImage.style.display = "none";
        emptyAvatar.style.display = "flex";
        return;
    }

    avatarImage.onerror = function () {
        avatarImage.style.display = "none";
        emptyAvatar.style.display = "flex";
        emptyAvatar.textContent = "Avatar error";
    };

    const publicAvatarUrl = avatarUrl.replace(
        ".storage.supabase.co/storage/v1/s3",
        ".supabase.co/storage/v1/object/public",
    );

    avatarImage.src = publicAvatarUrl + "?time=" + new Date().getTime();
    avatarImage.style.display = "block";
    emptyAvatar.style.display = "none";
}

function showProfileMessage(text, isError) {
    const message = document.getElementById("profileMessage");
    message.textContent = text;

    if (isError) {
        message.className = "profile-message error";
    } else {
        message.className = "profile-message ok";
    }
}

function logout() {
    localStorage.clear();
    window.location.href = "index.html";
}
