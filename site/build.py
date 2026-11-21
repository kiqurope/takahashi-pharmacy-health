#!/usr/bin/env python3
"""Free static website builder; no external API, hosting fee, or pip dependencies."""
from __future__ import annotations
import json, html, shutil, os
from pathlib import Path
from datetime import datetime, date
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content'
OUT=ROOT/'docs'
JST=datetime.now(ZoneInfo('Asia/Tokyo')).date()
SITE_DATE=date.fromisoformat(os.getenv('SITE_DATE',JST.isoformat()))
E=lambda x:html.escape(str(x),quote=True)

def read(name):
    data=json.loads((CONTENT/name).read_text(encoding='utf-8'))
    assert isinstance(data,list), f'{name} must be JSON list'
    for item in data:
        assert item.get('id') and item.get('title') and item.get('publish_on'),name
    assert len({x['id'] for x in data})==len(data),f'duplicate ID in {name}'
    return sorted([x for x in data if date.fromisoformat(x['publish_on'])<=SITE_DATE], key=lambda x:x['date'], reverse=True)

articles=read('articles.json')
recipes=read('recipes.json')
products=read('products.json')


def layout(title,section,body,desc='',root='../'):
    nav=[('ホーム',root+'index.html','home'),('健康情報',root+'health/','health'),('薬膳レシピ',root+'recipes/','recipes'),('おすすめ商品',root+'products/','products')]
    tags=''.join(f'<a href="{E(h)}" {"aria-current=page" if k==section else ""}>{E(t)}</a>' for t,h,k in nav)
    mobile=''.join(f'<a href="{E(h)}"><span>{emoji}</span>{E(t)}</a>' for (t,h,k),emoji in zip(nav,['🏠','💚','🥣','🌿']))
    return f'''<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#1b4d37"><meta name="description" content="{E(desc or title)}"><title>{E(title)} | タカハシ薬局</title><link rel="stylesheet" href="{E(root)}assets/style.css"></head>
<body><div class="ribbon">タカハシ薬局の健康情報をスマホでいつでも</div><header><div class="wrap head"><a class="brand" href="{E(root)}index.html"><em>✚</em> タカハシ薬局</a><nav aria-label="メインメニュー">{tags}</nav></div></header>
{body}
<footer class="footer"><div class="wrap">タカハシ薬局｜健康情報・薬膳レシピ・おすすめ商品<br>このサイトは一般的な健康情報の提供を目的としています。診断・治療に代わるものではありません。</div></footer><div class="mobilebar" aria-label="スマホメニュー">{mobile}</div>
<script>document.querySelectorAll('[data-filter]').forEach(input=>input.addEventListener('input',()=>{{const q=input.value.trim().toLowerCase();document.querySelectorAll('[data-search]').forEach(card=>{{card.hidden=!card.dataset.search.toLowerCase().includes(q)}})}}));</script>
</body></html>'''

def hero(tag,title,sub):
    return f'<section class="hero"><div class="wrap"><span class="tag">{E(tag)}</span><h1>{E(title)}</h1><p class="lead">{E(sub)}</p></div></section>'

def health_detail(a):
    habits=''.join(f'<div class="mini"><div class="emblem">{["🫧","🌬️","🌙"][i%3]}</div><h3>{E(x["title"])}</h3><p class="muted small">{E(x["description"])}</p></div>' for i,x in enumerate(a['habits']))
    nutrients=''.join(f'<div class="mini"><div class="emblem">{E(x.get("symbol","🍀"))}</div><h3>{E(x["name"])}</h3><p class="small">{E(x["summary"])}</p><p class="small muted"><b>食品例：</b>{E(x["foods"])}</p></div>' for x in a['nutrients'])
    food=''.join(f'<span class="food">{E(x.get("emoji","🍴"))} {E(x["name"])} · {E(x.get("note",""))}</span>' for x in a['seasonal'])
    sources=''.join(f'<li><a href="{E(x["url"])}" target="_blank" rel="noopener noreferrer">{E(x["label"])}</a></li>' for x in a['sources'] if x.get('url','').startswith('https://'))
    body=hero('🌿 健康だより · '+a['issue'], a['title'], a.get('subtitle',''))+f'''<main class="wrap article"><section class="card"><span class="issue">{E(a['issue'])}</span><p>{E(a['intro'])}</p><h2 class="article-sub">毎日の健康習慣</h2><div class="cols3">{habits}</div><h2 class="article-sub">意識して摂りたい栄養素</h2><div class="cols3">{nutrients}</div><h2 class="article-sub">身近な旬の食材</h2><div class="foods">{food}</div><div class="info" style="margin-top:24px"><strong>今月のまとめ</strong><p>{E(a['conclusion'])}</p></div><h2 class="article-sub">参考資料</h2><ul class="source-list">{sources}</ul><p class="muted small">※健康に関する一般的な情報です。症状については医療機関等にご相談ください。</p><div class="cta"><a class="btn" href="./">← 健康情報一覧へ</a><button class="btn light" onclick="window.print()">記事を印刷する</button></div></section></main>'''
    return layout(a['title'],'health',body,a['intro'],root='../')

