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
    mobile=''.join(f'<a href="{E(h)}"><span>{emoji}</span>{E(t)}</a>' for (t,h,k),emoji in zip(nav,['🏠','❤️','🥣','🌿']))
    return f'''<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="{'#175c96' if section=='products' else ('#b83b45' if section=='health' else '#1b4d37')}"><meta name="description" content="{E(desc or title)}"><title>{E(title)} | タカハシ薬局</title><link rel="stylesheet" href="{E(root)}assets/style.css"></head>
<body class="{'site-products' if section=='products' else ('site-health' if section=='health' else '')}"><div class="ribbon">{'タカハシ薬局のおすすめ商品をスマホでいつでも' if section=='products' else 'タカハシ薬局の健康情報をスマホでいつでも'}</div><header><div class="wrap head"><a class="brand" href="{E(root)}index.html"><em>✚</em> タカハシ薬局</a><nav aria-label="メインメニュー">{tags}</nav></div></header>
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
    body=hero('❤️ 健康だより · '+a['issue'], a['title'], a.get('subtitle',''))+f'''<main class="wrap article"><section class="card"><span class="issue">{E(a['issue'])}</span><p>{E(a['intro'])}</p><h2 class="article-sub">毎日の健康習慣</h2><div class="cols3">{habits}</div><h2 class="article-sub">意識して摂りたい栄養素</h2><div class="cols3">{nutrients}</div><h2 class="article-sub">身近な旬の食材</h2><div class="foods">{food}</div><div class="info" style="margin-top:24px"><strong>今月のまとめ</strong><p>{E(a['conclusion'])}</p></div><h2 class="article-sub">参考資料</h2><ul class="source-list">{sources}</ul><p class="muted small">※健康に関する一般的な情報です。症状については医療機関等にご相談ください。</p><div class="cta"><a class="btn" href="./">← 健康情報一覧へ</a><button class="btn light" onclick="window.print()">記事を印刷する</button></div></section></main>'''
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
        pic=f'<img class="recipe-card-img" src="../assets/{E(latest["image"])}" alt="{E(latest["title"])}">' if not is_h else '<div style="font-size:65px">❤️</div>'
        featured=f'''<section class="card"><div class="grid"><div>{pic}</div><div><span class="issue">{E(latest["issue"])}</span><h2 style="margin-top:12px">{E(latest["title"])}</h2><p>{E(latest.get('intro',latest.get('description','')))}</p><div class="cta"><a class="btn" href="{E(latest['id'])}.html">記事を読む →</a></div></div></div></section>'''
    else: featured='<section class="card">掲載準備中です。</section>'
    lis=''.join(f'<a data-search="{E(x["issue"]+" "+x["title"]+" "+x.get("description",x.get("intro","")))}" href="{E(x["id"])}.html"><span class="small">{E(x["issue"])}</span><strong>{E(x["title"])}</strong><span class="small">詳しく見る →</span></a>' for x in data)
    body=hero('タカハシ薬局 お客様向け',name,'季節の健康情報を、いつでもスマートフォンから。' if is_h else '旬の料理や作り方を、スマートフォンで気軽に。')+f'''<main class="wrap"><section><p class="sectionlabel">LATEST</p><h2>最新{E(name)}</h2>{featured}</section><section><p class="sectionlabel">ARCHIVE</p><h2>{E(archive_title)}</h2><label for="search" class="small muted">記事タイトルや発行月で検索</label><input id="search" class="search" data-filter type="search" placeholder="例：冬、12月、キムチ" autocomplete="off"><div class="article-list">{lis}</div></section></main>'''
    return layout(name,kind,body,root='../')


def product_photo(p, variant='detail'):
    image_url = p.get('image_url', '')
    credit = p.get('image_credit', '')
    photo_class = 'p-image p-image-' + variant
    if image_url.startswith('https://'):
        priority = 'loading="eager" fetchpriority="high"' if variant == 'featured' else 'loading="lazy"'
        return f'<figure class="{photo_class}"><img src="{E(image_url)}" alt="{E(p["title"])}の商品パッケージ" {priority} decoding="async"><figcaption>{E(credit)}</figcaption></figure>'
    if p.get('image'):
        priority = 'loading="eager" fetchpriority="high"' if variant == 'featured' else 'loading="lazy"'
        return f'<figure class="{photo_class}"><img src="../assets/{E(p["image"])}" alt="{E(credit or p["title"])}" {priority} decoding="async"><figcaption>{E(credit)}</figcaption></figure>'
    return f'<div class="{photo_class} p-image-fallback" role="img" aria-label="{E(p["title"])}"><span aria-hidden="true">✦</span><strong>{E(p["title"])}</strong></div>'


def product_listing(data):
    latest = data[0] if data else None
    if latest:
        newest = f'''<article class="p-feature-card">
          <div class="p-feature-photo">{product_photo(latest, 'featured')}</div>
          <div class="p-feature-copy">
            <span class="p-pill p-pill-blue">{E(latest["issue"])}・最新の掲載商品</span>
            <p class="p-overline">{E(latest.get("maker", ""))} ／ {E(latest.get("category", ""))}</p>
            <h2>{E(latest["title"])}</h2>
            <p class="p-catch">{E(latest.get("description", ""))}</p>
            <p class="p-feature-summary">{E(latest.get("summary", ""))}</p>
            <a class="p-primary-link" href="{E(latest['id'])}.html">商品の特徴や使い方を見る <span aria-hidden="true">↗</span></a>
          </div>
        </article>'''
        intro_link = f'<a class="p-hero-link" href="#latest">最新のおすすめを見る <span aria-hidden="true">↓</span></a>'
        intro_month = f'<span class="p-pill p-pill-white">最新号：{E(latest["issue"])}</span>'
    else:
        newest = '<div class="p-feature-empty">次回のおすすめ商品を準備しています。掲載内容が決まり次第こちらに追加します。</div>'
        intro_link = '<a class="p-hero-link" href="#archive">掲載履歴を見る ↓</a>'
        intro_month = ''

    cards = []
    for item in data:
        group = 'nippo' if '日邦薬品工業' in item.get('group', '') else 'other'
        keywords = ' '.join(str(item.get(k, '')) for k in ('issue','title','description','summary','maker','group','category'))
        latest_flag = '<span class="p-current-label">最新号</span>' if latest and item['id'] == latest['id'] else ''
        cards.append(f'''<a class="p-archive-card" data-product-card data-search="{E(keywords)}" data-group="{E(group)}" href="{E(item['id'])}.html" aria-label="{E(item['issue'])} {E(item['title'])}の商品紹介を読む">
            <div class="p-archive-media">{product_photo(item, 'thumb')}</div>
            <div class="p-archive-copy">
              <span class="p-archive-date">{E(item['issue'])} {latest_flag}</span>
              <h3>{E(item['title'])}</h3>
              <p class="p-archive-category">{E(item.get('category',''))}</p>
              <p class="p-archive-excerpt">{E(item.get('description',''))}</p>
              <span class="p-archive-arrow">この商品を見る <span aria-hidden="true">↗</span></span>
            </div>
        </a>''')
    card_html = ''.join(cards) if data else '<p class="p-no-items">バックナンバーは商品公開後に掲載します。</p>'
    archive = f'''<div class="p-archive-toolbar">
        <div class="p-filters" role="group" aria-label="メーカー分類で絞り込む">
          <button type="button" data-product-group="all" aria-pressed="true">すべて</button>
          <button type="button" data-product-group="nippo" aria-pressed="false">日邦薬品工業</button>
          <button type="button" data-product-group="other" aria-pressed="false">その他の取扱商品</button>
        </div>
        <label class="p-search-label" for="product-search">商品名や掲載月から探す</label>
        <input id="product-search" class="p-search" type="search" placeholder="例：若甦・10月・健康補助食品" autocomplete="off" aria-controls="product-archive-grid">
        <p class="p-results" id="product-result-count" role="status" aria-live="polite">{len(data)}件の商品</p>
      </div>
      <div class="p-archive-grid" id="product-archive-grid">{card_html}</div>
      <p class="p-no-results" id="product-no-results" hidden>該当する商品はありません。キーワードや絞り込みを変えてみてください。</p>'''

    top = f'''<section class="p-site-hero">
       <div class="wrap p-site-hero-inner">
         <div class="p-hero-text"><p class="p-eyebrow">TAKAHASHI PHARMACY <span>MONTHLY PICK</span></p>
            <h1>毎日の健やかさに、<br><span>ちょうどいい一品を。</span></h1>
            <p>タカハシ薬局が、季節に合わせておすすめする商品を月替わりでご紹介します。気になる商品は、特徴や使い方をご確認いただけます。</p>
            <div class="p-hero-actions">{intro_link}<a class="p-hero-ghost" href="#archive">バックナンバーを探す ↓</a></div>
         </div>
         <div class="p-hero-art" aria-hidden="true"><div class="p-hero-circle"><span>今月の</span><strong>おすすめ</strong><small>TAKAHASHI PHARMACY</small></div><span class="p-hero-tile p-hero-tile-a">✦</span><span class="p-hero-tile p-hero-tile-b">＋</span></div>
       </div>
       <div class="wrap p-hero-issue">{intro_month}</div>
    </section>'''

    body = top + f'''<main class="wrap p-products-home" id="main-content">
      <section class="p-section" id="latest" aria-labelledby="p-latest-title">
        <div class="p-section-heading"><div><p class="p-section-kicker">FEATURED PRODUCT</p><h2 id="p-latest-title">最新のおすすめ商品</h2></div><span class="p-subtle-label">毎月更新</span></div>
        {newest}
      </section>
      <section class="p-section" id="archive" aria-labelledby="p-archive-title">
        <div class="p-section-heading"><div><p class="p-section-kicker">BACK NUMBERS</p><h2 id="p-archive-title">これまでのおすすめ</h2></div><span class="p-subtle-label">掲載履歴</span></div>
        <p class="p-section-intro">過去の商品もいつでも見返せます。商品名やメーカー分類から探してみてください。</p>
        {archive}
      </section>
      <section class="p-contact" aria-labelledby="p-consult-title">
         <span class="p-contact-icon" aria-hidden="true">✚</span>
         <div><p class="p-section-kicker">ASK YOUR PHARMACIST</p><h2 id="p-consult-title">商品について、気軽にご相談ください</h2>
         <p>使い方や選び方、販売価格・在庫状況については、タカハシ薬局のスタッフがご案内します。</p>
         <p class="p-contact-hours">営業時間 9:00〜19:00　／　定休日 日曜日・祝日</p></div>
      </section>
      <p class="p-disclaimer">※掲載内容は商品の一般的なご案内です。</p>
    </main>
    <script src="../assets/products.js" defer></script>'''
    return layout('今月のおすすめ商品','products',body,'タカハシ薬局の今月のおすすめ商品とバックナンバー。商品ごとの特徴や使い方、注意事項をご紹介します。',root='../')


def product_detail(p):
    cards = ''.join(f'''<article class="p-point"><span class="p-point-number">0{i+1}</span><h3>{E(x["title"])}</h3><p>{E(x["body"])}</p></article>''' for i,x in enumerate(p.get('highlights',[])))
    people = ''.join(f'<li>{E(x)}</li>' for x in p.get('recommend',[]))
    is_medicine = '医薬品' in p.get('category','')
    usage_title = '用法・用量' if is_medicine else '召し上がり方'
    source = f'<a href="{E(p["source_url"])}" target="_blank" rel="noopener noreferrer">メーカー公式の商品ページを確認する <span aria-hidden="true">↗</span></a>' if p.get('source_url','').startswith('https://') else ''
    others = [x for x in products if x['id'] != p['id']]
    recommendations = ''.join(f'''<a class="p-related-card" href="{E(x['id'])}.html">
       {product_photo(x, 'tiny')}<span><small>{E(x['issue'])}</small><strong>{E(x['title'])}</strong><em>商品ページへ ↗</em></span>
       </a>''' for x in others[:3])
    medical_note = '<strong>第3類医薬品について</strong><p>用法・用量を守り、服用前に添付文書をよくお読みください。不明な点や体調に関するご相談は薬局スタッフへお尋ねください。</p>' if is_medicine else '<strong>健康補助食品について</strong><p>普段の食事を基本とし、食品として取り入れる商品です。疾病の治療・予防を目的とするものではありません。</p>'
    body = f'''<main class="wrap p-product-main" id="main-content">
      <nav aria-label="パンくずリスト" class="p-breadcrumb"><a href="../index.html">ホーム</a><span aria-hidden="true">›</span><a href="./">今月のおすすめ商品</a><span aria-hidden="true">›</span><span aria-current="page">{E(p['title'])}</span></nav>
      <article>
        <section class="p-detail-top" aria-labelledby="p-product-name">
          <div class="p-detail-image">{product_photo(p, 'detail')}</div>
          <div class="p-detail-summary">
            <div class="p-detail-badges"><span class="p-pill p-pill-blue">{E(p['issue'])}</span><span class="p-pill p-pill-outline">{E(p.get('category',''))}</span></div>
            <p class="p-overline">{E(p.get('maker',''))}</p>
            <h1 id="p-product-name">{E(p['title'])}</h1>
            <p class="p-catch">{E(p.get('description',''))}</p>
            <p class="p-detail-intro">{E(p.get('summary',''))}</p>
            <div class="p-detail-actions"><a class="p-primary-link" href="#features">商品の特徴をチェック ↓</a><a class="p-secondary-link" href="#contact">店舗でのご相談について ↓</a></div>
          </div>
        </section>
        <nav class="p-jump" aria-label="このページの目次"><span>このページでわかること</span><a href="#features">特長</a><a href="#recommended">こんな方に</a><a href="#usage">使い方</a><a href="#caution">注意事項</a></nav>
        <section class="p-detail-section" id="features" aria-labelledby="p-features-title"><div class="p-detail-section-heading"><p class="p-section-kicker">FEATURES</p><h2 id="p-features-title">この商品の3つの特長</h2><p>商品について、知っておきたいポイントをまとめました。</p></div><div class="p-points">{cards}</div></section>
        <section class="p-detail-section" id="recommended" aria-labelledby="p-recommend-title"><div class="p-detail-section-heading"><p class="p-section-kicker">FOR YOU</p><h2 id="p-recommend-title">こんな方におすすめ</h2></div><div class="p-recommend-panel"><ul class="p-recommend-list">{people}</ul><p class="p-recommend-note">当てはまる方も、体調や生活習慣に合わせてお選びください。</p></div></section>
        <section class="p-detail-section" id="usage" aria-labelledby="p-usage-title"><div class="p-detail-section-heading"><p class="p-section-kicker">HOW TO USE</p><h2 id="p-usage-title">{E(usage_title)}</h2></div><div class="p-usage-panel"><span class="p-usage-icon" aria-hidden="true">01</span><p>{E(p.get('usage',''))}</p></div></section>
        <section class="p-detail-section" id="caution" aria-labelledby="p-caution-title"><div class="p-detail-section-heading"><p class="p-section-kicker">IMPORTANT</p><h2 id="p-caution-title">ご使用前にご確認ください</h2></div><div class="p-care-panel" role="note"><div>{medical_note}</div><p>{E(p.get('caution',''))}</p></div></section>
        <section class="p-detail-section" id="contact" aria-labelledby="p-contact-title">
           <div class="p-contact p-contact-detail"><span class="p-contact-icon" aria-hidden="true">✚</span><div><p class="p-section-kicker">ASK YOUR PHARMACIST</p><h2 id="p-contact-title">迷ったら、タカハシ薬局へ</h2><p>ご自身に合うか、価格・在庫、使い方などお気軽にご相談ください。</p><p class="p-contact-hours">営業時間 9:00〜19:00　／　定休日 日曜日・祝日</p></div></div>
           <div class="p-official"><h3>メーカー公式情報</h3><p>詳しい商品情報・使用上の注意は、メーカー公式ページおよび実際の商品・添付文書でご確認ください。</p>{source}</div>
        </section>
        <section class="p-related" aria-labelledby="p-related-title"><div class="p-section-heading"><div><p class="p-section-kicker">OTHER ISSUES</p><h2 id="p-related-title">ほかの月のおすすめ</h2></div></div><div class="p-related-grid">{recommendations}</div><a class="p-backlink" href="./#archive">← すべてのバックナンバーを見る</a></section>
      </article>
    </main>'''
    return layout(p['title']+'｜'+p['issue'],'products',body,p.get('description',''),root='../')


def front():
    cards=[]
    for kind,data,emoji,title in [('health',articles,'❤️','健康情報'),('recipes',recipes,'🥣','薬膳レシピ'),('products',products,'🌿','今月のおすすめ')]:
        item=data[0] if data else {}
        excerpt=item.get('subtitle',item.get('description','掲載準備中'))
        cards.append(f'<article class="card feature"><div class="label">{emoji}</div><div><span class="issue">{E(item.get("issue","準備中"))}</span><h2>{title}</h2><p>{E(item.get("title",""))}</p><p class="small">{E(excerpt)}</p></div><a class="btn" href="{kind}/">{title}を開く →</a></article>')
    body=hero('タカハシ薬局 公式LINE', '毎日の健康を、もっと身近に。','季節の健康情報・薬膳レシピ・おすすめ商品をご案内します。')+f'''<main class="wrap"><section><p class="sectionlabel">LINE MENU</p><h2>読みたい情報を選んでください</h2><div class="grid">{''.join(cards)}</div></section><section class="info"><h3>新しい記事について</h3><p>健康情報・薬膳レシピ・おすすめ商品を順次追加します。過去の記事や商品のご案内も各一覧から確認できます。</p></section></main>'''
    return layout('健康情報・薬膳レシピ・おすすめ商品','home',body,root='./')


def line_guide(kind):
    prescription = kind == 'prescription'
    title = '処方せん送信' if prescription else 'お問い合わせ'
    label = 'LINEで処方せんを送る' if prescription else 'LINEで相談する'
    color = '#226b46' if prescription else '#175c96'
    intro = 'ご来局前に、紙の処方せんの写真をLINEでお送りいただけます。' if prescription else 'お薬や健康について、お気軽にご相談ください。'
    steps = (
        '<li>紙の処方せん全体が読めるよう、明るい場所で撮影してください。複数枚ある場合はすべて撮影してください。</li>'
        '<li>下のボタンから当薬局のLINEトークを開き、写真を添付して送信してください。</li>'
        '<li>薬局からの返信をご確認ください。お薬の準備には時間がかかる場合があります。</li>'
        if prescription else
        '<li>下のボタンから当薬局のLINEトークを開いてください。</li>'
        '<li>ご相談・ご質問の内容を入力し、送信ボタンを押してください。</li>'
        '<li>営業時間内に薬局スタッフが順次個別に返信します。</li>'
    )
    notice = (
        '<h2>処方せんのご注意</h2><p>紙の処方せんは、必ず原本を薬局へお持ちください。</p><p>使用期間は特に指定がない場合、交付日を含めて4日以内（休日・祝日も含む）です。</p><p>期限が迫っている場合やお急ぎの場合は、LINEの返信を待たず薬局に直接ご確認ください。<a href="https://www.mhlw.go.jp/stf/newpage_32041.html" rel="noreferrer">厚生労働省：処方箋の使用期間</a></p>'
        if prescription else
        '<h2>ご相談の前に</h2><p>LINEは緊急対応の窓口ではありません。急な重い症状など、緊急の場合は119番等にご相談ください。相談に不要な個人情報は送らないようお願いします。</p>'
    )
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><meta name="robots" content="noindex"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'"><title>{title} | タカハシ薬局</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f7f5;color:#20352e;font:16px/1.8 system-ui,sans-serif;overflow-wrap:anywhere}}header{{background:{color};color:white;padding:16px;text-align:center;font-weight:700}}main{{max-width:640px;margin:auto;padding:18px 16px 32px}}section{{background:white;border:1px solid #dbe5df;border-radius:16px;padding:20px;margin:14px 0}}h1{{font-size:29px;line-height:1.4;margin:8px 0;color:{color}}}h2{{font-size:19px;line-height:1.5;margin:0 0 8px}}p{{margin:8px 0}}ol{{padding-left:1.5em;margin:10px 0}}li{{padding:4px 0}}.hours{{font-weight:700}}.button{{display:block;background:#087c3e;color:white;text-align:center;text-decoration:none;font-weight:700;border-radius:12px;padding:16px;margin:18px 0 8px;font-size:18px}}a:focus-visible{{outline:3px solid #c47c00;outline-offset:4px}}.note{{font-size:14px;color:#43534b}}.caution{{border-left:5px solid #b57620}}footer{{text-align:center;font-size:13px;color:#52645a;padding:8px 16px 24px}}
</style></head><body><header>🍀 タカハシ薬局</header><main><h1>{title}</h1><p>{intro}</p><section><h2>ご利用方法</h2><ol>{steps}</ol><a class="button" href="https://line.me/R/oaMessage/%40299qyrsf" rel="noreferrer">{label} →</a><p class="note">ボタンを押すだけでは送信されません。LINEトークで送信操作をしてください。</p></section><section><h2>営業時間・返信について</h2><p class="hours">営業時間 9:00〜19:00<br>定休日：日曜日・祝日</p><p>営業時間外・定休日に届いたメッセージは翌営業日以降に対応します。</p></section><section class="caution">{notice}</section><section><h2>個人情報について</h2><p class="note">この案内ページには入力・写真アップロード機能はありません。相談や写真の送信は、タカハシ薬局のLINE公式アカウントのトーク画面で行ってください。</p></section></main><footer>タカハシ薬局</footer></body></html>'''


