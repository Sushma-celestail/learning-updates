function loadScript(src,callback){
    let script=document.createElement('script');
    script.src=src;
    document.head.append(script);
    script.onload=()=>callback(script);
}

loadScript('hello.js',function(script){
    console.log(`the script ${script.src} is loaded`);
    sayHi();
}) 