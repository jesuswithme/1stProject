s=open("tpl.html").read().replace("__TL__",open("tl.json").read())
open("index.html","w").write(s)
