let authMode = 'login'; // 'login' または 'signup'

/* ---------- LocalStorage操作 ---------- */
function loadUsers(){
  try { return JSON.parse(localStorage.getItem('laundry_users') || '{}'); }
  catch(e) { return {}; }
}
function saveUsers(u){
  try { localStorage.setItem('laundry_users', JSON.stringify(u)); }
  catch(e) {}
}

// 簡易ハッシュ関数（ローカルファイル実行時の暗号化エラーを回避）
function simpleHash(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash |= 0;
  }
  return hash.toString(16);
}

/* ---------- メッセージ表示 ---------- */
function showAuthError(msg){
  const el = document.getElementById('authError');
  if (el) {
    el.classList.remove('success');
    el.textContent = msg;
    el.style.display = 'block';
  }
}
function showAuthSuccess(msg){
  const el = document.getElementById('authError');
  if (el) {
    el.classList.add('success');
    el.textContent = msg;
    el.style.display = 'block';
  }
}
function clearAuthError(){
  const el = document.getElementById('authError');
  if (el) {
    el.style.display = 'none';
    el.classList.remove('success');
  }
}

/* ---------- 画面切替処理 ---------- */
function switchMode(targetMode){
  authMode = targetMode;
  clearAuthError();

  const isSignup = (authMode === 'signup');

  const tabLogin = document.getElementById('tabLogin');
  const tabSignup = document.getElementById('tabSignup');
  if (tabLogin) tabLogin.classList.toggle('active', !isSignup);
  if (tabSignup) tabSignup.classList.toggle('active', isSignup);

  const authTitle = document.getElementById('authTitle');
  if (authTitle) authTitle.textContent = isSignup ? '新規アカウント登録' : 'ログイン';

  const titleIcon = document.getElementById('titleIcon');
  if (titleIcon) titleIcon.className = isSignup ? 'ti ti-user-plus' : 'ti ti-user-circle';

  const submitBtn = document.getElementById('authSubmitBtn');
  if (submitBtn) submitBtn.textContent = isSignup ? '登録してはじめる' : 'ログイン';

  const toggleBtn = document.getElementById('authToggleBtn');
  if (toggleBtn) {
    toggleBtn.textContent = isSignup
      ? 'すでにアカウントをお持ちの方はこちら（ログイン）'
      : 'アカウントをお持ちでない方はこちら（新規登録）';
  }

  const usernameField = document.getElementById('usernameField');
  if (usernameField) usernameField.style.display = isSignup ? 'block' : 'none';

  const passwordConfirmField = document.getElementById('passwordConfirmField');
  if (passwordConfirmField) passwordConfirmField.style.display = isSignup ? 'block' : 'none';

  // パスワード欄の autocomplete をモードに合わせる
  const passwordEl = document.getElementById('authPassword');
  if (passwordEl) passwordEl.autocomplete = isSignup ? 'new-password' : 'current-password';
}

function toggleAuthMode(){
  switchMode(authMode === 'login' ? 'signup' : 'login');
}

/* ---------- 送信実行処理 ---------- */
function handleAuthSubmit(){
  clearAuthError();

  const usernameEl = document.getElementById('authUsername');
  const emailEl = document.getElementById('authEmail');
  const passwordEl = document.getElementById('authPassword');
  const passwordConfirmEl = document.getElementById('authPasswordConfirm');

  const username = usernameEl ? usernameEl.value.trim() : '';
  const email = emailEl ? emailEl.value.trim().toLowerCase() : '';
  const password = passwordEl ? passwordEl.value : '';
  const passwordConfirm = passwordConfirmEl ? passwordConfirmEl.value : '';

  if (authMode === 'signup' && !username) {
    showAuthError('ユーザー名を入力してください。');
    return;
  }
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showAuthError('有効なメールアドレスを入力してください。');
    return;
  }
  if (password.length < 6) {
    showAuthError('パスワードは6文字以上で入力してください。');
    return;
  }

  try {
    const users = loadUsers();

    if (authMode === 'signup') {
      if (password !== passwordConfirm) {
        showAuthError('確認用パスワードが一致しません。');
        return;
      }
      if (users[email]) {
        showAuthError('このメールアドレスはすでに登録されています。');
        return;
      }

      const hash = simpleHash(password);
      users[email] = { username, hash, createdAt: new Date().toISOString() };
      saveUsers(users);

      // 登録完了 → ログイン画面へ自動切り替え
      onSignupSuccess(email, username);
    } else {
      const rec = users[email];
      if (!rec) {
        showAuthError('アカウントが見つかりません。新規登録してください。');
        return;
      }

      const hash = simpleHash(password);
      if (hash !== rec.hash) {
        showAuthError('メールアドレスまたはパスワードが違います。');
        return;
      }

      onLoginSuccess(email, rec.username);
    }
  } catch (e) {
    console.error(e);
    showAuthError('エラーが発生しました: ' + e.message);
  }
}

/* ---------- 成功時の処理 ---------- */
function onSignupSuccess(email, username){
  // 入力欄をクリア（メールアドレス以外）
  document.getElementById('authUsername').value = '';
  document.getElementById('authPassword').value = '';
  document.getElementById('authPasswordConfirm').value = '';

  // ログイン画面に切り替え（この中でメッセージが消えるので、成功表示は後に行う）
  switchMode('login');

  // メールアドレスは入力済みにして、パスワードだけ入力すればログインできる状態に
  document.getElementById('authEmail').value = email;
  showAuthSuccess('登録が完了しました！' + username + 'さん、ログインしてください。');
  document.getElementById('authPassword').focus();
}

function onLoginSuccess(email, username){
  localStorage.setItem('laundry_session', email);
  alert('おかえりなさい、' + username + 'さん！');
}

function continueAsGuest(){
  localStorage.setItem('laundry_session', '__guest__');
  alert('ゲストとして進みます');
}

// Enterキーで送信
document.addEventListener('keydown', function(e){
  if (e.key === 'Enter' && e.target.tagName === 'INPUT') handleAuthSubmit();
});