def recipe_detail(r):
    ingredients=''.join(f'<li><label><input type="checkbox" aria-label="{E(n)}をチェック"><span>{E(n)}</span></label><strong>{E(v)}</strong></li>' for n,v in r['ingredients'])
    steps=''.join(f'<li>{E(t)}</li>' for t in r['steps'])
    photo=f'<img class="recipe-photo" src="../assets/{E(r["image"])}" alt="{E(r.get("image_alt",r["title"]+"の料理イメージ"))}">' if r.get('image') else ''
    if r.get('pdf'):
        download=f'<a class="btn" href="../assets/{E(r["pdf"])}" download>📄 印刷用PDFを保存</a><a class="btn light" href="../assets/{E(r["pdf"])}" target="_blank">A4レシピを見る</a>'
    else:
        download='<button class="btn" onclick="window.print()">🖨️ 印刷・PDFで保存</button>'
    safety=f'<div class="info orange safety" role="note" style="margin-top:16px"><h3>食品衛生上のご注意</h3><p>{E(r["safety_note"])}</p></div>' if r.get('safety_note') else ''
    body=hero('🥣 薬膳レシピ · '+r['issue'],r['title'],r['description'])+f'''<main class="wrap"><section class="card"><span class="issue">{E(r['issue'])}｜{E(r['season'])}</span><div class="recipe-layout" style="margin-top:18px"><div>{photo}<div class="cta">{download}</div></div><div><h2>材料（{E(r['servings'])}）</h2><p class="muted small">材料をタップするとお買い物チェックができます。</p><ul class="ingredients">{ingredients}</ul></div></div><h2 class="article-sub">作り方</h2><ol class="steps">{steps}</ol>{safety}<div class="info orange" style="margin-top:12px"><h3>おいしく作るワンポイント</h3><p>{E(r['tip'])}</p></div><div class="info" style="margin-top:12px"><h3>食材の豆知識</h3><p>{E(r['food_note'])}</p></div><p class="muted small" style="margin-top:15px">参考：{E(r['source_note'])}</p><div class="cta"><a class="btn" href="./">← レシピ一覧へ</a></div></section></main>'''
    return layout(r['title'],'recipes',body,r['description'],root='../')

def listing(kind,data):
    is_h=kind=='health'
    name='健康情報' if is_h else '薬膳レシピ'
    archive_title='過去の健康情報' if is_h else f'過去の{name}も探せます'
    latest=data[0] if data else None
    if latest:
        pic=f'<img class="recipe-card-img" src="../assets/{E(latest["image"])}" alt="{E(latest["title"])}">' if not is_h else '<div style="font-size:65px">💚</div>'
        featured=f'''<section class="card"><div class="grid"><div>{pic}</div><div><span class="issue">{E(latest["issue"])}</span><h2 style="margin-top:12px">{E(latest["title"])}</h2><p>{E(latest.get('intro',latest.get('description','')))}</p><div class="cta"><a class="btn" href="{E(latest['id'])}.html">記事を読む →</a></div></div></div></section>'''
    else: featured='<section class="card">掲載準備中です。</section>'
    lis=''.join(f'<a data-search="{E(x["issue"]+" "+x["title"]+" "+x.get("description",x.get("intro","")))}" href="{E(x["id"])}.html"><span class="small">{E(x["issue"])}</span><strong>{E(x["title"])}</strong><span class="small">詳しく見る →</span></a>' for x in data)
    body=hero('タカハシ薬局 お客様向け',name,'季節の健康情報を、いつでもスマートフォンから。' if is_h else '旬の料理や作り方を、スマートフォンで気軽に。')+f'''<main class="wrap"><section><p class="sectionlabel">LATEST</p><h2>最新{E(name)}</h2>{featured}</section><section><p class="sectionlabel">ARCHIVE</p><h2>{E(archive_title)}</h2><label for="search" class="small muted">記事タイトルや発行月で検索</label><input id="search" class="search" data-filter type="search" placeholder="例：冬、12月、キムチ" autocomplete="off"><div class="article-list">{lis}</div></section></main>'''
    return layout(name,kind,body,root='../')


