fetch('/users/test')
  .then(res => res.text())
  .then(text => console.log(text));

fetch('/users/test/trade_accounts')
  .then(res => res.text())
  .then(text => console.log(text));

fetch('/users/test/trade_accounts/101-001-31017856-001')
  .then(res => res.text())
  .then(text => console.log(text));