def store_guide():
    return '''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><meta name="robots" content="noindex"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'"><title>店舗案内 | タカハシ薬局</title><style>
*{box-sizing:border-box}body{margin:0;background:#f3f7f5;color:#20352e;font:16px/1.8 system-ui,sans-serif;overflow-wrap:anywhere}header{background:#226b46;color:white;padding:16px;text-align:center;font-weight:700}main{max-width:640px;margin:auto;padding:18px 16px 32px}section{background:white;border:1px solid #dbe5df;border-radius:16px;padding:20px;margin:14px 0}h1{font-size:29px;line-height:1.4;margin:8px 0;color:#226b46}h2{font-size:19px;line-height:1.5;margin:0 0 8px}p{margin:8px 0}.button{display:block;background:#226b46;color:white;text-align:center;text-decoration:none;font-weight:700;border-radius:12px;padding:16px;margin:16px 0 4px;font-size:18px}.phone{background:#175c96}a:focus-visible{outline:3px solid #c47c00;outline-offset:4px}.note{font-size:14px;color:#43534b}footer{text-align:center;font-size:13px;color:#52645a;padding:8px 16px 24px}
</style></head><body><header>🍀 タカハシ薬局</header><main><h1>店舗案内</h1><section><h2>所在地・アクセス</h2><p>〒210-0802<br>神奈川県川崎市川崎区大師駅前1-6-7</p><p>京急大師線「川崎大師駅」近く</p><a class="button" href="https://www.google.com/maps/search/?api=1&amp;query=%E3%82%BF%E3%82%AB%E3%83%8F%E3%82%B7%E8%96%AC%E5%B1%80%20%E5%B7%9D%E5%B4%8E%E5%B8%82%E5%B7%9D%E5%B4%8E%E5%8C%BA%E5%A4%A7%E5%B8%AB%E9%A7%85%E5%89%8D1-6-7" rel="noreferrer">Googleマップで見る →</a></section><section><h2>営業時間・定休日</h2><p><strong>月〜土 9:00〜19:00</strong><br>定休日：日曜日・祝日</p><p class="note">年末年始等は臨時休業の場合があります。</p></section><section><h2>電話番号</h2><p><strong>044-266-3994</strong></p><a class="button phone" href="tel:0442663994">電話をかける</a></section><section><p>皆さまのご来局をお待ちしております。</p></section></main><footer>タカハシ薬局</footer></body></html>'''

def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(data,encoding='utf-8')

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'.nojekyll').write_text('',encoding='utf-8')
    (OUT/'assets').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'site'/'style.css',OUT/'assets'/'style.css')
    shutil.copy2(ROOT/'site'/'products.js',OUT/'assets'/'products.js')
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
    save(OUT/'store'/'index.html',store_guide())
    save(OUT/'contact'/'index.html',line_guide('contact'))
    save(OUT/'prescription'/'index.html',line_guide('prescription'))
    print(f'Success: {SITE_DATE} JST; health={len(articles)}, recipes={len(recipes)}, products={len(products)}; output={OUT}')