def product_photo(p):
    url=p.get('image_url','')
    credit=p.get('image_credit','')
    if url.startswith('https://'):
        return f'<figure class="product-photo"><img src="{E(url)}" alt="{E(p["title"])}のメーカー公式商品写真" loading="lazy"><figcaption>{E(credit)}</figcaption></figure>'
    return f'<div class="product-photo product-photo-empty" role="img" aria-label="{E(p["title"])}"><span>🌿</span><strong>{E(p["title"])}</strong></div>'

def product_listing(data):
    latest=data[0] if data else None
    if latest:
        featured=f'''<section class="card product-feature"><div>{product_photo(latest)}</div><div><span class="issue">{E(latest["issue"])} · 最新号</span><p class="product-group">{E(latest.get("group",""))} ／ {E(latest.get("category",""))}</p><h2>{E(latest["title"])}</h2><p class="product-lead">{E(latest.get("description",""))}</p><p>{E(latest.get("summary",""))}</p><span class="stock">✓ タカハシ薬局で取扱あり</span><div class="cta"><a class="btn" href="{E(latest["id"])}.html">商品について詳しく見る →</a></div></div></section>'''
    else:
        featured='<section class="card"><h2>商品紹介ページを準備しています</h2><p>おすすめ商品を確認し、順次ご案内いたします。</p></section>'
    items=''.join(f'''<a data-search="{E(p["issue"]+" "+p["title"]+" "+p.get("description",""))}" href="{E(p["id"])}.html"><span class="small">{E(p["issue"])} · {E(p.get("category",""))}</span><strong>{E(p["title"])}</strong><span class="small">{E(p.get("description",""))}</span><span class="small product-arrow">商品ページを開く →</span></a>''' for p in data)
    archive=f'<label for="product-search" class="small muted">商品名や掲載月で検索できます</label><input id="product-search" data-filter class="search" type="search" placeholder="例：若甦、プログリーン、10月" autocomplete="off"><div class="article-list">{items}</div><p class="muted small">これまでにご紹介した商品は、今後もこの一覧からご覧いただけます。</p>' if data else '<p class="muted">バックナンバーは掲載後にこちらへ追加されます。</p>'
    body=hero('🌿 タカハシ薬局 · LINEリッチメニュー','今月のおすすめ商品','毎月ひとつ、季節や暮らしに合わせた取扱商品をご紹介します。')+f'''<main class="wrap products-page"><section><p class="sectionlabel">THIS MONTH</p><h2>最新のおすすめ</h2>{featured}</section><section id="archive"><p class="sectionlabel">BACK NUMBER</p><h2>バックナンバー</h2>{archive}</section><section class="info product-consult"><h3>ご購入・商品に関するご相談</h3><p>掲載商品はタカハシ薬局で取り扱っています。在庫・販売価格や、ご自身に合うかどうかについては薬局スタッフにお尋ねください。</p><p class="small">営業時間 9:00〜19:00 ／ 定休日 日曜日・祝日</p></section></main>'''
    return layout('今月のおすすめ商品','products',body,root='../')

