"""Build with verbatim client copy and audit all 63 PowerPoint slides."""
import html, json, pathlib, re, zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).parent
DECK = pathlib.Path('C:/Users/USER/Downloads/Chunmun_Kamal_Coaching__Midlife_v2.1.pptx')
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
slides = []
if DECK.exists():
    with zipfile.ZipFile(DECK) as archive:
        for number in range(1,64):
            tree = ET.fromstring(archive.read(f'ppt/slides/slide{number}.xml'))
            paragraphs = []
            for paragraph in tree.findall('.//a:p',NS):
                value = ''.join((node.text or '') if node.tag == f'{{{NS["a"]}}}t' else '\n' for node in paragraph.iter() if node.tag in (f'{{{NS["a"]}}}t',f'{{{NS["a"]}}}br'))
                if value.strip(): paragraphs.append(value.strip())
            slides.append({'number':number,'blocks':paragraphs})
    (ROOT/'revisions.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2),encoding='utf-8')
else: slides=json.loads((ROOT/'revisions.json').read_text(encoding='utf-8'))
assert len(slides)==63
audit={}
def source(n,i):return slides[n-1]['blocks'][i]
def escaped(value):return html.escape(value.replace('\u200b',''))
def mark(n,i,disposition,reason=''):
    audit.setdefault((n,i),{'slide':n,'block':i,'text':source(n,i),'uses':[]})['uses'].append({'disposition':disposition,'reason':reason})
def attr(n,i):return f'data-source-slide="{n}" data-source-block="{i}"'
def text(n,i,tag='p',cls=''):
    mark(n,i,'verbatim website copy')
    return f'<{tag} {attr(n,i)} class="{cls}">{escaped(source(n,i)).replace(chr(10),"<br>")}</{tag}>'
def link(n,i,href,cls='button'):
    mark(n,i,'verbatim website copy')
    return f'<a {attr(n,i)} class="{cls}" href="{href}">{escaped(source(n,i)).replace(chr(10),"<br>")}</a>'
def call(n,first,second,href='book-a-call.html'):
    mark(n,first,'verbatim website copy');mark(n,second,'verbatim website copy')
    return f'<a class="button" href="{href}"><span {attr(n,first)}>{escaped(source(n,first))}</span> <span {attr(n,second)}>{escaped(source(n,second))}</span></a>'
def note(n,i,reason):mark(n,i,'design / implementation note',reason)
def ignored(n,i):
    s=source(n,i)
    if not s.strip('\u200b '):note(n,i,'Empty formatting paragraph');return True
    if re.search('placeholder',s,re.I):note(n,i,'Visual placeholder implemented as imagery or page layout');return True
    if s in ['Logo','Logo 1']:note(n,i,'Logo placement; existing black logo used');return True
    return False
def render(n,indices=None,headings=()):
    indices=list(range(len(slides[n-1]['blocks'])) if indices is None else indices)
    result=[];j=0
    while j<len(indices):
        i=indices[j];s=source(n,i)
        if ignored(n,i):j+=1;continue
        if s=='Book Your Midlife' and j+1<len(indices) and source(n,indices[j+1])=='Recharge Call':
            result.append(call(n,i,indices[j+1]));j+=2;continue
        if s=='Workplace Wellbeing' and j+1<len(indices) and source(n,indices[j+1])=='Discovery Call':
            result.append(call(n,i,indices[j+1],'contact.html?programme=Workplace%20Wellbeing'));j+=2;continue
        if s in ['(…continued on next slide)','Delaying help slide cpntent continued…','Landing Page – S3','About Me - 1','About Me - 2','Testimonial Banner']:
            note(n,i,'Presentation layout / continuation label');j+=1;continue
        if s.startswith('Discover your unique root cause') and '\n' not in s:
            mark(n,i,'verbatim website copy');title='Discover your unique root cause';body=s[len(title):]
            result.append(f'<div {attr(n,i)} class="copy-block"><h3>{escaped(title)}</h3><p>{escaped(body)}</p></div>')
        elif '\n' in s and s.split('\n',1)[0].startswith(('Path ','Who it','Your outcome','Discover your unique','Tailored Wellbeing','Ongoing Support')):
            mark(n,i,'verbatim website copy');a,b=s.split('\n',1)
            result.append(f'<div {attr(n,i)} class="copy-block"><h3>{escaped(a)}</h3><p>{escaped(b).replace(chr(10),"<br>")}</p></div>')
        else:result.append(text(n,i,'h3' if i in headings else 'p','micro' if s=='30 mins. No pressure. Just clarity.' else ''))
        j+=1
    return ''.join(result)
def section(n,body,cls=''):return f'<section class="section {cls}" data-deck-slide="{n}"><div class="container">{body}</div></section>'
def heading(n,i=0,tag='h2'):return text(n,i,tag)
def photo(body,image='site-11.png'):return f'<div class="split photo-right"><div>{body}</div><div class="photo"><img src="assets/{image}" alt="" loading="lazy"></div></div>'
def icon(kind='leaf'):
    paths={'leaf':'M12 34C10 15 22 7 40 8c0 20-8 31-28 26ZM12 34l18-16', 'person':'M24 8a7 7 0 1 0 0 14 7 7 0 0 0 0-14ZM10 40v-5a14 14 0 0 1 28 0v5', 'briefcase':'M7 18h34v23H7zM17 18v-7h14v7M7 27c12 5 22 5 34 0M21 27h6v6h-6z', 'sun':'M24 15a9 9 0 1 0 0 18 9 9 0 0 0 0-18ZM24 4v5M24 39v5M4 24h5M39 24h5M10 10l4 4M34 34l4 4M10 38l4-4M34 14l4-4', 'heart':'M24 39 8 23C-2 11 14 3 24 15 34 3 50 11 40 23Z', 'moon':'M36 33A18 18 0 0 1 15 8a18 18 0 1 0 21 25Z', 'chat':'M7 9h34v25H22L11 42v-8H7zM14 17h20M14 25h13', 'steps':'M6 38h12V27h12V16h12M31 7h11v11', 'target':'M24 7a17 17 0 1 0 0 34 17 17 0 0 0 0-34ZM24 15a9 9 0 1 0 0 18 9 9 0 0 0 0-18ZM24 21v6M21 24h6'}
    return f'<svg class="topic-icon" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{paths.get(kind,paths["leaf"])}"/></svg>'
def cta():return section(20,heading(20)+render(20,range(1,5)),'gold-band')
nav=[(6,4,'about.html'),(6,7,'coaching.html'),(6,9,'workplace.html'),(6,5,'case-studies.html'),(6,6,'blog.html'),(6,8,'contact.html')]
def page(name,title,body):
    links=''.join(link(n,i,url,'nav-link') for n,i,url in nav)
    doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{escaped(source(6,2))}"><title>{title} | Chunmun Kamal</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Libre+Caslon+Display&display=swap" rel="stylesheet"><link rel="stylesheet" href="styles.css"><script src="script.js" defer></script></head><body><a class="skip" href="#main">Skip to content</a><div class="topbar">{escaped(source(7,4))}</div><header><div class="container header"><a class="brand" href="index.html" aria-label="Chunmun Kamal home"><img src="assets/logo.png" alt="Chunmun Kamal"></a><button class="menu-toggle" aria-controls="navigation" aria-expanded="false">Menu <span aria-hidden="true">☰</span></button><nav id="navigation" aria-label="Main navigation">{links}</nav></div></header><main id="main">{body}</main><footer><div class="container footer-top"><div><a class="brand" href="index.html"><img src="assets/logo.png" alt="Chunmun Kamal"></a>{text(6,1)}</div><div><a href="mailto:hello@chunmunkamal.com">hello@chunmunkamal.com</a></div><div>{links}</div></div><div class="container footer-bottom"><span>© 2026 Chunmun Kamal.</span></div></footer></body></html>'''
    doc=re.sub(r'<div class="topbar">.*?</div>','',doc,count=1)
    (ROOT/name).write_text(doc,encoding='utf-8')

for n in range(1,6):
    for i in range(len(slides[n-1]['blocks'])):note(n,i,'Design guidance reviewed: colours, black logo, imagery, reference layout and fonts')
for i in [0,14,16]:ignored(6,i)
hero=f'<section class="hero" data-deck-slide="6"><div class="container hero-grid"><div class="hero-copy"><div class="hero-panel">{text(6,1,"p","eyebrow")}{text(6,10,"h1")}{text(6,2,"p","lead")}{text(6,3,"blockquote","hero-quote")}</div>{link(6,15,"mailto:hello@chunmunkamal.com?subject=Midlife%20Energy%2C%20Sleep%20and%20Resilience%20Quiz","button quiz-link")}{text(6,13,"p","micro")}</div><div class="hero-visual">{call(6,11,12)}<div class="photo-frame"><img src="assets/site-11.png" alt="" fetchpriority="high"></div></div></div></section>'
intro=section(7,'<div class="intro-text">'+render(7,range(4))+'</div>'+text(7,4,'h2')+heading(7,14)+'<div class="cards two"><article class="service">'+heading(7,7,'h3')+call(7,8,9)+text(7,5,'p','micro')+'</article><article class="service gold">'+heading(7,11,'h3')+call(7,11,12,'contact.html?programme=Workplace%20Wellbeing')+text(7,13,'p','micro')+'</article></div>')
for i in [6,10]:ignored(7,i)
page('index.html',source(6,1),hero+intro+section(7,text(7,15),'navy credentials'))

coaching=section(8,heading(8,0,'h1'),'page-hero center')
coaching+=section(9,'<div class="audience-layout"><aside class="audiences">'+''.join('<div>'+icon(k)+text(9,i)+'</div>' for k,i in [('briefcase',1),('leaf',3),('person',5)])+'</aside><div>'+heading(9,18)+render(9,[6,7])+heading(9,17,'h3')+'<ul class="symptoms">'+''.join(text(9,i,'li') for i in range(8,17))+'</ul></div></div>')
for i in [0,2,4]:ignored(9,i)
coaching+=section(10,'<div class="reading">'+render(10,[0,3,2])+heading(10,1)+render(10,[6,7,4,5])+'</div>')
coaching+=section(11,render(11,[0])+'<div class="reassurance three">'+''.join('<article class="tone-'+tone+'">'+icon(kind)+text(11,i,'h3')+'</article>' for i,tone,kind in [(1,'slate','heart'),(3,'rose','sun'),(2,'gold','leaf')])+'</div>'+render(11,[4]))
coaching+=section(12,heading(12,16)+heading(12,0)+render(12,[15])+'<div class="framework-columns">'+''.join('<article class="framework-column">'+text(12,head,'h3','framework-title')+''.join('<div class="framework-item">'+icon(kind)+render(12,ids,headings=ids[:1])+'</div>' for ids,kind in pairs)+'</article>' for head,pairs in [(10,[([3],'target'),([8,9],'leaf')]),(11,[([1,2],'sun'),([12,13],'heart')]),(14,[([6,7],'moon'),([4,5],'chat')])])+'</div>')
coaching+=section(13,heading(13,7)+photo(''.join('<div class="approach-item tone-'+tone+'">'+icon(kind)+'<div>'+render(13,ids,headings=ids[:1])+'</div></div>' for tone,kind,ids in [('slate','target',[0,1]),('sage','person',[2,3]),('gold','steps',[4,5])])))
ignored(13,6)
coaching+=section(14,photo(''.join('<div class="approach-item tone-'+tone+'">'+icon(kind)+'<div>'+render(14,ids,headings=ids[:1])+'</div></div>' for tone,kind,ids in [('rose','chat',[0,1]),('slate','heart',[2,3])])))
ignored(14,4)
coaching+=section(15,'<div class="stats deck-stats"><div>'+text(15,0,'h3')+text(15,1,'h3')+'</div><div>'+text(15,2,'h3')+'</div><div>'+text(15,3,'h3')+'</div></div>','navy')
seen={};cost=[]
for n in [16,17,18]:
    for i,s in enumerate(slides[n-1]['blocks']):
        if s=='Delaying help slide cpntent continued…':note(n,i,'Continuation label');continue
        if s in seen:mark(n,i,'duplicate copy retained elsewhere',f'Same text as slide {seen[s][0]}, block {seen[s][1]}')
        else:seen[s]=(n,i);cost.append(text(n,i,'h3' if len(s)<65 else 'p'))
coaching+=section(16,heading(16,2)+heading(16,1,'h3')+heading(16,0,'h3')+'<div class="cost-columns">'+''.join('<article>'+render(16,ids,headings=ids[:1])+'</article>' for ids in [[3,4],[5],[6,7],[8,9],[10,11],[12,13]])+'</div>'+text(18,2,'p','micro'))
coaching+=section(19,heading(19)+'<div class="process-columns">'+''.join('<article>'+icon(kind)+render(19,ids,headings=ids[:1])+'</article>' for kind,ids in [('chat',[1,2,3,4]),('heart',[5,6,7]),('sun',[8,9,10])])+'</div>')+cta()
for n in [21,22,23]:
    coaching+=section(n,'<div class="testimonial-columns"><blockquote>'+render(n,[0])+'</blockquote><blockquote>'+render(n,[1,2])+'</blockquote></div>')
    if n==21:note(21,3,'Presentation label identifying testimonial banner')
coaching+=section(24,heading(24),'page-hero center')+section(25,render(25,[0])+'<ul>'+''.join(text(25,i,'li') for i in range(1,8))+'</ul>')
for group in [[26,27],[28,29,30],[31,32]]:
    content='';seen_group={}
    for n in group:
        ids=[]
        for i,s in enumerate(slides[n-1]['blocks']):
            if s in seen_group and s not in ['Book Your Midlife','Recharge Call','30 mins. No pressure. Just clarity.','\u200b']:
                prev=seen_group[s];mark(n,i,'duplicate copy retained elsewhere',f'Same text as slide {prev[0]}, block {prev[1]}')
            else:seen_group[s]=(n,i);ids.append(i)
        content+=render(n,ids,headings=tuple(i for i,s in enumerate(slides[n-1]['blocks']) if s in ["What's included",'Your outcome','Follow up support']))
    coaching+=section(group[0],'<div class="reading pathway">'+content+'</div>','cream' if group[0]!=28 else '')
faq=heading(33)+heading(34,4)+heading(34,5)
for n in [34,35,37,38,39,40,41,42,43]:
    limit=4 if n==34 else len(slides[n-1]['blocks'])
    answer=render(n,range(1,limit))
    if n==35:answer+=render(36,headings=(0,1,3,5,7,9,10,13,15,17))
    faq+='<details>'+text(n,0,'summary')+'<div>'+answer+'</div></details>'
coaching+=section(33,'<div class="faq">'+faq+'</div>','cream')+cta()
page('coaching.html','1:1 Coaching',coaching)
workplace=section(44,heading(44,0,'h1'),'page-hero center')+section(45,heading(45)+'<div class="workplace-steps">'+''.join('<article>'+icon(kind)+'<div>'+render(45,ids,headings=ids[:1])+'</div></article>' for kind,ids in [('chat',[2,3]),('person',[4]),('leaf',[5])])+'</div>'+render(45,[1,6,7,8,9]))
page('workplace.html','Workplace Wellbeing',workplace)

cases=section(46,heading(46,0,'h1'),'page-hero center')
for n in range(47,53):
    b=slides[n-1]['blocks'];title=next(i for i,s in enumerate(b) if s.startswith('Case Study #'));reason=title+1;results=title+2
    cases+=section(n,heading(n,title)+text(n,reason,'p','lead')+'<div class="case-columns"><div class="case-work">'+heading(n,0,'h3')+'<ul>'+''.join(text(n,i,'li') for i in range(1,title))+'</ul></div><div class="case-quote">'+heading(n,results,'h3')+render(n,range(results+1,len(b)))+'</div></div>')
page('case-studies.html','Case Studies',cases)
about=section(53,heading(53,0,'h1'),'page-hero center')+section(54,render(54))+section(55,heading(55,4)+'<div class="credential-columns"><div>'+render(55,[0,1,2,3],headings=(1,)) + render(55,[5,6,7,8],headings=(5,))+'</div><div>'+render(55,[9,10,11,12,13,14,15],headings=(9,14))+'</div></div>')+section(56,heading(56,1)+'<div class="association-slots" aria-hidden="true"><div></div><div></div><div></div></div>')
for i in [0,2,3]:ignored(56,i)
about+=section(57,heading(57,2)+'<div class="personal-columns">'+''.join('<article><img src="assets/'+image+'" alt="" loading="lazy">'+render(57,pair,headings=pair[:1])+'</article>' for image,pair in [('site-10.png',[0,1]),('site-6.png',[3,4]),('site-4.png',[5,6])])+'</div>')
for i in [7,8,9]:ignored(57,i)
page('about.html','About Me',about)

booking=section(58,heading(58,0,'h1'),'page-hero center')+section(59,heading(59)+render(59,[1,2])+link(59,5,source(59,5),'calendar-link')+'<div class="calendly-inline-widget" data-url="https://calendly.com/hello-chunmunkamal/30min" style="min-width:280px;height:760px"></div><script src="https://assets.calendly.com/assets/external/widget.js" async></script>')
for i in [3,4,6,7,8,9]:note(59,i,'Calendly integration implemented as widget plus direct calendar link')
booking+=section(60,heading(60)+'<div class="process-columns">'+''.join('<article>'+icon(kind)+render(60,pair,headings=pair[:1])+'</article>' for kind,pair in [('target',[4,5]),('heart',[6,7]),('steps',[8,9])])+'</div>')
for i in [1,2,3]:ignored(60,i)
page('book-a-call.html','Book Your Midlife Recharge Call',booking)
form='''<form id="contact-form"><div class="form-grid"><label>First name (required)<input name="firstName" autocomplete="given-name" required></label><label>Last name (required)<input name="lastName" autocomplete="family-name" required></label><label>Mobile phone (required)<input name="phone" type="tel" autocomplete="tel" required></label><label>Email (required)<input name="email" type="email" autocomplete="email" required></label></div><label>How did you hear about me ?<input name="source"></label><label>Which programme are you interested in?<select name="programme"><option value="">—</option><option>The Foundation</option><option>The Accelerator</option><option>The Mastery</option><option>Workplace Wellbeing</option></select></label><label>Your message<textarea name="message" rows="5"></textarea></label><button class="button" type="submit">Submit Responses</button><p id="form-status" role="status"></p></form>'''
for i in [0,1,2,8]:mark(61,i,'verbatim form copy','Name row split into two fields')
for i in [3,4,5]:mark(61,i,'form specification implemented','Public label retained; editor notes implemented as control type')
ignored(61,7)
page('contact.html','Contact',section(61,text(6,8,'h1'),'page-hero center')+section(61,heading(61,6,'h3')+text(61,9)+'<div class="deck-contact">'+form+'</div>'))
posts=json.loads((ROOT/'blog-source.json').read_text(encoding='utf-8'))
post=next(p for p in posts if 'stress' in p['title']['rendered'].lower())
blog_body=re.sub(r'<script\b[^>]*>.*?</script>','',post['content']['rendered'],flags=re.S|re.I)
note(63,0,'Existing stress article copied in full to blog.html')
page('blog.html','Blog',section(62,heading(62,0,'h1'),'page-hero center')+section(63,'<article class="blog-content"><h2>'+post['title']['rendered']+'</h2>'+blog_body+'</article>'))

missing=[(n,i,s) for n in range(1,64) for i,s in enumerate(slides[n-1]['blocks']) if (n,i) not in audit]
assert not missing,f'Unaccounted source blocks: {missing}'
report={'slide_count':63,'source':str(DECK),'policy':'Verbatim copy; authored spelling and punctuation preserved. Only layout whitespace changes. Design notes, placeholders and integration code are not public prose. Exact duplicates consolidated and documented.','blocks':list(audit.values())}
(ROOT/'content-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
class Reader(HTMLParser):
    def __init__(self):super().__init__();self.values=[]
    def handle_data(self,value):self.values.append(value)
def normal(s):return re.sub(r'\s+',' ',s.replace('\u200b','')).strip()
website=''
for p in ROOT.glob('*.html'):
    if p.name=='reference-site.html':continue
    reader=Reader();reader.feed(p.read_text(encoding='utf-8'));website+=' '+normal(' '.join(reader.values))
for item in audit.values():
    if any(u['disposition'] in ['verbatim website copy','duplicate copy retained elsewhere'] for u in item['uses']):
        assert normal(item['text']) in website,f'Copy mismatch on slide {item["slide"]}, block {item["block"]}'
destinations={**{n:'Design guidance' for n in range(1,6)},6:'index.html',7:'index.html',**{n:'coaching.html' for n in range(8,44)},44:'workplace.html',45:'workplace.html',**{n:'case-studies.html' for n in range(46,53)},**{n:'about.html' for n in range(53,58)},**{n:'book-a-call.html' for n in range(58,61)},61:'contact.html',62:'blog.html',63:'blog.html'}
lines=['# Audit of all 63 client slides','', 'Website copy is taken directly from the PowerPoint, without paraphrasing, shortening, correcting spelling, or changing punctuation. Authored line breaks are retained. Each source paragraph is tracked in `content-audit.json`.', '', '| Slide | Destination | Review |','| --- | --- | --- |']
for n in range(1,64):
    entries=[entry for entry in audit.values() if entry['slide']==n]
    copy_count=sum(any(use['disposition'].startswith('verbatim') for use in entry['uses']) for entry in entries)
    duplicate_count=sum(any(use['disposition']=='duplicate copy retained elsewhere' for use in entry['uses']) for entry in entries)
    note_count=len(entries)-copy_count-duplicate_count
    lines.append(f'| {n} | {destinations[n]} | {copy_count} copy blocks; {duplicate_count} identical duplicate blocks; {note_count} design / implementation blocks. Reviewed. |')
lines+=['','## Document details preserved','', '- Slides 16–18 overlap. Identical paragraphs are displayed once. Both authored heading variations are retained.', '- Slides 29–30 repeat the Accelerator outcome. The identical outcome is displayed once; the optional paid follow-up session is retained.', '- All six testimonials in slides 21–23 are included in full, as well as all six case studies in slides 47–52.', '- Both slides 51 and 52 say “Case Study #5”. This source numbering is preserved.', '- Source spelling and wording, including “Practioner”, “gaols” and “Taks”, are preserved.', '- Slide 56 supplies a memberships heading and three logo placeholders, but no association names or logos. The heading is present; no association has been invented.', '- Slides 1–5 are design instructions, not public-facing copy. Placeholder labels and presentation navigation labels are documented but not displayed.', '- Slide 59 supplies Calendly integration code, which is implemented rather than printed on the page.', '- Slide 61 describes form controls. Public labels and all four programme options are retained; notes such as “free text” are implemented as control types.', '- Slide 63 instructs copying the existing stress article. Its full saved HTML content is included.', '', 'The quiz destination is not supplied in the deck. The exact quiz CTA currently opens an email request. Contact remains an email draft integration, without a submission backend.']
(ROOT/'CONTENT-AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'Built 8 pages. Verified all 63 slides and {len(audit)} source blocks; website copy matches the deck.')
