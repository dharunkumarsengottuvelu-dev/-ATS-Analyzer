const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new', executablePath: 'C:\\Users\\haris\\.cache\\puppeteer\\chrome\\win64-150.0.7871.24\\chrome-win64\\chrome.exe' });
  const page = await browser.newPage();
  
  await page.setViewport({ width: 1024, height: 768 });
  
  await page.goto('http://localhost:3000/upload', { waitUntil: 'networkidle0' });
  
  await new Promise(r => setTimeout(r, 2000));
  
  const results = await page.evaluate(() => {
    function getCssString(el) {
      const computed = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      const tagName = el.tagName.toLowerCase();
      const cls = el.className && typeof el.className === 'string' ? '.' + el.className.split(' ').filter(c => c).join('.') : '';
      
      const props = [
        'display', 'position', 'width', 'min-width', 'max-width',
        'overflow-x', 'overflow-y', 'flex', 'flex-grow', 'flex-shrink', 'flex-basis',
        'grid-template-columns', 'gap', 'margin', 'padding', 'transform',
        'left', 'right'
      ];
      
      const vals = {};
      for (const p of props) {
        vals[p] = computed.getPropertyValue(p);
      }
      
      return {
        tag: tagName + (cls.length > 50 ? cls.substring(0, 50) + '...' : cls),
        rect: {
          width: rect.width,
          height: rect.height,
          right: rect.right,
          left: rect.left
        },
        scrollWidth: el.scrollWidth,
        clientWidth: el.clientWidth,
        isOverflowingScreen: rect.right > window.innerWidth,
        css: vals
      };
    }

    const tree = [];
    
    function walk(node, depth) {
      if (node.nodeType !== Node.ELEMENT_NODE) return;
      if (node.tagName === 'SCRIPT' || node.tagName === 'STYLE') return;
      
      const info = getCssString(node);
      
      tree.push({
        depth,
        tag: info.tag,
        isOverflowing: info.isOverflowingScreen,
        rect: info.rect,
        scrollWidth: info.scrollWidth,
        clientWidth: info.clientWidth,
        css: info.css
      });
      
      for (const child of node.childNodes) {
        walk(child, depth + 1);
      }
    }
    
    walk(document.body, 0);
    return {
      windowWidth: window.innerWidth,
      docScrollWidth: document.documentElement.scrollWidth,
      tree: tree.filter(t => t.rect.width > 0 && t.rect.height > 0)
    };
  });
  
  console.log(JSON.stringify(results, null, 2));
  await browser.close();
})();