def product_detail(p):
    highlights=''.join(f'<div class="mini"><h3>{E(x["title"])}</h3><p>{E(x["body"])}</p></div>' for x in p.get('highlights',[]))
    people=''.join(f'<li>{E(x)}</li>' for x in p.get('recommend',[]))
    sources=f'<a href="{E(p["source_url"])}" target="_blank" rel="noopener noreferrer">{E(p["source_name"])} ↗</a>' if p.get('source_url','').startswith('https://') else ''
    theme='product-green' if 'progreen' in p['id'] else 'product-red'
    body=hero('🌿 今月のおすすめ · '+p['issue'],p['title'],p.get('description',''))+f'''<main class="wrap product-detail {theme}"><section class="card"><span class="issue">{E(p["issue"])}</span> <span class="stock">✓ タカハシ薬局で取扱あり</span><div class="product-overview"><div>{product_photo(p)}</div><div><p class="product-group">{E(p.get("maker",""))} ｜ {E(p.get("category",""))}</p><h2>{E(p["title"])}</h2><p class="product-lead">{E(p.get("description",""))}</p><p>{E(p.get("summary",""))}</p><div class="info product-price"><strong>価格・在庫について</strong><p>販売価格や在庫状況は店頭でご確認ください。</p></div></div></div><h2 class="article-sub">この商品の特長</h2><div class="product-highlights">{highlights}</div><h2 class="article-sub">こんな方に</h2><ul class="product-people">{people}</ul><h2 class="article-sub">{'服用方法' if p.get('category')=='第3類医薬品' else '召し上がり方'}</h2><p>{E(p.get("usage",""))}</p><div class="info orange safety" role="note"><h3>ご使用・ご利用上の注意</h3><p>{E(p.get("caution",""))}</p></div><h2 class="article-sub">メーカー公式情報</h2><p>{sources}</p><p class="muted small">※商品の詳細はメーカー公式情報や実際のパッケージ・添付文書をご確認ください。商品の説明は医療機関での診断や治療に代わるものではありません。</p><div class="cta"><a class="btn" href="./">← 今月のおすすめ一覧・バックナンバーへ</a></div></section></main>'''
    return layout(p['title']+'｜'+p['issue'],'products',body,p.get('description',''),root='../')

def front():
    cards=[]
    for kind,data,emoji,title in [('health',articles,'💚','健康情報'),('recipes',recipes,'🥣','薬膳レシピ'),('products',products,'🌿','今月のおすすめ')]:
        item=data[0] if data else {}
        excerpt=item.get('subtitle',item.get('description','掲載準備中'))
        cards.append(f'<article class="card feature"><div class="label">{emoji}</div><div><span class="issue">{E(item.get("issue","準備中"))}</span><h2>{title}</h2><p>{E(item.get("title",""))}</p><p class="small">{E(excerpt)}</p></div><a class="btn" href="{kind}/">{title}を開く →</a></article>')
    body=hero('タカハシ薬局 公式LINE', '毎日の健康を、もっと身近に。','季節の健康情報・薬膳レシピ・おすすめ商品をご案内します。')+f'''<main class="wrap"><section><p class="sectionlabel">LINE MENU</p><h2>読みたい情報を選んでください</h2><div class="grid">{''.join(cards)}</div></section><section class="info"><h3>新しい記事について</h3><p>健康情報・薬膳レシピ・おすすめ商品を順次追加します。過去の記事や商品のご案内も各一覧から確認できます。</p></section></main>'''
    return layout('健康情報・薬膳レシピ・おすすめ商品','home',body,root='./')

def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(data,encoding='utf-8')

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'.nojekyll').write_text('',encoding='utf-8')
    (OUT/'assets').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'site'/'style.css',OUT/'assets'/'style.css')
    for r in recipes:
        for key in ('image','pdf'):
            if not r.get(key): continue
            src=CONTENT/'assets'/r[key]
            assert src.is_file(),f'missing file: {src}'
            shutil.copy2(src,OUT/'assets'/src.name)
    for p in products:
        if p.get('image'):
            src=CONTENT/'assets'/p['image']
            assert src.is_file(),f'missing file: {src}'
            shutil.copy2(src,OUT/'assets'/src.name)
    # Replace only published print PDFs with the detailed A4 editions.
    # Original DM-format PDFs remain untouched under content/assets.
    import subprocess, sys
    subprocess.check_call([sys.executable,str(ROOT/'site'/'generate_recipe_pdfs.py')])
    save(OUT/'index.html',front())
    save(OUT/'health'/'index.html',listing('health',articles))
    save(OUT/'recipes'/'index.html',listing('recipes',recipes))
    save(OUT/'products'/'index.html',product_listing(products))
    for a in articles:
        destination=OUT/'health'/f'{a["id"]}.html'
        if a.get('archive_static'):
            # Previously published, hand-edited backnumbers remain intact.
            assert destination.is_file(), f'missing archived health page: {destination}'
            continue
        save(destination,health_detail(a))
    for r in recipes:save(OUT/'recipes'/f'{r["id"]}.html',recipe_detail(r))
    for p in products:save(OUT/'products'/f'{p["id"]}.html',product_detail(p))
    print(f'Success: {SITE_DATE} JST; health={len(articles)}, recipes={len(recipes)}, products={len(products)}; output={OUT}')
