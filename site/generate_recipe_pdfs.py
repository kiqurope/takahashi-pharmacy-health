#!/usr/bin/env python3
"""Generate detailed, photo-led A4 PDF recipes for GitHub Pages.
Read source-checked details separately from the web article; never change the
existing DM-oriented PDFs in content/assets.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from PIL import Image as PILImage

ROOT=Path(__file__).resolve().parents[1]
FONT="HeiseiKakuGo-W5"
pdfmetrics.registerFont(UnicodeCIDFont(FONT))
GREEN=colors.HexColor("#20533B")
PALE=colors.HexColor("#EAF2EC")
LIGHT=colors.HexColor("#F7F9F7")
DARK=colors.HexColor("#263C31")
MUTED=colors.HexColor("#62756A")
ST={
"brand":ParagraphStyle("brand",fontName=FONT,fontSize=9,leading=12,textColor=GREEN),
"title":ParagraphStyle("title",fontName=FONT,fontSize=19,leading=25,textColor=DARK,spaceAfter=8),
"sub":ParagraphStyle("sub",fontName=FONT,fontSize=9.4,leading=15,textColor=DARK),
"section":ParagraphStyle("section",fontName=FONT,fontSize=12.7,leading=18.5,textColor=GREEN,spaceBefore=15,spaceAfter=7),
"small":ParagraphStyle("small",fontName=FONT,fontSize=8.6,leading=13.6,textColor=DARK),
"ingredient":ParagraphStyle("ingredient",fontName=FONT,fontSize=9.0,leading=14.2,textColor=DARK),
"step":ParagraphStyle("step",fontName=FONT,fontSize=9.7,leading=16.4,textColor=DARK,leftIndent=19,firstLineIndent=-17,spaceAfter=5),
"note":ParagraphStyle("note",fontName=FONT,fontSize=9.2,leading=15.3,textColor=DARK),
"meta":ParagraphStyle("meta",fontName=FONT,fontSize=7.6,leading=11,textColor=MUTED)
}
def p(text,sty):
    return Paragraph(escape(str(text)).replace("\n","<br/>"),ST[sty])
def page_header(canvas,doc):
    w,h=A4
    canvas.setFillColor(GREEN);canvas.rect(0,h-10,w,10,fill=1,stroke=0)
    canvas.setStrokeColor(colors.HexColor("#D8E5DB"));canvas.line(42,32,w-42,32)
    canvas.setFont(FONT,7.4);canvas.setFillColor(MUTED)
    canvas.drawString(42,22,"タカハシ薬局  |  薬膳料理レシピ  |  詳しい作り方")
    canvas.drawRightString(w-42,22,str(doc.page))
def photo(path):
    if not path.is_file():return None
    with PILImage.open(path) as im:iw,ih=im.size
    factor=min(231.0/iw,143.0/ih)
    return Image(str(path),width=iw*factor,height=ih*factor)
def make(r,detail,assets,out):
    target=out/r["pdf"];target.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(target),pagesize=A4,rightMargin=42,leftMargin=42,
      topMargin=35,bottomMargin=46,title=r["title"]+" | 詳しい作り方",author="タカハシ薬局",pageCompression=1)
    width=A4[0]-84
    items=[p("薬膳料理レシピ  /  "+r.get("issue",""),"brand"),Spacer(1,5),p(r["title"],"title")]
    im=photo(assets/r.get("image",""))
    left=[im] if im else [p("料理写真は公開ページをご覧ください。","meta")]
    right=[p(r.get("description",""),"sub"),Spacer(1,8),
           p("季節："+r.get("season","")+"　　目安："+r.get("servings",""),"small")]
    intro=Table([[left,right]],colWidths=[245,width-245],hAlign="LEFT")
    intro.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
      ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(0,0),14),
      ("RIGHTPADDING",(1,0),(1,0),0),("TOPPADDING",(0,0),(-1,-1),3),
      ("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    items.extend([intro,p("材料（"+r.get("servings","")+"）","section")])
    cells=[p(f"{name}　{qty}","ingredient") for name,qty in r.get("ingredients",[])]
    if len(cells)%2:cells.append("")
    rows=[[cells[i],cells[i+1]] for i in range(0,len(cells),2)]
    tab=Table(rows,colWidths=[width/2,width/2],hAlign="LEFT")
    tab.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),LIGHT),
      ("LINEBELOW",(0,0),(-1,-2),0.35,colors.HexColor("#DFE7E1")),
      ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
      ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
      ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    items.extend([tab,p("詳しい作り方","section")])
    for sec in detail.get("sections",[]):
        if len(detail.get("sections",[]))>1 or sec.get("heading")!="作り方":
            items.append(p(sec.get("heading","作り方"),"small"));items.append(Spacer(1,6))
        for i,step in enumerate(sec.get("steps",[]),1):
            items.append(p(f"{i}.  {step}","step"))
        items.append(Spacer(1,3))
    tip=detail.get("tip") or r.get("tip","")
    if tip:
        items.append(p("おいしく作るワンポイント","section"))
        box=Table([[p(tip,"note")]],colWidths=[width])
        box.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PALE),
          ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#C9DBCE")),
          ("LEFTPADDING",(0,0),(-1,-1),11),("RIGHTPADDING",(0,0),(-1,-1),11),
          ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10)]))
        items.append(box)
    if r.get("food_note"):
        items.extend([p("食材の豆知識","section"),p(r["food_note"],"note")])
    if r.get("safety_note") and r["id"]=="shijimi-shoyu-zuke-200606":
        items.extend([Spacer(1,7),p("安全上の注意：古い原資料の加熱方法を改訂しました。二枚貝は十分加熱してお召し上がりください。","small")])
    items.extend([Spacer(1,18),HRFlowable(width="100%",thickness=.6,color=colors.HexColor("#CBD9CD")),
       Spacer(1,6),p("参考："+detail.get("source",r.get("source_note","")),"meta"),
       p("※一般向け料理紹介です。食材の効能による病気の予防・治療を保証するものではありません。","meta")])
    doc.build(items,onFirstPage=page_header,onLaterPages=page_header)
    return target
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    root=args.root
    recipes=json.loads((root/"content"/"recipes.json").read_text(encoding="utf-8"))
    details=json.loads((root/"content"/"recipe_details.json").read_text(encoding="utf-8"))
    assets=root/"content"/"assets"
    output=args.out or root/"docs"/"assets"
    for r in recipes:
        if r["id"] not in details:continue
        target=make(r,details[r["id"]],assets,output)
        print("PDF generated:",r["title"],target)
if __name__=="__main__":main()
