import os

PIXEL = '''<!-- Facebook Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window,document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
 fbq('init', '1509252477674429'); 
fbq('track', 'PageView');
</script>
<noscript>
 <img height="1" width="1" 
src="https://www.facebook.com/tr?id=1509252477674429&ev=PageView
&noscript=1"/>
</noscript>
<!-- End Facebook Pixel Code -->
</head>'''

PUB = '/app/frontend/public'
pages = ['index.html', 'home/index.html', 'why/index.html', 'programs/index.html', 'outcomes/index.html', 'apply/index.html']
for p in pages:
    fp = f'{PUB}/{p}'
    html = open(fp, encoding='utf-8').read()
    if 'fbevents.js' in html:
        print('skip (already present):', p)
        continue
    html = html.replace('</head>', PIXEL, 1)
    open(fp, 'w', encoding='utf-8').write(html)
    print('added:', p)
