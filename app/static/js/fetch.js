fetch('/account/101-001-31017856-001')
  .then(res => res.text())
  .then(text => console.log(text));