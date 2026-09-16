const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
const out = path.join(root, 'outputs');
fs.mkdirSync(out, {recursive:true});
const phase = process.argv[2] || 'before';
const base = 'http://127.0.0.1:8765/index.html';
(async()=>{
 const browser = await chromium.launch({headless:true});
 const report={phase,views:[],errors:[]};
 try {
  for (const width of [1440,390,768]) {
   const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});
   page.on('pageerror',e=>report.errors.push(e.message));
   await page.goto(base,{waitUntil:'load',timeout:45000});
   await page.waitForFunction(()=>document.querySelector('.name').textContent.trim()==='Pr. Dr. Eng. CHERIF Adnane');
   await page.evaluate(()=>document.fonts.ready);
   await page.screenshot({path:path.join(out,`${phase}-${width}.png`)});
   const info=await page.evaluate(()=>{
    const selectors=['.cv-container','.sidebar','.main-content','.name','.profile-section','.profile-img','.title','.section-title','.nav-menu','.nav-container','.nav-logo','.nav-links','.nav-toggle','#mobileMenu','.main-content .section','.main-content .experience-item','.main-content .job-title','.qr-card','.stats-grid','.stat-card','.annex-item','table'];
    const vals=selectors.map(sel=>{const el=document.querySelector(sel);if(!el)return {sel,missing:true};const s=getComputedStyle(el),r=el.getBoundingClientRect();return{sel,box:[r.x,r.y,r.width,r.height].map(Math.round),display:s.display,font:s.fontFamily,size:s.fontSize,color:s.color,bg:s.backgroundImage==='none'?s.backgroundColor:s.backgroundImage,padding:s.padding,margin:s.margin,columns:s.gridTemplateColumns,position:s.position,shadow:s.boxShadow};});
    const anchors=[...document.querySelectorAll('.nav-links a')].map(a=>({href:a.getAttribute('href'),exists:!!document.querySelector(a.getAttribute('href'))}));
    return{width:innerWidth,scrollWidth:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight,styles:vals,anchors,images:[...document.images].filter(i=>!i.naturalWidth).map(i=>i.getAttribute('src')),counts:{sections:document.querySelectorAll('.section').length,images:document.querySelectorAll('.cv-wrapper img').length,videos:document.querySelectorAll('video').length,tables:document.querySelectorAll('table').length},headings:[...document.querySelectorAll('.main-content>.section>.section-title')].map(x=>x.textContent.trim())};
   });
   if(width===1440){
    await page.evaluate(()=>{const e=document.querySelector('.annex-item');window.scrollTo({top:e.getBoundingClientRect().top+scrollY-100,behavior:'instant'});});
    await page.screenshot({path:path.join(out,`${phase}-annex.png`)});
   }
   if(width===390){
    await page.locator('#navToggle').click();
    info.menuOpen=await page.locator('#mobileMenu').evaluate(e=>e.classList.contains('active')&&getComputedStyle(e).display!=='none');
    await page.locator('#mobileMenu a[href="#experience"]').click();
    await page.waitForFunction(()=>!document.querySelector('#mobileMenu').classList.contains('active'));
    await page.waitForFunction(()=>Math.abs(document.querySelector('#experience').getBoundingClientRect().top-70)<5,{},{timeout:12000});
    info.menuClosed=true;
    await page.screenshot({path:path.join(out,`${phase}-mobile-experience.png`)});
   }
   report.views.push(info);
   await page.close();
  }
  fs.writeFileSync(path.join(out,`${phase}-checks.json`),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report.views.map(v=>({width:v.width,scrollWidth:v.scrollWidth,height:v.height,counts:v.counts,imagesFailed:v.images,anchors:v.anchors,menuOpen:v.menuOpen,menuClosed:v.menuClosed})),null,2));
  console.log('Page errors:',JSON.stringify(report.errors));
  console.log('Desktop styles:',JSON.stringify(report.views[0].styles,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
