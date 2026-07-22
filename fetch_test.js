fetch('http://127.0.0.1:3000').then(r => r.text()).then(t => console.log('HTML length:', t.length, t.substring(0, 100))).catch(e => console.error(e));
