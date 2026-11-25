import json,re,sys
ACC={
'l01':[0,1,2,3,4,5,6,7,8,11,12,13],
'l02':[0,1,2,3,4,5,6,7,8,9,10,11,15,16,18],
'l03':[0,1,2,3,5,7,9,12],
'l04':[0,1,2,3,4,6,7,8,12,14,15,16,17],
'l05':[0,1,2,4,6,14,15],
'l06':[0,1,6],
'l06b':[1,2,3,6,7,8,9],
'l07':[0,6,8,14,19],
'l08':[0,1,2,3,4,5,8,16,17],
'l08b':[0,1],
'l09':[0,1,2,3,4,5,6],
'l10':[0,1,3,5,6,7,8,9,10,14,16,18],
'l11':[0,1,2,4,9,12,16],
}
TAG=r'(?:<[^>]+>)*'
def find(s,sent):
    if s.count(sent)==1: i=s.index(sent); return i,i+len(sent)
    if s.count(sent)>1: return 'multi'
    pat=TAG.join(re.escape(c) for c in sent)
    pat=pat.replace(re.escape('&'),'&(?:amp;)?').replace(re.escape('<'),'(?:<|&lt;)').replace(re.escape('>'),'(?:>|&gt;)')
    m=list(re.finditer(pat,s))
    if len(m)==1: return m[0].start(),m[0].end()
    return 'multi' if m else None
tot=0;fail=[]
for l,ids in ACC.items():
    d=json.load(open(f'notes/sweep/{l}.json')); p=f'docs/{l}.html'; s=open(p).read()
    qa=s.index('<script type="application/json" id="quiz">') if 'id="quiz"' in s else len(s)
    body,tail=s[:qa],s[qa:]
    for i in ids:
        r=find(body,d[i]['sentence'])
        if not isinstance(r,tuple): fail.append((l,i,r,d[i]['sentence'])); continue
        a,b=r; seg=body[a:b]
        # 保留跨出去的標籤配對：只刪文字，留下 seg 內的標籤再清空殼
        keep=''.join(re.findall(r'<[^>]+>',seg))
        body=body[:a]+keep+body[b:]; tot+=1
    for _ in range(3):
        body=re.sub(r'<(strong|b|em|code|span)>\s*</\1>','',body)
        body=re.sub(r'<p(?: class="[^"]*")?>\s*</p>\n?','',body)
        body=re.sub(r'<li>\s*</li>\n?','',body)
    open(p,'w').write(body+tail)
print(tot); [print(f) for f in fail]
