import json
L=json.load(open("lines.json"))
LEAD={"intro":4.0,"miracle":3.2}; GAP=1.5; TAIL={"intro":1.6,"love":2.5}
gapx={"miracle":1.8}
scenes=[];t=0.0;cur=None
for l in L:
    if cur is None or cur["id"]!=l["scene"]:
        if cur: cur["end"]=round(t-GAP+TAIL.get(cur["id"],1.6),3); t=cur["end"]
        cur={"id":l["scene"],"start":round(t,3),"lines":[]}; scenes.append(cur)
        t+=LEAD.get(l["scene"],2.6)
    cur["lines"].append({"t":round(t,3),"e":round(t+l["dur"],3),"text":l["text"],"file":l["file"]})
    t+=l["dur"]+gapx.get(l["scene"],GAP)
cur["end"]=round(t-GAP+TAIL.get(cur["id"],1.6),3)
scenes.append({"id":"outro","start":cur["end"],"end":round(cur["end"]+9.0,3),"lines":[]})
json.dump(scenes,open("tl.json","w"),ensure_ascii=False,indent=1)
for s in scenes: print(s["id"],round(s["start"],1),round(s["end"],1),[x["t"] for x in s["lines"]])
