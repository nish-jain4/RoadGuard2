function logout(role) {
  clearToken(role);
  window.location.href = 'login.html';
}