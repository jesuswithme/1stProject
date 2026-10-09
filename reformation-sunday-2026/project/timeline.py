import json,subprocess
def dur(f): return float(subprocess.check_output(["ffprobe","-v","0","-show_entries","format=duration","-of","csv=p=0",f]))
# id, start time (s), display text
L=[("c1",7.0,"세상은 빠르게 변하고 있습니다."),("c2",14.5,"교회는 무엇을 붙들어야 합니까?"),("c3",21.5,"무엇은 다시 개혁되어야 합니까?"),
("k1",37.9,"1517"),("k2",41.0,"한 사람이 문을 두드렸다."),("k3",44.8,"교회를 무너뜨리기 위해서가 아니라"),("k4",48.3,"교회를 깨우기 위해서였다."),
("s1",56.1,"SOLA GRATIA"),("s2",63.0,"SOLA FIDE"),("s3",69.9,"SOLA SCRIPTURA"),("s4",76.8,"SOLUS CHRISTUS"),("s5",83.7,"SOLI DEO GLORIA"),
("r1",95.5,"그러나 종교개혁은 1517년에 끝났을까요?"),("r2",101.6,"아닙니다."),("r3",106.0,"ECCLESIA REFORMATA, SEMPER REFORMANDA"),("r4",112.6,"개혁된 교회는 계속 개혁되어야 한다."),
("d0",131.5,"오늘 무엇이 다시 형성되어야 하는가?"),("d1",137.6,"나의 삶에서?"),("d2",141.3,"우리 가정에서?"),("d3",145.0,"우리 교회에서?"),("d4",148.7,"우리 공동체에서?"),("d5",152.6,"우리 시대와 세계에서?"),("d6",157.0,"우리 시대의 95개조"),("d7",162.4,"오늘 우리가 다시 붙여야 할 한 문장은 무엇입니까?"),
("f1",172.5,"믿는 것을 고백하고"),("f2",177.0,"고백한 것을 실천하고"),("f3",181.5,"실천한 것이 우리를 형성하며"),("f4",186.0,"형성된 삶을 다음 세대에 전수한다."),
("e1",223.2,"개혁은 아직 끝나지 않았습니다."),("e2",226.6,"성령께서 오늘도 교회를 다시 형성하고 계십니다."),("e3",233.6,"고백에서 삶으로. 교회에서 가정으로. 우리에게서 다음 세대로."),
("p",240.0,"주여, 우리를 다시 개혁하소서."),
]
out={}
for i,t,txt in L:
    f=f"tts/{i}.mp3" if i!="p" else "tts/p4.mp3"
    d=dur(f); out[i]={"t":t,"e":round(t+d,3),"text":txt}
# check overlaps
ks=list(out)
for a,b in zip(ks,ks[1:]):
    if out[a]["e"]>out[b]["t"]-0.4: print("TIGHT",a,b,out[a]["e"],out[b]["t"])
SFX={"knock":[31.5,34.5,36.5,55.4,62.3,69.2,76.1,83.0,213.0],"cut":30.0,"door":214.6,"END":250.0}
json.dump({"L":out,"SFX":SFX},open("tl.json","w"),ensure_ascii=False,indent=1)
for k,v in out.items(): print(k,v["t"],v["e"])
